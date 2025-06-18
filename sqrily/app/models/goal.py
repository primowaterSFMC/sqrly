from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class SqrilyQuadrant(int, enum.Enum):
    """Sqrily Time Management Matrix Quadrants"""
    URGENT_IMPORTANT = 1      # Crisis, emergencies, deadline-driven projects
    NOT_URGENT_IMPORTANT = 2  # Prevention, planning, values clarification, relationship building
    URGENT_NOT_IMPORTANT = 3  # Interruptions, some mail, some reports, some meetings
    NOT_URGENT_NOT_IMPORTANT = 4  # Trivia, busywork, time wasters, pleasant activities

class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"

class Goal(Base, DatabaseMixin):
    __tablename__ = "goals"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Sqrily integration
    fc_quadrant = Column(Integer, nullable=True)  # 1-4 for Sqrily quadrants
    values_alignment = Column(JSON, nullable=True)  # List of values this goal aligns with
    mission_connection = Column(Text, nullable=True)  # How this connects to personal mission
    role_category = Column(String(100), nullable=True)  # professional, personal, self_care, etc.
    
    # Goal specifics
    target_date = Column(DateTime, nullable=True)
    success_metrics = Column(JSON, nullable=True)  # List of success criteria
    priority_level = Column(Integer, default=5)  # 1-10 scale
    
    # Progress tracking
    status = Column(String(20), default=GoalStatus.ACTIVE)
    progress_percentage = Column(Float, default=0.0)
    
    # AI-generated insights
    ai_breakdown = Column(JSON, nullable=True)  # AI-generated phases and tasks
    ai_insights = Column(JSON, nullable=True)  # AI analysis and recommendations
    ai_confidence = Column(Float, nullable=True)  # AI confidence score
    
    # ADHD-specific
    complexity_assessment = Column(String(20), nullable=True)  # low, medium, high
    estimated_effort_hours = Column(Integer, nullable=True)
    overwhelm_risk = Column(String(20), default="medium")  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="goal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title={self.title}, quadrant={self.fc_quadrant})>"
    
    @property
    def quadrant_name(self) -> str:
        """Get human-readable quadrant name"""
        quadrant_names = {
            1: "Urgent & Important",
            2: "Not Urgent & Important", 
            3: "Urgent & Not Important",
            4: "Not Urgent & Not Important"
        }
        return quadrant_names.get(self.fc_quadrant, "Unassigned")
    
    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue"""
        if self.target_date and self.status == GoalStatus.ACTIVE:
            return datetime.utcnow() > self.target_date
        return False
    
    @property
    def days_until_target(self) -> int:
        """Days until target date (negative if overdue)"""
        if self.target_date:
            delta = self.target_date - datetime.utcnow()
            return delta.days
        return 0
    
    def update_progress(self, percentage: float):
        """Update progress percentage"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        self.updated_at = datetime.utcnow()
        
        if self.progress_percentage >= 100.0 and self.status == GoalStatus.ACTIVE:
            self.status = GoalStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def get_ai_recommendation(self, key: str, default=None):
        """Get AI recommendation by key"""
        if self.ai_insights:
            return self.ai_insights.get(key, default)
        return default
    
    def add_ai_insight(self, key: str, value):
        """Add AI insight"""
        if self.ai_insights is None:
            self.ai_insights = {}
        
        self.ai_insights[key] = value
        self.updated_at = datetime.utcnow()
    
    def calculate_quadrant_score(self, urgency: int, importance: int) -> int:
        """Calculate Sqrily quadrant based on urgency and importance scores"""
        if urgency >= 7 and importance >= 7:
            return 1  # Urgent & Important
        elif urgency < 7 and importance >= 7:
            return 2  # Not Urgent & Important
        elif urgency >= 7 and importance < 7:
            return 3  # Urgent & Not Important
        else:
            return 4  # Not Urgent & Not Important

class Milestone(Base, DatabaseMixin):
    __tablename__ = "milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=False)
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goal = relationship("Goal", back_populates="milestones")
    
    def __repr__(self):
        return f"<Milestone(id={self.id}, title={self.title}, goal_id={self.goal_id})>"