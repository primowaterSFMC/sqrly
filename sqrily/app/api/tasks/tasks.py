"""
Task API endpoints for the Sqrly ADHD Planner.

This module provides comprehensive task management functionality with
ADHD-specific features including AI analysis, task breakdown, and
executive function support.
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import structlog

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskFilters, TaskActionRequest, TaskBreakdownRequest, TaskBreakdownResponse
)
from ...services.task_service import TaskService
from ...exceptions import TaskNotFoundError, ValidationError

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    task_type: Optional[List[str]] = Query(None, description="Filter by type"),
    complexity_level: Optional[List[str]] = Query(None, description="Filter by complexity"),
    fc_quadrant: Optional[List[int]] = Query(None, description="Filter by Sqrily quadrant"),
    goal_id: Optional[UUID] = Query(None, description="Filter by goal"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of user's tasks with filtering options.

    Supports ADHD-friendly filtering by complexity, energy level,
    and Sqrily quadrant for better task organization.
    """
    logger.info("Fetching tasks", user_id=str(current_user.id), page=page, per_page=per_page)

    # Create filters object
    filters = TaskFilters(
        status=status,
        task_type=task_type,
        complexity_level=complexity_level,
        fc_quadrant=fc_quadrant,
        goal_id=goal_id
    )

    task_service = TaskService(db)
    return await task_service.get_user_tasks(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        filters=filters
    )


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task with AI analysis and Sqrily quadrant assignment.

    The AI will analyze the task for complexity, priority, and provide
    ADHD-specific recommendations for execution.
    """
    logger.info("Creating task", user_id=str(current_user.id), title=task_data.title)

    task_service = TaskService(db)
    return await task_service.create_task(
        user_id=current_user.id,
        task_data=task_data
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.

    Returns detailed task information including AI analysis,
    progress tracking, and ADHD-specific recommendations.
    """
    logger.info("Fetching task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    task = await task_service.get_task(task_id=task_id, user_id=current_user.id)

    if not task:
        raise TaskNotFoundError(str(task_id))

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_data: TaskUpdate,
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task.

    Supports partial updates and will re-run AI analysis if
    significant changes are made to complexity or requirements.
    """
    logger.info("Updating task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    task = await task_service.update_task(
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data
    )

    if not task:
        raise TaskNotFoundError(str(task_id))

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a task.

    Tasks are not permanently deleted but marked as deleted
    to preserve data integrity and allow for recovery.
    """
    logger.info("Deleting task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    success = await task_service.delete_task(task_id=task_id, user_id=current_user.id)

    if not success:
        raise TaskNotFoundError(str(task_id))

    return {
        "message": "Task deleted successfully",
        "task_id": str(task_id),
        "adhd_friendly_message": "Task removed! Don't worry - you can always create a new one if needed."
    }


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(
    action_data: TaskActionRequest,
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start working on a task.

    Marks the task as in progress and starts time tracking.
    Includes ADHD-friendly momentum building features.
    """
    logger.info("Starting task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    task = await task_service.start_task(
        task_id=task_id,
        user_id=current_user.id,
        notes=action_data.notes
    )

    if not task:
        raise TaskNotFoundError(str(task_id))

    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    action_data: TaskActionRequest,
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed.

    Records completion time and actual duration.
    Provides ADHD-friendly celebration and momentum building.
    """
    logger.info("Completing task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    task = await task_service.complete_task(
        task_id=task_id,
        user_id=current_user.id,
        actual_duration_minutes=action_data.actual_duration_minutes,
        notes=action_data.notes
    )

    if not task:
        raise TaskNotFoundError(str(task_id))

    return task


@router.post("/{task_id}/break-down", response_model=TaskBreakdownResponse)
async def break_down_task(
    breakdown_request: TaskBreakdownRequest,
    task_id: UUID = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Use AI to break down a complex task into smaller, manageable subtasks.

    This is especially helpful for ADHD users who struggle with
    executive function and task initiation.
    """
    logger.info("Breaking down task", user_id=str(current_user.id), task_id=str(task_id))

    task_service = TaskService(db)
    breakdown = await task_service.break_down_task(
        task_id=task_id,
        user_id=current_user.id,
        breakdown_request=breakdown_request
    )

    if not breakdown:
        raise TaskNotFoundError(str(task_id))

    return breakdown