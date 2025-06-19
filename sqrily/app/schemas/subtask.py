"""
Subtask management schemas for the Sqrly ADHD Planner.

This module contains Pydantic models for subtask CRUD operations,
including ADHD-specific features and AI-generated subtasks.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class SubtaskTypeEnum(str, Enum):
    """Subtask type enumeration for API"""
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"
    MICRO = "micro"


class SubtaskDifficultyEnum(str, Enum):
    """Subtask difficulty enumeration for API"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubtaskStatusEnum(str, Enum):
    """Subtask status enumeration for API"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SubtaskBase(BaseModel):
    """Base subtask schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Subtask title")
    action: Optional[str] = Field(None, max_length=1000, description="Specific action to take")
    completion_criteria: Optional[str] = Field(None, max_length=500, description="How to know it's done")
    
    # Sequencing and dependencies
    sequence_order: int = Field(1, ge=1, description="Order within the parent task")
    depends_on_subtask_ids: Optional[List[UUID]] = Field(None, description="List of prerequisite subtask IDs")
    
    # Classification
    subtask_type: SubtaskTypeEnum = Field(SubtaskTypeEnum.EXECUTION, description="Type of subtask")
    difficulty_level: SubtaskDifficultyEnum = Field(SubtaskDifficultyEnum.MEDIUM, description="Difficulty level")
    
    # Time estimates
    estimated_minutes: int = Field(15, ge=1, le=240, description="Estimated duration in minutes")
    
    # ADHD-specific support
    energy_required: int = Field(5, ge=1, le=10, description="Energy required (1-10)")
    focus_required: int = Field(5, ge=1, le=10, description="Focus required (1-10)")
    initiation_support: Optional[str] = Field(None, max_length=500, description="Specific guidance to start")
    success_indicators: Optional[List[str]] = Field(None, description="Signs of completion")
    dopamine_reward: Optional[str] = Field(None, max_length=200, description="Reward/celebration suggestion")
    
    # Executive function support
    preparation_steps: Optional[List[str]] = Field(None, description="What to do before starting")
    materials_needed: Optional[List[str]] = Field(None, description="Required tools/resources")
    
    # Progress and motivation
    momentum_builder: bool = Field(False, description="Designed to build momentum")
    confidence_boost: bool = Field(False, description="Designed to boost confidence")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean subtask title"""
        if not v or not v.strip():
            raise ValueError('Subtask title cannot be empty')
        return v.strip()


class SubtaskCreate(SubtaskBase):
    """Schema for creating a new subtask"""
    task_id: UUID = Field(..., description="Parent task ID")
    
    # AI assistance
    ai_generated: bool = Field(False, description="Whether AI created this subtask")
    ai_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in breakdown")


class SubtaskUpdate(BaseModel):
    """Schema for updating an existing subtask"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    action: Optional[str] = Field(None, max_length=1000)
    completion_criteria: Optional[str] = Field(None, max_length=500)
    
    # Sequencing and dependencies
    sequence_order: Optional[int] = Field(None, ge=1)
    depends_on_subtask_ids: Optional[List[UUID]] = None
    
    # Classification
    subtask_type: Optional[SubtaskTypeEnum] = None
    difficulty_level: Optional[SubtaskDifficultyEnum] = None
    status: Optional[SubtaskStatusEnum] = None
    
    # Time estimates
    estimated_minutes: Optional[int] = Field(None, ge=1, le=240)
    actual_minutes: Optional[int] = Field(None, ge=1, le=480)
    
    # ADHD-specific support
    energy_required: Optional[int] = Field(None, ge=1, le=10)
    focus_required: Optional[int] = Field(None, ge=1, le=10)
    initiation_support: Optional[str] = Field(None, max_length=500)
    success_indicators: Optional[List[str]] = None
    dopamine_reward: Optional[str] = Field(None, max_length=200)
    
    # Executive function support
    preparation_steps: Optional[List[str]] = None
    materials_needed: Optional[List[str]] = None
    
    # Progress and motivation
    momentum_builder: Optional[bool] = None
    confidence_boost: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean subtask title"""
        if v is not None:
            if not v.strip():
                raise ValueError('Subtask title cannot be empty')
            return v.strip()
        return v


class SubtaskResponse(SubtaskBase):
    """Schema for subtask responses"""
    id: UUID = Field(..., description="Subtask ID")
    task_id: UUID = Field(..., description="Parent task ID")
    
    # Status and progress
    status: SubtaskStatusEnum = Field(..., description="Current subtask status")
    actual_minutes: Optional[int] = Field(None, description="Actual time spent")
    
    # AI assistance
    ai_generated: bool = Field(False, description="Whether AI created this subtask")
    ai_confidence: Optional[float] = Field(None, description="AI confidence in breakdown")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="When subtask was started")
    completed_at: Optional[datetime] = Field(None, description="When subtask was completed")
    
    # Computed properties
    is_blocked: Optional[bool] = Field(None, description="Whether subtask is blocked by dependencies")
    can_start: Optional[bool] = Field(None, description="Whether subtask can be started now")

    class Config:
        from_attributes = True


class SubtaskListResponse(BaseModel):
    """Schema for paginated subtask list responses"""
    subtasks: List[SubtaskResponse] = Field(..., description="List of subtasks")
    total: int = Field(..., description="Total number of subtasks")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class SubtaskActionRequest(BaseModel):
    """Schema for subtask actions like start, complete, skip"""
    action: str = Field(..., description="Action to perform (start, complete, skip)")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    actual_minutes: Optional[int] = Field(None, ge=1, description="Actual duration for completion")


class SubtaskFilters(BaseModel):
    """Schema for filtering subtasks"""
    task_id: Optional[UUID] = Field(None, description="Filter by parent task")
    status: Optional[List[SubtaskStatusEnum]] = Field(None, description="Filter by status")
    subtask_type: Optional[List[SubtaskTypeEnum]] = Field(None, description="Filter by type")
    difficulty_level: Optional[List[SubtaskDifficultyEnum]] = Field(None, description="Filter by difficulty")
    ai_generated: Optional[bool] = Field(None, description="Filter by AI generation")
    can_start_now: Optional[bool] = Field(None, description="Filter by availability to start")
