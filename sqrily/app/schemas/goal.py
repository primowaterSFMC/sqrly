"""
Goal-related Pydantic schemas for request/response validation.

This module contains all the schemas for goal operations including
Sqrily methodology integration and ADHD-specific features.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from ..models.goal import GoalStatus


class GoalStatusEnum(str, Enum):
    """Goal status enumeration for API"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ComplexityAssessmentEnum(str, Enum):
    """Goal complexity assessment for ADHD planning"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OverwhelmRiskEnum(str, Enum):
    """Overwhelm risk assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GoalBase(BaseModel):
    """Base goal schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Goal title")
    description: Optional[str] = Field(None, max_length=2000, description="Goal description")
    
    # Sqrily integration
    values_alignment: Optional[List[str]] = Field(None, description="List of values this goal aligns with")
    mission_connection: Optional[str] = Field(None, max_length=1000, description="How this connects to personal mission")
    role_category: Optional[str] = Field(None, max_length=100, description="Role category (professional, personal, etc.)")
    
    # Goal specifics
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    success_metrics: Optional[List[str]] = Field(None, description="List of success criteria")
    priority_level: int = Field(5, ge=1, le=10, description="Priority level (1-10)")
    
    # ADHD-specific
    complexity_assessment: ComplexityAssessmentEnum = Field(ComplexityAssessmentEnum.MEDIUM, description="Complexity assessment")
    estimated_effort_hours: Optional[int] = Field(None, ge=1, le=1000, description="Estimated effort in hours")
    overwhelm_risk: OverwhelmRiskEnum = Field(OverwhelmRiskEnum.MEDIUM, description="Risk of causing overwhelm")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean goal title"""
        if not v or not v.strip():
            raise ValueError('Goal title cannot be empty')
        return v.strip()

    @field_validator('values_alignment')
    @classmethod
    def validate_values_alignment(cls, v):
        """Validate values alignment list"""
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 values allowed')
            # Clean and validate each value
            cleaned_values = []
            for value in v:
                if isinstance(value, str) and value.strip():
                    cleaned_values.append(value.strip())
            return cleaned_values
        return v

    @field_validator('success_metrics')
    @classmethod
    def validate_success_metrics(cls, v):
        """Validate success metrics list"""
        if v is not None:
            if len(v) > 15:
                raise ValueError('Maximum 15 success metrics allowed')
            # Clean and validate each metric
            cleaned_metrics = []
            for metric in v:
                if isinstance(metric, str) and metric.strip():
                    cleaned_metrics.append(metric.strip())
            return cleaned_metrics
        return v


class GoalCreate(GoalBase):
    """Schema for creating a new goal"""
    natural_language_input: Optional[str] = Field(None, max_length=1000, description="Original user input for AI processing")


class GoalUpdate(BaseModel):
    """Schema for updating an existing goal"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    
    # Sqrily integration
    values_alignment: Optional[List[str]] = None
    mission_connection: Optional[str] = Field(None, max_length=1000)
    role_category: Optional[str] = Field(None, max_length=100)
    
    # Goal specifics
    status: Optional[GoalStatusEnum] = None
    target_date: Optional[datetime] = None
    success_metrics: Optional[List[str]] = None
    priority_level: Optional[int] = Field(None, ge=1, le=10)
    
    # ADHD-specific
    complexity_assessment: Optional[ComplexityAssessmentEnum] = None
    estimated_effort_hours: Optional[int] = Field(None, ge=1, le=1000)
    overwhelm_risk: Optional[OverwhelmRiskEnum] = None
    
    # Progress
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean goal title"""
        if v is not None:
            if not v.strip():
                raise ValueError('Goal title cannot be empty')
            return v.strip()
        return v


