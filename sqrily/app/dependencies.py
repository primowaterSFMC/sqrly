from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import structlog

from .database import get_db
from .config import settings
from .models.user import User

logger = structlog.get_logger()
security = HTTPBearer()

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        token_type_claim: str = payload.get("type")
        
        if user_id is None or token_type_claim != token_type:
            raise AuthenticationError()
            
        return payload
    except JWTError as e:
        logger.warning("JWT verification failed", error=str(e))
        raise AuthenticationError()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError()
            
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AuthenticationError("User not found")
            
        if user.deleted_at is not None:
            raise AuthenticationError("User account is deactivated")
            
        return user
        
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise AuthenticationError()

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (not disabled)"""
    if not current_user.is_active:
        raise PermissionError("Inactive user")
    return current_user

def require_onboarding_complete(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require user to have completed onboarding"""
    if not current_user.onboarding_completed:
        raise PermissionError(
            detail="Please complete your onboarding process first",
            headers={"X-Onboarding-Required": "true"}
        )
    return current_user

def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Check rate limit for user and endpoint"""
    # TODO: Implement Redis-based rate limiting
    return True

class RateLimiter:
    """Rate limiting dependency"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def __call__(self, current_user: User = Depends(get_current_active_user)):
        # TODO: Implement rate limiting logic
        return current_user