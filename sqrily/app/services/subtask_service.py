"""
Subtask service for the Sqrly ADHD Planner.

This module provides comprehensive subtask management functionality with
ADHD-specific features including dependency tracking, energy matching,
and executive function support.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import structlog

from ..models.subtask import Subtask, SubtaskStatus, SubtaskType, SubtaskDifficulty
from ..models.task import Task
from ..schemas.subtask import (
    SubtaskCreate, SubtaskUpdate, SubtaskResponse, SubtaskListResponse,
    SubtaskFilters, SubtaskActionRequest
)

logger = structlog.get_logger()


class SubtaskNotFoundError(Exception):
    """Raised when a subtask is not found"""
    def __init__(self, subtask_id: str):
        self.subtask_id = subtask_id
        super().__init__(f"Subtask {subtask_id} not found")


class SubtaskBlockedError(Exception):
    """Raised when trying to start a blocked subtask"""
    def __init__(self, subtask_id: str, blocking_subtasks: List[str]):
        self.subtask_id = subtask_id
        self.blocking_subtasks = blocking_subtasks
        super().__init__(f"Subtask {subtask_id} is blocked by: {', '.join(blocking_subtasks)}")


class SubtaskService:
    """Service for managing subtasks with ADHD-specific features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_subtasks_for_task(
        self,
        task_id: UUID,
        user_id: UUID,
        filters: Optional[SubtaskFilters] = None
    ) -> List[SubtaskResponse]:
        """Get all subtasks for a specific task"""
        
        # Verify task ownership
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return []
        
        # Build query
        query = self.db.query(Subtask).filter(Subtask.task_id == task_id)
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Subtask.status.in_([s.value for s in filters.status]))
            if filters.subtask_type:
                query = query.filter(Subtask.subtask_type.in_([t.value for t in filters.subtask_type]))
            if filters.difficulty_level:
                query = query.filter(Subtask.difficulty_level.in_([d.value for d in filters.difficulty_level]))
            if filters.ai_generated is not None:
                query = query.filter(Subtask.ai_generated == filters.ai_generated)
        
        # Order by sequence
        subtasks = query.order_by(Subtask.sequence_order, Subtask.created_at).all()
        
        # Convert to response objects
        responses = []
        for subtask in subtasks:
            response = await self._subtask_to_response(subtask)
            responses.append(response)
        
        return responses
    
    async def get_subtask(
        self,
        subtask_id: UUID,
        user_id: UUID
    ) -> Optional[SubtaskResponse]:
        """Get a specific subtask by ID"""
        
        subtask = self.db.query(Subtask).join(Task).filter(
            and_(
                Subtask.id == subtask_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not subtask:
            return None
        
        return await self._subtask_to_response(subtask)
    
    async def create_subtask(
        self,
        user_id: UUID,
        subtask_data: SubtaskCreate
    ) -> SubtaskResponse:
        """Create a new subtask"""
        
        # Verify task ownership
        task = self.db.query(Task).filter(
            and_(
                Task.id == subtask_data.task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            raise SubtaskNotFoundError(str(subtask_data.task_id))
        
        # Create subtask
        subtask = Subtask(
            task_id=subtask_data.task_id,
            title=subtask_data.title,
            action=subtask_data.action,
            completion_criteria=subtask_data.completion_criteria,
            sequence_order=subtask_data.sequence_order,
            depends_on_subtask_ids=subtask_data.depends_on_subtask_ids,
            subtask_type=subtask_data.subtask_type.value,
            difficulty_level=subtask_data.difficulty_level.value,
            estimated_minutes=subtask_data.estimated_minutes,
            energy_required=subtask_data.energy_required,
            focus_required=subtask_data.focus_required,
            initiation_support=subtask_data.initiation_support,
            success_indicators=subtask_data.success_indicators,
            dopamine_reward=subtask_data.dopamine_reward,
            preparation_steps=subtask_data.preparation_steps,
            materials_needed=subtask_data.materials_needed,
            momentum_builder=subtask_data.momentum_builder,
            confidence_boost=subtask_data.confidence_boost,
            ai_generated=subtask_data.ai_generated,
            ai_confidence=subtask_data.ai_confidence
        )
        
        self.db.add(subtask)
        self.db.commit()
        self.db.refresh(subtask)
        
        logger.info("Subtask created", subtask_id=str(subtask.id), task_id=str(subtask_data.task_id))
        
        return await self._subtask_to_response(subtask)
    
    async def update_subtask(
        self,
        subtask_id: UUID,
        user_id: UUID,
        subtask_data: SubtaskUpdate
    ) -> Optional[SubtaskResponse]:
        """Update an existing subtask"""
        
        subtask = self.db.query(Subtask).join(Task).filter(
            and_(
                Subtask.id == subtask_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not subtask:
            return None
        
        # Update fields
        update_data = subtask_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(subtask, field):
                if field in ['subtask_type', 'difficulty_level', 'status'] and value:
                    setattr(subtask, field, value.value if hasattr(value, 'value') else value)
                else:
                    setattr(subtask, field, value)
        
        subtask.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(subtask)
        
        logger.info("Subtask updated", subtask_id=str(subtask_id))
        
        return await self._subtask_to_response(subtask)
    
    async def delete_subtask(
        self,
        subtask_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a subtask"""
        
        subtask = self.db.query(Subtask).join(Task).filter(
            and_(
                Subtask.id == subtask_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not subtask:
            return False
        
        self.db.delete(subtask)
        self.db.commit()
        
        logger.info("Subtask deleted", subtask_id=str(subtask_id))
        
        return True
    
    async def perform_action(
        self,
        subtask_id: UUID,
        user_id: UUID,
        action_request: SubtaskActionRequest
    ) -> Optional[SubtaskResponse]:
        """Perform an action on a subtask (start, complete, skip)"""
        
        subtask = self.db.query(Subtask).join(Task).filter(
            and_(
                Subtask.id == subtask_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not subtask:
            return None
        
        action = action_request.action.lower()
        
        if action == "start":
            if not subtask.can_start():
                blocked_subtasks = await self._get_blocking_subtasks(subtask)
                raise SubtaskBlockedError(str(subtask_id), blocked_subtasks)
            subtask.start_subtask()
            
        elif action == "complete":
            subtask.complete_subtask(action_request.actual_minutes)
            
        elif action == "skip":
            subtask.skip_subtask()
            
        else:
            raise ValueError(f"Unknown action: {action}")
        
        self.db.commit()
        self.db.refresh(subtask)
        
        logger.info("Subtask action performed", subtask_id=str(subtask_id), action=action)
        
        return await self._subtask_to_response(subtask)
    
    async def _subtask_to_response(self, subtask: Subtask) -> SubtaskResponse:
        """Convert a Subtask model to SubtaskResponse"""
        
        return SubtaskResponse(
            id=subtask.id,
            task_id=subtask.task_id,
            title=subtask.title,
            action=subtask.action,
            completion_criteria=subtask.completion_criteria,
            sequence_order=subtask.sequence_order,
            depends_on_subtask_ids=subtask.depends_on_subtask_ids,
            subtask_type=subtask.subtask_type,
            difficulty_level=subtask.difficulty_level,
            status=subtask.status,
            estimated_minutes=subtask.estimated_minutes,
            actual_minutes=subtask.actual_minutes,
            energy_required=subtask.energy_required,
            focus_required=subtask.focus_required,
            initiation_support=subtask.initiation_support,
            success_indicators=subtask.success_indicators,
            dopamine_reward=subtask.dopamine_reward,
            preparation_steps=subtask.preparation_steps,
            materials_needed=subtask.materials_needed,
            momentum_builder=subtask.momentum_builder,
            confidence_boost=subtask.confidence_boost,
            ai_generated=subtask.ai_generated,
            ai_confidence=subtask.ai_confidence,
            created_at=subtask.created_at,
            updated_at=subtask.updated_at,
            started_at=subtask.started_at,
            completed_at=subtask.completed_at,
            is_blocked=subtask.is_blocked,
            can_start=subtask.can_start()
        )
    
    async def _get_blocking_subtasks(self, subtask: Subtask) -> List[str]:
        """Get list of subtask titles that are blocking this subtask"""
        if not subtask.depends_on_subtask_ids:
            return []
        
        blocking = self.db.query(Subtask).filter(
            and_(
                Subtask.id.in_(subtask.depends_on_subtask_ids),
                Subtask.status != SubtaskStatus.COMPLETED
            )
        ).all()
        
        return [s.title for s in blocking]
