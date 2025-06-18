from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class TaskComplexity(str, enum.Enum):
    MICRO = "micro"      # 2-5 minutes
    SIMPLE = "simple"    # 5-15 minutes
    MEDIUM = "medium"    # 15-45 minutes
    COMPLEX = "complex"  # 45+ minutes

class TaskType(str, enum.Enum):
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    LEARNING = "learning"
    ADMIN = "admin"
    CREATIVE = "creative"

class Task(Base, DatabaseMixin):
    __tablename__ = "tasks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=True)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    natural_language_input = Column(Text, nullable=True)  # Original user input for AI processing
    
    # Sqrily classification
    fc_quadrant = Column(Integer, nullable=True)  # 1-4
    importance_level = Column(Integer, default=5)  # 1-10
    urgency_level = Column(Integer, default=5)    # 1-10
    
    # Task specifics
    status = Column(String(20), default=TaskStatus.PENDING)
    task_type = Column(String(20), default=TaskType.WORK)
    complexity_level = Column(String(20), default=TaskComplexity.MEDIUM)
    
    # Time management
    estimated_duration_minutes = Column(Integer, nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    due_date = Column(DateTime, nullable=True)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    
    # AI analysis
    ai_priority_score = Column(Float, nullable=True)  # AI-calculated priority
    ai_suggestions = Column(JSON, nullable=True)     # AI recommendations
    ai_confidence = Column(Float, nullable=True)     # AI confidence in analysis
    
    # ADHD-specific fields
    executive_difficulty = Column(Integer, default=5)  # 1-10, how hard to start/complete
    initiation_difficulty = Column(Integer, default=5) # 1-10, how hard to begin
    completion_difficulty = Column(Integer, default=5) # 1-10, how hard to finish
    required_energy_level = Column(Integer, default=5) # 1-10, energy needed
    
    # Context and environment
    context_tags = Column(JSON, nullable=True)        # ["computer", "phone", "outdoors"]
    required_materials = Column(JSON, nullable=True)  # List of needed items
    optimal_environment = Column(JSON, nullable=True) # Environment preferences
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    time_blocks = relationship("TimeBlock", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def is_due_soon(self) -> bool:
        """Check if task is due within 24 hours"""
        if self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            hours_until_due = (self.due_date - datetime.utcnow()).total_seconds() / 3600
            return 0 < hours_until_due <= 24
        return False
    
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
    
    def calculate_priority_score(self) -> float:
        """Calculate dynamic priority score based on multiple factors"""
        base_score = (self.importance_level + self.urgency_level) / 2
        
        # Adjust for due date
        if self.due_date:
            hours_until_due = (self.due_date - datetime.utcnow()).total_seconds() / 3600
            if hours_until_due < 24:
                base_score += 2  # Boost for urgent deadlines
            elif hours_until_due < 168:  # One week
                base_score += 1
        
        # Adjust for complexity (simpler tasks get slight boost for momentum)
        complexity_adjustments = {
            TaskComplexity.MICRO: 0.5,
            TaskComplexity.SIMPLE: 0.2,
            TaskComplexity.MEDIUM: 0,
            TaskComplexity.COMPLEX: -0.5
        }
        base_score += complexity_adjustments.get(self.complexity_level, 0)
        
        # Adjust for executive function difficulty (easier to start gets boost)
        if self.initiation_difficulty <= 3:
            base_score += 0.5
        elif self.initiation_difficulty >= 8:
            base_score -= 0.5
        
        return max(1.0, min(10.0, base_score))
    
    def start_task(self):
        """Mark task as started"""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    def complete_task(self, actual_duration: int = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.0
        self.updated_at = datetime.utcnow()
        
        if actual_duration:
            self.actual_duration_minutes = actual_duration
    
    def get_breakdown_recommendation(self) -> bool:
        """Check if task should be broken down into subtasks"""
        if self.complexity_level in [TaskComplexity.COMPLEX]:
            return True
        if self.estimated_duration_minutes and self.estimated_duration_minutes > 45:
            return True
        if self.executive_difficulty >= 7:
            return True
        return False
    
    def get_ai_suggestion(self, key: str, default=None):
        """Get AI suggestion by key"""
        if self.ai_suggestions:
            return self.ai_suggestions.get(key, default)
        return default
    
    def add_ai_suggestion(self, key: str, value):
        """Add AI suggestion"""
        if self.ai_suggestions is None:
            self.ai_suggestions = {}
        
        self.ai_suggestions[key] = value
        self.updated_at = datetime.utcnow()

class TimeBlock(Base, DatabaseMixin):
    """Time blocks for calendar integration"""
    __tablename__ = "time_blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Time block details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    title = Column(String(255), nullable=False)
    
    # Block type and settings
    block_type = Column(String(50), default="focused_work")  # focused_work, communication, admin, etc.
    buffer_before = Column(Integer, default=0)  # Buffer time in minutes
    buffer_after = Column(Integer, default=0)
    
    # ADHD optimizations
    energy_match_score = Column(Float, nullable=True)  # How well this matches user's energy
    distraction_risk = Column(String(20), default="medium")  # low, medium, high
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="time_blocks")
    user = relationship("User")
    
    def __repr__(self):
        return f"<TimeBlock(id={self.id}, task_id={self.task_id}, start={self.start_time})>"