"""
Task-related Pydantic schemas for request/response validation.

This module contains all the schemas for task operations including
ADHD-specific fields and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from ..models.task import TaskStatus, TaskComplexity, TaskType


class TaskStatusEnum(str, Enum):
    """Task status enumeration for API"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskComplexityEnum(str, Enum):
    """Task complexity enumeration for API"""
    MICRO = "micro"      # 2-5 minutes
    SIMPLE = "simple"    # 5-15 minutes
    MEDIUM = "medium"    # 15-45 minutes
    COMPLEX = "complex"  # 45+ minutes


class TaskTypeEnum(str, Enum):
    """Task type enumeration for API"""
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    LEARNING = "learning"
    ADMIN = "admin"
    CREATIVE = "creative"


class TaskBase(BaseModel):
    """Base task schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    
    # Sqrily classification
    importance_level: int = Field(5, ge=1, le=10, description="Importance level (1-10)")
    urgency_level: int = Field(5, ge=1, le=10, description="Urgency level (1-10)")
    
    # Task specifics
    task_type: TaskTypeEnum = Field(TaskTypeEnum.WORK, description="Type of task")
    complexity_level: TaskComplexityEnum = Field(TaskComplexityEnum.MEDIUM, description="Task complexity")
    
    # Time management
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, le=480, description="Estimated duration in minutes")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    
    # ADHD-specific fields
    executive_difficulty: int = Field(5, ge=1, le=10, description="How hard to start/complete (1-10)")
    initiation_difficulty: int = Field(5, ge=1, le=10, description="How hard to begin (1-10)")
    completion_difficulty: int = Field(5, ge=1, le=10, description="How hard to finish (1-10)")
    required_energy_level: int = Field(5, ge=1, le=10, description="Energy needed (1-10)")
    
    # Context and environment
    context_tags: Optional[List[str]] = Field(None, description="Context tags like 'computer', 'phone', 'outdoors'")
    required_materials: Optional[List[str]] = Field(None, description="List of needed items")
    optimal_environment: Optional[Dict[str, Any]] = Field(None, description="Environment preferences")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean task title"""
        if not v or not v.strip():
            raise ValueError('Task title cannot be empty')
        return v.strip()

    @field_validator('context_tags')
    @classmethod
    def validate_context_tags(cls, v):
        """Validate context tags"""
        if v is not None:
            # Limit number of tags
            if len(v) > 10:
                raise ValueError('Maximum 10 context tags allowed')
            # Clean and validate each tag
            cleaned_tags = []
            for tag in v:
                if isinstance(tag, str) and tag.strip():
                    cleaned_tags.append(tag.strip().lower())
            return cleaned_tags
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    goal_id: Optional[UUID] = Field(None, description="Associated goal ID")
    natural_language_input: Optional[str] = Field(None, max_length=1000, description="Original user input for AI processing")
    
    # Optional scheduling
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end time")

    @field_validator('scheduled_end')
    @classmethod
    def validate_scheduled_times(cls, v, info):
        """Validate that end time is after start time"""
        if v is not None and 'scheduled_start' in info.data:
            scheduled_start = info.data['scheduled_start']
            if scheduled_start is not None and v <= scheduled_start:
                raise ValueError('Scheduled end time must be after start time')
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    
    # Sqrily classification
    importance_level: Optional[int] = Field(None, ge=1, le=10)
    urgency_level: Optional[int] = Field(None, ge=1, le=10)
    
    # Task specifics
    status: Optional[TaskStatusEnum] = None
    task_type: Optional[TaskTypeEnum] = None
    complexity_level: Optional[TaskComplexityEnum] = None
    
    # Time management
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    due_date: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    # ADHD-specific fields
    executive_difficulty: Optional[int] = Field(None, ge=1, le=10)
    initiation_difficulty: Optional[int] = Field(None, ge=1, le=10)
    completion_difficulty: Optional[int] = Field(None, ge=1, le=10)
    required_energy_level: Optional[int] = Field(None, ge=1, le=10)
    
    # Context and environment
    context_tags: Optional[List[str]] = None
    required_materials: Optional[List[str]] = None
    optimal_environment: Optional[Dict[str, Any]] = None
    
    # Progress
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean task title"""
        if v is not None:
            if not v.strip():
                raise ValueError('Task title cannot be empty')
            return v.strip()
        return v


class TaskResponse(TaskBase):
    """Schema for task responses"""
    id: UUID = Field(..., description="Task ID")
    user_id: UUID = Field(..., description="User ID")
    goal_id: Optional[UUID] = Field(None, description="Associated goal ID")
    
    # Status and progress
    status: TaskStatusEnum = Field(..., description="Current task status")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    
    # Sqrily quadrant (calculated)
    fc_quadrant: Optional[int] = Field(None, description="Franklin Covey quadrant (1-4)")
    quadrant_name: Optional[str] = Field(None, description="Human-readable quadrant name")
    
    # AI analysis
    ai_priority_score: Optional[float] = Field(None, description="AI-calculated priority score")
    ai_suggestions: Optional[Dict[str, Any]] = Field(None, description="AI recommendations")
    ai_confidence: Optional[float] = Field(None, description="AI confidence in analysis")
    
    # Time tracking
    actual_duration_minutes: Optional[int] = Field(None, description="Actual time spent")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end time")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="When task was started")
    completed_at: Optional[datetime] = Field(None, description="When task was completed")
    
    # Computed properties
    is_overdue: Optional[bool] = Field(None, description="Whether task is overdue")
    is_due_soon: Optional[bool] = Field(None, description="Whether task is due within 24 hours")
    breakdown_recommended: Optional[bool] = Field(None, description="Whether task should be broken down")

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list responses"""
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class TaskFilters(BaseModel):
    """Schema for task filtering parameters"""
    status: Optional[List[TaskStatusEnum]] = Field(None, description="Filter by status")
    task_type: Optional[List[TaskTypeEnum]] = Field(None, description="Filter by type")
    complexity_level: Optional[List[TaskComplexityEnum]] = Field(None, description="Filter by complexity")
    fc_quadrant: Optional[List[int]] = Field(None, description="Filter by Sqrily quadrant")
    goal_id: Optional[UUID] = Field(None, description="Filter by goal")
    due_before: Optional[datetime] = Field(None, description="Due before this date")
    due_after: Optional[datetime] = Field(None, description="Due after this date")
    context_tags: Optional[List[str]] = Field(None, description="Filter by context tags")
    min_priority: Optional[float] = Field(None, ge=1.0, le=10.0, description="Minimum priority score")
    max_priority: Optional[float] = Field(None, ge=1.0, le=10.0, description="Maximum priority score")


class TaskActionRequest(BaseModel):
    """Schema for task actions like start, complete, etc."""
    action: str = Field(..., description="Action to perform")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    actual_duration_minutes: Optional[int] = Field(None, ge=1, description="Actual duration for completion")


class TaskBreakdownRequest(BaseModel):
    """Schema for requesting AI task breakdown"""
    max_subtasks: int = Field(5, ge=2, le=10, description="Maximum number of subtasks to create")
    target_duration_minutes: int = Field(15, ge=5, le=60, description="Target duration for each subtask")
    include_micro_tasks: bool = Field(False, description="Include micro-tasks for executive dysfunction")
    user_context: Optional[str] = Field(None, max_length=500, description="Additional context for AI")


class TaskBreakdownResponse(BaseModel):
    """Schema for AI task breakdown response"""
    original_task_id: UUID = Field(..., description="Original task ID")
    subtasks: List[Dict[str, Any]] = Field(..., description="Generated subtasks")
    ai_reasoning: str = Field(..., description="AI explanation of the breakdown")
    confidence_score: float = Field(..., description="AI confidence in the breakdown")
    estimated_total_time: int = Field(..., description="Total estimated time for all subtasks")
