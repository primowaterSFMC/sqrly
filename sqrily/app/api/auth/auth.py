from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import structlog
import httpx
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
import secrets
import uuid

from ...database import get_db
from ...dependencies import create_access_token, create_refresh_token, verify_token, get_current_user
from ...models import User, AuthProvider
from ...config import settings
from ...schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    GoogleCallbackResponse, AppleCallbackRequest, RefreshTokenRequest
)

logger = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth setup
oauth = OAuth()

# Google OAuth
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name='google',
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()

def create_user_response(user: User, access_token: str, refresh_token: str) -> dict:
    """Create standardized user response with tokens"""
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
            "provider": user.provider.value,
            "onboarding_completed": user.onboarding_completed,
            "subscription_tier": user.subscription_tier.value,
            "adhd_profile": user.adhd_profile,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with ADHD profile setup"""
    
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        timezone=user_data.timezone,
        provider=AuthProvider.EMAIL,
        adhd_profile=user_data.adhd_profile.dict() if user_data.adhd_profile else None
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("User registered successfully", user_id=str(user.id), email=user.email)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Determine onboarding steps
    onboarding_steps = []
    if not user.adhd_profile:
        onboarding_steps.append("adhd_assessment")
    onboarding_steps.extend(["task_preferences", "ai_collaboration_setup"])
    
    response = create_user_response(user, access_token, refresh_token)
    response.update({
        "user_id": str(user.id),
        "onboarding_steps": onboarding_steps
    })
    
    return response

@router.post("/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Email/password authentication"""
    
    user = get_user_by_email(db, user_data.email)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
    
    # Create tokens with extended expiry if remember_me is True
    expires_delta = None
    if user_data.remember_me:
        expires_delta = timedelta(days=30)
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=expires_delta
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return create_user_response(user, access_token, refresh_token)

@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth flow"""
    if not oauth.google:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    redirect_uri = str(request.url_for('google_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Google OAuth callback handler"""
    if not oauth.google:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    # Verify state for CSRF protection
    state = request.query_params.get('state')
    if not state or state != request.session.get('oauth_state'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token['userinfo']
        
        email = user_info['email']
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        avatar_url = user_info.get('picture')
        provider_id = user_info['sub']
        
        # Check if user exists
        user = get_user_by_email(db, email)
        is_new_user = False
        
        if not user:
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url,
                provider=AuthProvider.GOOGLE,
                provider_id=provider_id,
                is_verified=True  # Google emails are pre-verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
            
            logger.info("New user created via Google OAuth", user_id=str(user.id), email=email)
        else:
            # Update existing user if needed
            if user.provider != AuthProvider.GOOGLE:
                user.provider = AuthProvider.GOOGLE
                user.provider_id = provider_id
                user.is_verified = True
            
            user.last_login_at = datetime.utcnow()
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            
            db.commit()
            
            logger.info("Existing user logged in via Google OAuth", user_id=str(user.id), email=email)
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        response = create_user_response(user, access_token, refresh_token)
        response.update({
            "is_new_user": is_new_user,
            "onboarding_required": not user.onboarding_completed
        })
        
        return response
        
    except Exception as e:
        logger.error("Google OAuth callback error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth authentication failed"
        )

@router.post("/apple/callback")
async def apple_callback(
    id_token: str = Form(...),
    code: str = Form(...),
    state: str = Form(...),
    user: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Apple Sign In callback handler"""
    # TODO: Implement Apple Sign In verification
    # This requires validating the JWT token from Apple
    # and extracting user information
    
    try:
        # For now, return a placeholder response
        # In production, implement proper Apple JWT verification
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Apple Sign In not yet implemented"
        )
        
    except Exception as e:
        logger.error("Apple Sign In callback error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apple Sign In authentication failed"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: RefreshTokenRequest, 
    db: Session = Depends(get_db)
):
    """Refresh JWT access tokens"""
    
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active or user.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
        
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout():
    """Logout user (client should delete tokens)"""
    # Since we're using stateless JWT tokens, 
    # logout is handled on the client side
    # In production, consider implementing token blacklisting
    
    return {
        "message": "Successfully logged out",
        "adhd_friendly_message": "You're all logged out! Take care of yourself. 💙"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    logger.info("Getting current user info", user_id=str(current_user.id))

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        avatar_url=current_user.avatar_url,
        provider=current_user.provider.value,
        onboarding_completed=current_user.onboarding_completed,
        subscription_tier=current_user.subscription_tier.value,
        adhd_preferences=current_user.adhd_profile,
        created_at=current_user.created_at
    )