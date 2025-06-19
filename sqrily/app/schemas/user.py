"""
User management schemas for the Sqrly ADHD Planner.

This module contains Pydantic models for user profile management,
ADHD preferences, and user-related API requests/responses.
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserUpdate(BaseModel):
    """User profile update request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class ADHDProfileUpdate(BaseModel):
    """ADHD profile update request"""
    # Core ADHD characteristics
    overwhelm_threshold: Optional[int] = None  # 1-10 scale
    hyperfocus_tendency: Optional[int] = None  # 1-10 scale
    attention_span_minutes: Optional[int] = None
    preferred_task_size: Optional[str] = None  # micro, small, medium, large
    
    # Energy and focus patterns
    peak_focus_hours: Optional[List[Dict[str, str]]] = None  # [{"start": "09:00", "end": "11:00"}]
    energy_tracking_enabled: Optional[bool] = None
    break_reminders: Optional[bool] = None
    
    # AI collaboration preferences
    ai_communication_style: Optional[str] = None  # directive, collaborative, supportive
    feedback_sensitivity: Optional[int] = None  # 1-10 scale
    
    # Environment and triggers
    optimal_environment: Optional[Dict[str, str]] = None
    distraction_triggers: Optional[List[str]] = None
    overwhelm_notifications: Optional[bool] = None
    
    # Medication and routine
    medication_schedule: Optional[Dict[str, Any]] = None
    routine_preferences: Optional[Dict[str, Any]] = None
    
    @field_validator('overwhelm_threshold', 'hyperfocus_tendency', 'feedback_sensitivity')
    @classmethod
    def validate_scale_fields(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Scale values must be between 1 and 10')
        return v
    
    @field_validator('attention_span_minutes')
    @classmethod
    def validate_attention_span(cls, v):
        if v is not None and (v < 5 or v > 180):
            raise ValueError('Attention span must be between 5 and 180 minutes')
        return v
    
    @field_validator('preferred_task_size')
    @classmethod
    def validate_task_size(cls, v):
        if v is not None and v not in ['micro', 'small', 'medium', 'large']:
            raise ValueError('Task size must be one of: micro, small, medium, large')
        return v
    
    @field_validator('ai_communication_style')
    @classmethod
    def validate_communication_style(cls, v):
        if v is not None and v not in ['directive', 'collaborative', 'supportive']:
            raise ValueError('Communication style must be one of: directive, collaborative, supportive')
        return v

class UserPreferences(BaseModel):
    """User preferences for app behavior"""
    theme: Optional[str] = "light"  # light, dark, auto
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True
    push_notifications: Optional[bool] = True
    
    # ADHD-specific preferences
    gentle_reminders: Optional[bool] = True
    overwhelm_protection: Optional[bool] = True
    focus_mode_enabled: Optional[bool] = True
    
    # Privacy preferences
    data_sharing_analytics: Optional[bool] = False
    data_sharing_research: Optional[bool] = False

class OnboardingStep(BaseModel):
    """Onboarding step completion"""
    step: str
    data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

class UserStats(BaseModel):
    """User statistics and metrics"""
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    current_streak: int
    longest_streak: int
    average_energy_level: float
    total_focus_time_minutes: int
    
    # ADHD-specific metrics
    overwhelm_incidents: int
    successful_focus_sessions: int
    task_breakdown_usage: int

class UserProfileResponse(BaseModel):
    """Complete user profile response"""
    id: str
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    provider: str
    timezone: str
    
    # Account status
    is_active: bool
    is_verified: bool
    subscription_tier: str
    onboarding_completed: bool
    
    # ADHD profile
    adhd_profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    # Statistics
    stats: Optional[UserStats] = None
    
    # Timestamps
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListItem(BaseModel):
    """User item for admin list views"""
    id: str
    email: str
    first_name: str
    last_name: str
    provider: str
    subscription_tier: str
    onboarding_completed: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserSearchFilters(BaseModel):
    """Filters for user search (admin only)"""
    email: Optional[str] = None
    provider: Optional[str] = None
    subscription_tier: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class EmailChangeRequest(BaseModel):
    """Email change request"""
    new_email: EmailStr
    password: str  # Require password confirmation

class AccountDeactivationRequest(BaseModel):
    """Account deactivation request"""
    password: str
    reason: Optional[str] = None
    feedback: Optional[str] = None
