from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class SubtaskType(str, enum.Enum):
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"
    MICRO = "micro"  # For executive dysfunction support

class SubtaskDifficulty(str, enum.Enum):
    EASY = "easy"      # Low cognitive load, simple action
    MEDIUM = "medium"  # Moderate effort required
    HARD = "hard"      # High cognitive load or complex

class SubtaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Subtask(Base, DatabaseMixin):
    __tablename__ = "subtasks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    action = Column(Text, nullable=True)  # Specific action to take
    completion_criteria = Column(Text, nullable=True)  # How to know it's done
    
    # Sequencing and dependencies
    sequence_order = Column(Integer, default=1)  # Order within the parent task
    depends_on_subtask_ids = Column(JSON, nullable=True)  # List of prerequisite subtask IDs
    
    # Classification
    subtask_type = Column(String(20), default=SubtaskType.EXECUTION)
    difficulty_level = Column(String(20), default=SubtaskDifficulty.MEDIUM)
    status = Column(String(20), default=SubtaskStatus.PENDING)
    
    # Time estimates
    estimated_minutes = Column(Integer, default=15)
    actual_minutes = Column(Integer, nullable=True)
    
    # ADHD-specific support
    energy_required = Column(Integer, default=5)     # 1-10 scale
    focus_required = Column(Integer, default=5)      # 1-10 scale
    initiation_support = Column(Text, nullable=True) # Specific guidance to start
    success_indicators = Column(JSON, nullable=True) # Signs of completion
    dopamine_reward = Column(Text, nullable=True)    # Reward/celebration suggestion
    
    # Executive function support
    preparation_steps = Column(JSON, nullable=True)  # What to do before starting
    materials_needed = Column(JSON, nullable=True)   # Required tools/resources
    
    # AI assistance
    ai_generated = Column(Boolean, default=False)    # Whether AI created this subtask
    ai_confidence = Column(Float, nullable=True)     # AI confidence in breakdown
    
    # Progress and motivation
    momentum_builder = Column(Boolean, default=False) # Designed to build momentum
    confidence_boost = Column(Boolean, default=False) # Designed to boost confidence
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="subtasks")
    
    def __repr__(self):
        return f"<Subtask(id={self.id}, title={self.title}, status={self.status})>"
    
    @property
    def is_blocked(self) -> bool:
        """Check if subtask is blocked by incomplete dependencies"""
        if not self.depends_on_subtask_ids:
            return False
        
        # TODO: Query dependent subtasks to check completion
        # For now, assume not blocked
        return False
    
    @property
    def cognitive_load_score(self) -> float:
        """Calculate cognitive load based on difficulty, energy, and focus requirements"""
        difficulty_weights = {
            SubtaskDifficulty.EASY: 1.0,
            SubtaskDifficulty.MEDIUM: 2.0,
            SubtaskDifficulty.HARD: 3.0
        }
        
        base_load = difficulty_weights.get(self.difficulty_level, 2.0)
        energy_factor = self.energy_required / 10.0
        focus_factor = self.focus_required / 10.0
        
        return base_load * (1 + energy_factor + focus_factor) / 3
    
    def can_start(self) -> bool:
        """Check if subtask can be started (dependencies met)"""
        if self.status != SubtaskStatus.PENDING:
            return False
        
        return not self.is_blocked
    
    def start_subtask(self):
        """Mark subtask as started"""
        if self.can_start():
            self.status = SubtaskStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    def complete_subtask(self, actual_minutes: int = None):
        """Mark subtask as completed"""
        self.status = SubtaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if actual_minutes:
            self.actual_minutes = actual_minutes
    
    def skip_subtask(self, reason: str = None):
        """Mark subtask as skipped"""
        self.status = SubtaskStatus.SKIPPED
        self.updated_at = datetime.utcnow()
        # TODO: Store skip reason if needed
    
    def get_next_action(self) -> str:
        """Get the next specific action to take"""
        if self.initiation_support:
            return self.initiation_support
        elif self.action:
            return self.action
        else:
            return f"Work on: {self.title}"
    
    def is_momentum_appropriate(self, user_energy: int, user_confidence: int) -> bool:
        """Check if this subtask is appropriate for building momentum"""
        if not self.momentum_builder:
            return True
        
        # Momentum builders should be used when energy/confidence is low
        return user_energy <= 5 or user_confidence <= 5
    
    def get_completion_signal(self) -> str:
        """Get clear signal that subtask is complete"""
        if self.completion_criteria:
            return self.completion_criteria
        elif self.success_indicators:
            return " and ".join(self.success_indicators)
        else:
            return f"You have completed: {self.title}"

class MicroTask(Base, DatabaseMixin):
    """Ultra-small tasks for severe executive dysfunction support"""
    __tablename__ = "micro_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subtask_id = Column(UUID(as_uuid=True), ForeignKey("subtasks.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Micro task details
    action = Column(String(255), nullable=False)  # Very specific action
    duration_minutes = Column(Integer, default=2) # 1-5 minutes max
    
    # Materials and completion
    materials_needed = Column(JSON, nullable=True)
    completion_signal = Column(String(255), nullable=False)
    motivation_note = Column(Text, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Support features
    confidence_boost = Column(Boolean, default=True)
    momentum_builder = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subtask = relationship("Subtask")
    task = relationship("Task")
    
    def __repr__(self):
        return f"<MicroTask(id={self.id}, action={self.action})>"
    
    def complete(self):
        """Mark micro task as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()