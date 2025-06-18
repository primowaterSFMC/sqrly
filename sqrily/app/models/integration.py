from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class IntegrationProvider(str, enum.Enum):
    GOOGLE_CALENDAR = "google_calendar"
    APPLE_CALENDAR = "apple_calendar"
    MICROSOFT_OUTLOOK = "microsoft_outlook"
    SPOTIFY = "spotify"
    NOTION = "notion"
    TODOIST = "todoist"
    SLACK = "slack"

class IntegrationStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"

class SyncDirection(str, enum.Enum):
    IMPORT_ONLY = "import_only"
    EXPORT_ONLY = "export_only"
    BIDIRECTIONAL = "bidirectional"

class Integration(Base, DatabaseMixin):
    __tablename__ = "integrations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Integration details
    provider = Column(String(50), nullable=False)
    status = Column(String(20), default=IntegrationStatus.PENDING)
    
    # OAuth and authentication
    access_token = Column(Text, nullable=True)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)  # Encrypted in production
    token_expires_at = Column(DateTime, nullable=True)
    
    # Provider-specific data
    provider_user_id = Column(String(255), nullable=True)
    provider_account_info = Column(JSON, nullable=True)
    
    # Integration settings
    sync_direction = Column(String(20), default=SyncDirection.BIDIRECTIONAL)
    sync_frequency = Column(String(20), default="real_time")  # real_time, hourly, daily
    
    # ADHD optimizations
    adhd_optimizations_enabled = Column(Boolean, default=True)
    buffer_time_minutes = Column(Integer, default=15)
    gentle_reminders = Column(Boolean, default=True)
    focus_protection_enabled = Column(Boolean, default=True)
    
    # Privacy settings
    share_task_details = Column(Boolean, default=False)
    use_generic_titles = Column(Boolean, default=True)
    sync_personal_events = Column(Boolean, default=False)
    
    # Sync statistics
    last_sync_at = Column(DateTime, nullable=True)
    total_syncs = Column(Integer, default=0)
    sync_errors = Column(Integer, default=0)
    items_synced = Column(Integer, default=0)
    
    # Features enabled
    features_enabled = Column(JSON, nullable=True)  # List of enabled features
    
    # Error tracking
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    connected_at = Column(DateTime, nullable=True)
    disconnected_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    sync_logs = relationship("SyncLog", back_populates="integration", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, provider={self.provider}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if integration is active"""
        return self.status == IntegrationStatus.ACTIVE
    
    @property
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at
    
    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refreshing"""
        if not self.token_expires_at:
            return False
        # Refresh if token expires within 10 minutes
        return (self.token_expires_at - datetime.utcnow()).total_seconds() < 600
    
    def activate(self):
        """Activate the integration"""
        self.status = IntegrationStatus.ACTIVE
        self.connected_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def disconnect(self, reason: str = None):
        """Disconnect the integration"""
        self.status = IntegrationStatus.DISCONNECTED
        self.disconnected_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if reason:
            self.last_error = f"Disconnected: {reason}"
            self.last_error_at = datetime.utcnow()
    
    def record_sync_success(self, items_count: int = 0):
        """Record successful sync"""
        self.last_sync_at = datetime.utcnow()
        self.total_syncs += 1
        self.items_synced += items_count
        self.updated_at = datetime.utcnow()
        
        # Clear error status if it was in error state
        if self.status == IntegrationStatus.ERROR:
            self.status = IntegrationStatus.ACTIVE
    
    def record_sync_error(self, error_message: str):
        """Record sync error"""
        self.sync_errors += 1
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
        self.status = IntegrationStatus.ERROR
        self.updated_at = datetime.utcnow()
    
    def get_health_score(self) -> float:
        """Calculate integration health score (0-1)"""
        if self.total_syncs == 0:
            return 1.0  # New integration, assume healthy
        
        error_rate = self.sync_errors / self.total_syncs
        base_score = 1.0 - error_rate
        
        # Adjust for recent activity
        if self.last_sync_at:
            hours_since_sync = (datetime.utcnow() - self.last_sync_at).total_seconds() / 3600
            if hours_since_sync > 24:
                base_score *= 0.8  # Reduce score if no recent sync
        
        return max(0.0, min(1.0, base_score))
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled"""
        if not self.features_enabled:
            return False
        return feature in self.features_enabled
    
    def enable_feature(self, feature: str):
        """Enable a specific feature"""
        if self.features_enabled is None:
            self.features_enabled = []
        
        if feature not in self.features_enabled:
            self.features_enabled.append(feature)
            self.updated_at = datetime.utcnow()
    
    def disable_feature(self, feature: str):
        """Disable a specific feature"""
        if self.features_enabled and feature in self.features_enabled:
            self.features_enabled.remove(feature)
            self.updated_at = datetime.utcnow()

class SyncLog(Base, DatabaseMixin):
    """Log entries for integration sync operations"""
    __tablename__ = "sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(50), nullable=False)  # import, export, bidirectional
    status = Column(String(20), nullable=False)     # success, error, partial
    
    # Results
    items_processed = Column(Integer, default=0)
    items_created = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    items_deleted = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    # Timing
    duration_seconds = Column(Integer, nullable=True)
    
    # Error details
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Metadata
    sync_metadata = Column(JSON, nullable=True)  # Provider-specific sync data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = relationship("Integration", back_populates="sync_logs")
    
    def __repr__(self):
        return f"<SyncLog(id={self.id}, integration_id={self.integration_id}, status={self.status})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate for this sync"""
        total_items = self.items_processed
        if total_items == 0:
            return 1.0
        
        successful_items = total_items - self.items_failed
        return successful_items / total_items