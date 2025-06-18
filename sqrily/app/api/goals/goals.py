"""
Goal API endpoints for the Sqrly ADHD Planner.

This module provides comprehensive goal management functionality with
Sqrily methodology integration and ADHD-specific features.
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import structlog

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalListResponse,
    GoalFilters, GoalAnalysisRequest, GoalAnalysisResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    GoalProgressUpdate
)
from ...services.goal_service import GoalService
from ...exceptions import GoalNotFoundError, ValidationError

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=GoalListResponse)
async def get_goals(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    fc_quadrant: Optional[List[int]] = Query(None, description="Filter by Sqrily quadrant"),
    role_category: Optional[List[str]] = Query(None, description="Filter by role category"),
    complexity_assessment: Optional[List[str]] = Query(None, description="Filter by complexity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of user's goals with filtering options.

    Supports ADHD-friendly filtering by complexity, quadrant,
    and role category for better goal organization.
    """
    logger.info("Fetching goals", user_id=str(current_user.id), page=page, per_page=per_page)

    # Create filters object
    filters = GoalFilters(
        status=status,
        fc_quadrant=fc_quadrant,
        role_category=role_category,
        complexity_assessment=complexity_assessment
    )

    goal_service = GoalService(db)
    return await goal_service.get_user_goals(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        filters=filters
    )


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new goal with AI analysis and Sqrily quadrant assignment.

    The AI will analyze the goal for complexity, priority, and provide
    ADHD-specific recommendations for achievement.
    """
    logger.info("Creating goal", user_id=str(current_user.id), title=goal_data.title)

    goal_service = GoalService(db)
    return await goal_service.create_goal(
        user_id=current_user.id,
        goal_data=goal_data
    )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific goal by ID.

    Returns detailed goal information including AI analysis,
    progress tracking, and ADHD-specific recommendations.
    """
    logger.info("Fetching goal", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    goal = await goal_service.get_goal(goal_id=goal_id, user_id=current_user.id)

    if not goal:
        raise GoalNotFoundError(str(goal_id))

    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_data: GoalUpdate,
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing goal.

    Supports partial updates and will re-run AI analysis if
    significant changes are made to complexity or requirements.
    """
    logger.info("Updating goal", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    goal = await goal_service.update_goal(
        goal_id=goal_id,
        user_id=current_user.id,
        goal_data=goal_data
    )

    if not goal:
        raise GoalNotFoundError(str(goal_id))

    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive a goal.

    Goals are not permanently deleted but marked as archived
    to preserve data integrity and allow for recovery.
    """
    logger.info("Archiving goal", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    success = await goal_service.archive_goal(goal_id=goal_id, user_id=current_user.id)

    if not success:
        raise GoalNotFoundError(str(goal_id))

    return {
        "message": "Goal archived successfully",
        "goal_id": str(goal_id),
        "adhd_friendly_message": "Goal safely archived! You can always reactivate it later if needed."
    }


@router.post("/{goal_id}/analyze", response_model=GoalAnalysisResponse)
async def analyze_goal(
    analysis_request: GoalAnalysisRequest,
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI analysis and recommendations for a goal.

    Provides Sqrily quadrant assignment, complexity assessment,
    and ADHD-specific recommendations for goal achievement.
    """
    logger.info("Analyzing goal", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    analysis = await goal_service.analyze_goal(
        goal_id=goal_id,
        user_id=current_user.id,
        analysis_request=analysis_request
    )

    if not analysis:
        raise GoalNotFoundError(str(goal_id))

    return analysis


@router.post("/{goal_id}/progress", response_model=GoalResponse)
async def update_goal_progress(
    progress_update: GoalProgressUpdate,
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update goal progress percentage and notes.

    Automatically handles goal completion when progress reaches 100%.
    Provides ADHD-friendly celebration and momentum building.
    """
    logger.info("Updating goal progress", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    goal = await goal_service.update_progress(
        goal_id=goal_id,
        user_id=current_user.id,
        progress_update=progress_update
    )

    if not goal:
        raise GoalNotFoundError(str(goal_id))

    return goal


@router.get("/{goal_id}/tasks")
async def get_goal_tasks(
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks associated with a goal.

    Returns tasks organized by status and priority for
    better ADHD-friendly goal management.
    """
    logger.info("Fetching goal tasks", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    tasks = await goal_service.get_goal_tasks(
        goal_id=goal_id,
        user_id=current_user.id
    )

    return {
        "goal_id": str(goal_id),
        "tasks": tasks,
        "task_count": len(tasks),
        "completed_count": len([t for t in tasks if t.get("status") == "completed"]),
        "adhd_tip": "Focus on one task at a time. Small progress is still progress!"
    }


# Milestone endpoints
@router.post("/{goal_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(
    milestone_data: MilestoneCreate,
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a milestone for a goal.

    Milestones help break down large goals into manageable chunks,
    which is especially helpful for ADHD users.
    """
    logger.info("Creating milestone", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    milestone = await goal_service.create_milestone(
        goal_id=goal_id,
        user_id=current_user.id,
        milestone_data=milestone_data
    )

    if not milestone:
        raise GoalNotFoundError(str(goal_id))

    return milestone


@router.get("/{goal_id}/milestones", response_model=List[MilestoneResponse])
async def get_goal_milestones(
    goal_id: UUID = Path(..., description="Goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all milestones for a goal.

    Returns milestones ordered by target date for
    better progress visualization.
    """
    logger.info("Fetching goal milestones", user_id=str(current_user.id), goal_id=str(goal_id))

    goal_service = GoalService(db)
    milestones = await goal_service.get_goal_milestones(
        goal_id=goal_id,
        user_id=current_user.id
    )

    return milestones


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_data: MilestoneUpdate,
    milestone_id: UUID = Path(..., description="Milestone ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a milestone.

    Supports marking milestones as completed and updating
    target dates for better goal management.
    """
    logger.info("Updating milestone", user_id=str(current_user.id), milestone_id=str(milestone_id))

    goal_service = GoalService(db)
    milestone = await goal_service.update_milestone(
        milestone_id=milestone_id,
        user_id=current_user.id,
        milestone_data=milestone_data
    )

    if not milestone:
        raise GoalNotFoundError(str(milestone_id))

    return milestone