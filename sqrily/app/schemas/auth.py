from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ADHDProfile(BaseModel):
    """ADHD-specific profile settings"""
    executive_strengths: Optional[List[str]] = None
    executive_challenges: Optional[List[str]] = None
    overwhelm_threshold: Optional[int] = 6  # 1-10 scale
    hyperfocus_tendency: Optional[int] = 5  # 1-10 scale
    peak_focus_hours: Optional[List[Dict[str, Any]]] = None
    energy_pattern: Optional[str] = "morning"  # morning, afternoon, evening, variable
    attention_span_minutes: Optional[int] = 25
    break_frequency_minutes: Optional[int] = 5
    preferred_task_size: Optional[str] = "medium"  # micro, small, medium, large
    breakdown_style: Optional[str] = "sequential"  # sequential, parallel, flexible
    completion_motivation: Optional[List[str]] = None  # progress_bars, celebrations, etc.
    ai_communication_style: Optional[str] = "collaborative"  # directive, collaborative, supportive
    feedback_sensitivity: Optional[int] = 5  # 1-10 scale
    optimal_environment: Optional[Dict[str, str]] = None
    distraction_triggers: Optional[List[str]] = None
    
    @field_validator('overwhelm_threshold')
    @classmethod
    def validate_overwhelm_threshold(cls, v):
        if v and (v < 1 or v > 10):
            raise ValueError('Overwhelm threshold must be between 1 and 10')
        return v

    @field_validator('hyperfocus_tendency')
    @classmethod
    def validate_hyperfocus_tendency(cls, v):
        if v and (v < 1 or v > 10):
            raise ValueError('Hyperfocus tendency must be between 1 and 10')
        return v

class DeviceInfo(BaseModel):
    """Device information for login tracking"""
    device_type: str = "web"  # web, mobile, desktop
    user_agent: Optional[str] = None
    timezone: Optional[str] = "UTC"

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    timezone: str = "UTC"
    adhd_profile: Optional[ADHDProfile] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        return v.strip()

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    remember_me: bool = False
    device_info: Optional[DeviceInfo] = None

class UserResponse(BaseModel):
    """User information in responses"""
    id: str
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    provider: str
    onboarding_completed: bool
    subscription_tier: str
    adhd_preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token response for authentication"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class GoogleCallbackResponse(BaseModel):
    """Google OAuth callback response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    is_new_user: bool
    onboarding_required: bool

class AppleUserInfo(BaseModel):
    """Apple Sign In user info"""
    name: Optional[Dict[str, str]] = None
    email: Optional[str] = None

class AppleCallbackRequest(BaseModel):
    """Apple Sign In callback request"""
    id_token: str
    code: str
    state: str
    user: Optional[AppleUserInfo] = None

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v