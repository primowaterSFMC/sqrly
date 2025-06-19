"""
Subtask API endpoints for the Sqrly ADHD Planner.

This module provides comprehensive subtask management functionality with
ADHD-specific features including dependency tracking, energy matching,
and executive function support.
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import structlog

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...schemas.subtask import (
    SubtaskCreate, SubtaskUpdate, SubtaskResponse, SubtaskListResponse,
    SubtaskFilters, SubtaskActionRequest
)
from ...services.subtask_service import SubtaskService, SubtaskNotFoundError, SubtaskBlockedError

logger = structlog.get_logger()
router = APIRouter()


@router.get("/task/{task_id}", response_model=List[SubtaskResponse])
async def get_subtasks_for_task(
    task_id: UUID = Path(..., description="Task ID"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    subtask_type: Optional[List[str]] = Query(None, description="Filter by type"),
    difficulty_level: Optional[List[str]] = Query(None, description="Filter by difficulty"),
    ai_generated: Optional[bool] = Query(None, description="Filter by AI generation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all subtasks for a specific task.

    Returns subtasks ordered by sequence and creation time,
    with ADHD-specific metadata and dependency information.
    """
    logger.info("Fetching subtasks for task", user_id=str(current_user.id), task_id=str(task_id))

    # Build filters
    filters = SubtaskFilters(
        task_id=task_id,
        status=status,
        subtask_type=subtask_type,
        difficulty_level=difficulty_level,
        ai_generated=ai_generated
    )

    subtask_service = SubtaskService(db)
    subtasks = await subtask_service.get_subtasks_for_task(
        task_id=task_id,
        user_id=current_user.id,
        filters=filters
    )

    return subtasks


@router.post("/", response_model=SubtaskResponse)
async def create_subtask(
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subtask.

    Supports ADHD-specific features like energy requirements,
    executive function support, and dependency tracking.
    """
    logger.info("Creating subtask", user_id=str(current_user.id), title=subtask_data.title)

    subtask_service = SubtaskService(db)
    try:
        return await subtask_service.create_subtask(
            user_id=current_user.id,
            subtask_data=subtask_data
        )
    except SubtaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{subtask_id}", response_model=SubtaskResponse)
async def get_subtask(
    subtask_id: UUID = Path(..., description="Subtask ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific subtask by ID.

    Returns detailed subtask information including ADHD-specific
    support features and dependency status.
    """
    logger.info("Fetching subtask", user_id=str(current_user.id), subtask_id=str(subtask_id))

    subtask_service = SubtaskService(db)
    subtask = await subtask_service.get_subtask(
        subtask_id=subtask_id,
        user_id=current_user.id
    )

    if not subtask:
        raise HTTPException(status_code=404, detail=f"Subtask {subtask_id} not found")

    return subtask


@router.put("/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    subtask_data: SubtaskUpdate,
    subtask_id: UUID = Path(..., description="Subtask ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing subtask.

    Supports partial updates and maintains ADHD-specific
    features and dependency relationships.
    """
    logger.info("Updating subtask", user_id=str(current_user.id), subtask_id=str(subtask_id))

    subtask_service = SubtaskService(db)
    subtask = await subtask_service.update_subtask(
        subtask_id=subtask_id,
        user_id=current_user.id,
        subtask_data=subtask_data
    )

    if not subtask:
        raise HTTPException(status_code=404, detail=f"Subtask {subtask_id} not found")

    return subtask


@router.delete("/{subtask_id}")
async def delete_subtask(
    subtask_id: UUID = Path(..., description="Subtask ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a subtask.

    Removes the subtask and updates any dependent subtasks
    to maintain consistency.
    """
    logger.info("Deleting subtask", user_id=str(current_user.id), subtask_id=str(subtask_id))

    subtask_service = SubtaskService(db)
    success = await subtask_service.delete_subtask(
        subtask_id=subtask_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(status_code=404, detail=f"Subtask {subtask_id} not found")

    return {
        "message": "Subtask deleted successfully",
        "subtask_id": str(subtask_id),
        "adhd_friendly_message": "Subtask removed! One less thing to worry about."
    }


@router.post("/{subtask_id}/action", response_model=SubtaskResponse)
async def perform_subtask_action(
    action_request: SubtaskActionRequest,
    subtask_id: UUID = Path(..., description="Subtask ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform an action on a subtask (start, complete, skip).

    Supports ADHD-friendly actions with dependency checking
    and executive function support.
    """
    logger.info("Performing subtask action",
                user_id=str(current_user.id),
                subtask_id=str(subtask_id),
                action=action_request.action)

    subtask_service = SubtaskService(db)
    try:
        subtask = await subtask_service.perform_action(
            subtask_id=subtask_id,
            user_id=current_user.id,
            action_request=action_request
        )

        if not subtask:
            raise HTTPException(status_code=404, detail=f"Subtask {subtask_id} not found")

        return subtask

    except SubtaskBlockedError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(e),
                "blocking_subtasks": e.blocking_subtasks,
                "adhd_friendly_message": "This subtask needs other subtasks to be completed first. Let's tackle those dependencies!"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))