class GoalResponse(GoalBase):
    """Schema for goal responses"""
    id: UUID = Field(..., description="Goal ID")
    user_id: UUID = Field(..., description="User ID")
    
    # Status and progress
    status: GoalStatusEnum = Field(..., description="Current goal status")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    
    # Sqrily quadrant (calculated)
    fc_quadrant: Optional[int] = Field(None, description="Franklin Covey quadrant (1-4)")
    quadrant_name: Optional[str] = Field(None, description="Human-readable quadrant name")
    
    # AI analysis
    ai_breakdown: Optional[Dict[str, Any]] = Field(None, description="AI-generated phases and tasks")
    ai_insights: Optional[Dict[str, Any]] = Field(None, description="AI analysis and recommendations")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="When goal was completed")
    
    # Computed properties
    is_overdue: Optional[bool] = Field(None, description="Whether goal is overdue")
    days_until_target: Optional[int] = Field(None, description="Days until target date")
    
    # Related data counts
    task_count: Optional[int] = Field(None, description="Number of associated tasks")
    completed_task_count: Optional[int] = Field(None, description="Number of completed tasks")
    milestone_count: Optional[int] = Field(None, description="Number of milestones")

    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """Schema for paginated goal list responses"""
    goals: List[GoalResponse] = Field(..., description="List of goals")
    total: int = Field(..., description="Total number of goals")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class GoalFilters(BaseModel):
    """Schema for goal filtering parameters"""
    status: Optional[List[GoalStatusEnum]] = Field(None, description="Filter by status")
    fc_quadrant: Optional[List[int]] = Field(None, description="Filter by Sqrily quadrant")
    role_category: Optional[List[str]] = Field(None, description="Filter by role category")
    complexity_assessment: Optional[List[ComplexityAssessmentEnum]] = Field(None, description="Filter by complexity")
    overwhelm_risk: Optional[List[OverwhelmRiskEnum]] = Field(None, description="Filter by overwhelm risk")
    target_before: Optional[datetime] = Field(None, description="Target date before this date")
    target_after: Optional[datetime] = Field(None, description="Target date after this date")
    min_priority: Optional[int] = Field(None, ge=1, le=10, description="Minimum priority level")
    max_priority: Optional[int] = Field(None, ge=1, le=10, description="Maximum priority level")
    values_alignment: Optional[List[str]] = Field(None, description="Filter by values alignment")


class MilestoneCreate(BaseModel):
    """Schema for creating a milestone"""
    title: str = Field(..., min_length=1, max_length=255, description="Milestone title")
    description: Optional[str] = Field(None, max_length=1000, description="Milestone description")
    target_date: datetime = Field(..., description="Target completion date")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean milestone title"""
        if not v or not v.strip():
            raise ValueError('Milestone title cannot be empty')
        return v.strip()


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean milestone title"""
        if v is not None:
            if not v.strip():
                raise ValueError('Milestone title cannot be empty')
            return v.strip()
        return v


class MilestoneResponse(BaseModel):
    """Schema for milestone responses"""
    id: UUID = Field(..., description="Milestone ID")
    goal_id: UUID = Field(..., description="Associated goal ID")
    title: str = Field(..., description="Milestone title")
    description: Optional[str] = Field(None, description="Milestone description")
    target_date: datetime = Field(..., description="Target completion date")
    is_completed: bool = Field(..., description="Whether milestone is completed")
    completed_at: Optional[datetime] = Field(None, description="When milestone was completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class GoalAnalysisRequest(BaseModel):
    """Schema for requesting AI goal analysis"""
    include_breakdown: bool = Field(True, description="Include task breakdown")
    include_timeline: bool = Field(True, description="Include timeline suggestions")
    include_risk_assessment: bool = Field(True, description="Include ADHD risk assessment")
    user_context: Optional[str] = Field(None, max_length=500, description="Additional context for AI")


class GoalAnalysisResponse(BaseModel):
    """Schema for AI goal analysis response"""
    goal_id: UUID = Field(..., description="Goal ID")
    quadrant_assignment: int = Field(..., description="Recommended Sqrily quadrant")
    quadrant_reasoning: str = Field(..., description="Explanation for quadrant assignment")
    complexity_assessment: ComplexityAssessmentEnum = Field(..., description="AI complexity assessment")
    overwhelm_risk: OverwhelmRiskEnum = Field(..., description="AI overwhelm risk assessment")
    recommended_breakdown: Optional[List[Dict[str, Any]]] = Field(None, description="Recommended task breakdown")
    timeline_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Timeline and milestone suggestions")
    adhd_considerations: List[str] = Field(..., description="ADHD-specific considerations and tips")
    confidence_score: float = Field(..., description="AI confidence in the analysis")


class GoalProgressUpdate(BaseModel):
    """Schema for updating goal progress"""
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    notes: Optional[str] = Field(None, max_length=500, description="Progress notes")
    milestone_completed: Optional[UUID] = Field(None, description="Milestone ID if one was completed")
