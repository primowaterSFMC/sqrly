from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, JSON, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class User(Base, DatabaseMixin):
    __tablename__ = "users"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    provider = Column(Enum(AuthProvider), default=AuthProvider.EMAIL)
    provider_id = Column(String(255), nullable=True)
    
    # Basic profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    
    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(String(50), nullable=True)
    
    # Privacy settings
    privacy_focused = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # ADHD Profile - stored as JSON for flexibility
    adhd_profile = Column(JSON, nullable=True)
    
    # Relationships
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    ai_sessions = relationship("AISession", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_adhd_preference(self, key: str, default=None):
        """Get ADHD profile preference by key"""
        if self.adhd_profile:
            return self.adhd_profile.get(key, default)
        return default
    
    def update_adhd_profile(self, updates: dict):
        """Update ADHD profile with new values"""
        if self.adhd_profile is None:
            self.adhd_profile = {}
        
        self.adhd_profile.update(updates)
        self.updated_at = datetime.utcnow()
    
    def get_overwhelm_threshold(self) -> int:
        """Get user's overwhelm threshold (1-10 scale)"""
        return self.get_adhd_preference("overwhelm_threshold", 6)
    
    def get_attention_span_minutes(self) -> int:
        """Get user's typical attention span in minutes"""
        return self.get_adhd_preference("attention_span_minutes", 25)
    
    def get_preferred_task_size(self) -> str:
        """Get user's preferred task size (micro, small, medium, large)"""
        return self.get_adhd_preference("preferred_task_size", "medium")
    
    def get_ai_communication_style(self) -> str:
        """Get user's preferred AI communication style"""
        return self.get_adhd_preference("ai_communication_style", "collaborative")
    
    def is_peak_focus_time(self, hour: int) -> bool:
        """Check if given hour is within user's peak focus time"""
        peak_hours = self.get_adhd_preference("peak_focus_hours", [])
        for period in peak_hours:
            start_hour = int(period.get("start", "09:00").split(":")[0])
            end_hour = int(period.get("end", "11:00").split(":")[0])
            if start_hour <= hour <= end_hour:
                return True
        return False