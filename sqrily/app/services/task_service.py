"""
Task service for business logic and database operations.

This service handles all task-related operations including CRUD,
AI analysis, task breakdown, and ADHD-specific functionality.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import structlog

from ..models.task import Task, TaskStatus, TaskComplexity, TaskType
from ..models.user import User
from ..schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskFilters, TaskBreakdownRequest, TaskBreakdownResponse
)
from ..services.ai_service import OpenAIService
from ..exceptions import (
    TaskNotFoundError, ValidationError, TaskTooComplexError,
    EnergyMismatchError, OverwhelmDetectedError
)

logger = structlog.get_logger()


class TaskService:
    """Service class for task operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = OpenAIService()
    
    async def get_user_tasks(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[TaskFilters] = None
    ) -> TaskListResponse:
        """Get paginated list of user's tasks with filtering"""
        
        # Base query
        query = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        )
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Task.status.in_(filters.status))
            
            if filters.task_type:
                query = query.filter(Task.task_type.in_(filters.task_type))
            
            if filters.complexity_level:
                query = query.filter(Task.complexity_level.in_(filters.complexity_level))
            
            if filters.fc_quadrant:
                query = query.filter(Task.fc_quadrant.in_(filters.fc_quadrant))
            
            if filters.goal_id:
                query = query.filter(Task.goal_id == filters.goal_id)
            
            if filters.due_before:
                query = query.filter(Task.due_date <= filters.due_before)
            
            if filters.due_after:
                query = query.filter(Task.due_date >= filters.due_after)
            
            if filters.context_tags:
                # Filter by context tags (JSON contains)
                for tag in filters.context_tags:
                    query = query.filter(Task.context_tags.contains([tag]))
            
            if filters.min_priority:
                query = query.filter(Task.ai_priority_score >= filters.min_priority)
            
            if filters.max_priority:
                query = query.filter(Task.ai_priority_score <= filters.max_priority)
        
        # Order by priority and creation date
        query = query.order_by(
            Task.ai_priority_score.desc().nulls_last(),
            Task.created_at.desc()
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        tasks = query.offset(offset).limit(per_page).all()
        
        # Convert to response models
        task_responses = []
        for task in tasks:
            task_response = await self._task_to_response(task)
            task_responses.append(task_response)
        
        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total,
            has_prev=page > 1
        )
    
    async def get_task(self, task_id: UUID, user_id: UUID) -> Optional[TaskResponse]:
        """Get a specific task by ID"""
        
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return None
        
        return await self._task_to_response(task)
    
    async def create_task(self, user_id: UUID, task_data: TaskCreate) -> TaskResponse:
        """Create a new task with AI analysis"""
        
        # Check for overwhelm before creating
        await self._check_user_overwhelm(user_id)
        
        # Create task instance
        task = Task(
            user_id=user_id,
            goal_id=task_data.goal_id,
            title=task_data.title,
            description=task_data.description,
            natural_language_input=task_data.natural_language_input,
            importance_level=task_data.importance_level,
            urgency_level=task_data.urgency_level,
            task_type=task_data.task_type,
            complexity_level=task_data.complexity_level,
            estimated_duration_minutes=task_data.estimated_duration_minutes,
            due_date=task_data.due_date,
            scheduled_start=task_data.scheduled_start,
            scheduled_end=task_data.scheduled_end,
            executive_difficulty=task_data.executive_difficulty,
            initiation_difficulty=task_data.initiation_difficulty,
            completion_difficulty=task_data.completion_difficulty,
            required_energy_level=task_data.required_energy_level,
            context_tags=task_data.context_tags,
            required_materials=task_data.required_materials,
            optimal_environment=task_data.optimal_environment
        )
        
        # Calculate Sqrily quadrant
        task.fc_quadrant = self._calculate_quadrant(
            task_data.urgency_level,
            task_data.importance_level
        )
        
        # Save to database first
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        # Run AI analysis asynchronously
        try:
            await self._run_ai_analysis(task)
            self.db.commit()
        except Exception as e:
            logger.warning("AI analysis failed", task_id=str(task.id), error=str(e))
            # Continue without AI analysis - not critical
        
        return await self._task_to_response(task)
    
    async def update_task(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: TaskUpdate
    ) -> Optional[TaskResponse]:
        """Update an existing task"""
        
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return None
        
        # Track if significant changes were made for AI re-analysis
        significant_changes = False
        
        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(task, field):
                old_value = getattr(task, field)
                setattr(task, field, value)
                
                # Check for significant changes
                if field in ['title', 'description', 'complexity_level', 'estimated_duration_minutes']:
                    if old_value != value:
                        significant_changes = True
        
        # Recalculate quadrant if urgency/importance changed
        if 'urgency_level' in update_data or 'importance_level' in update_data:
            task.fc_quadrant = self._calculate_quadrant(
                task.urgency_level,
                task.importance_level
            )
            significant_changes = True
        
        task.updated_at = datetime.utcnow()
        
        # Re-run AI analysis if significant changes
        if significant_changes:
            try:
                await self._run_ai_analysis(task)
            except Exception as e:
                logger.warning("AI re-analysis failed", task_id=str(task.id), error=str(e))
        
        self.db.commit()
        self.db.refresh(task)
        
        return await self._task_to_response(task)
    
    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Soft delete a task"""
        
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return False
        
        task.deleted_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def start_task(
        self,
        task_id: UUID,
        user_id: UUID,
        notes: Optional[str] = None
    ) -> Optional[TaskResponse]:
        """Start working on a task"""
        
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return None
        
        # Check energy level match
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            current_energy = user.get_adhd_preference("current_energy_level", 5)
            if task.required_energy_level > current_energy + 2:
                raise EnergyMismatchError(task.required_energy_level, current_energy)
        
        # Start the task
        task.start_task()
        
        # Add notes if provided
        if notes:
            if not task.ai_suggestions:
                task.ai_suggestions = {}
            task.ai_suggestions["start_notes"] = notes
        
        self.db.commit()
        self.db.refresh(task)
        
        return await self._task_to_response(task)
    
    async def complete_task(
        self,
        task_id: UUID,
        user_id: UUID,
        actual_duration_minutes: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Optional[TaskResponse]:
        """Mark a task as completed"""
        
        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()
        
        if not task:
            return None
        
        # Complete the task
        task.complete_task(actual_duration_minutes)
        
        # Add completion notes
        if notes:
            if not task.ai_suggestions:
                task.ai_suggestions = {}
            task.ai_suggestions["completion_notes"] = notes
        
        self.db.commit()
        self.db.refresh(task)
        
        return await self._task_to_response(task)
    
    def _calculate_quadrant(self, urgency: int, importance: int) -> int:
        """Calculate Sqrily quadrant based on urgency and importance"""
        if urgency >= 7 and importance >= 7:
            return 1  # Urgent & Important
        elif urgency < 7 and importance >= 7:
            return 2  # Not Urgent & Important
        elif urgency >= 7 and importance < 7:
            return 3  # Urgent & Not Important
        else:
            return 4  # Not Urgent & Not Important
    
    async def _task_to_response(self, task: Task) -> TaskResponse:
        """Convert Task model to TaskResponse schema"""
        
        # Calculate computed properties
        is_overdue = task.is_overdue
        is_due_soon = task.is_due_soon
        breakdown_recommended = task.get_breakdown_recommendation()
        quadrant_name = task.quadrant_name
        
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            goal_id=task.goal_id,
            title=task.title,
            description=task.description,
            importance_level=task.importance_level,
            urgency_level=task.urgency_level,
            task_type=task.task_type,
            complexity_level=task.complexity_level,
            estimated_duration_minutes=task.estimated_duration_minutes,
            due_date=task.due_date,
            executive_difficulty=task.executive_difficulty,
            initiation_difficulty=task.initiation_difficulty,
            completion_difficulty=task.completion_difficulty,
            required_energy_level=task.required_energy_level,
            context_tags=task.context_tags,
            required_materials=task.required_materials,
            optimal_environment=task.optimal_environment,
            status=task.status,
            progress_percentage=task.progress_percentage,
            fc_quadrant=task.fc_quadrant,
            quadrant_name=quadrant_name,
            ai_priority_score=task.ai_priority_score,
            ai_suggestions=task.ai_suggestions,
            ai_confidence=task.ai_confidence,
            actual_duration_minutes=task.actual_duration_minutes,
            scheduled_start=task.scheduled_start,
            scheduled_end=task.scheduled_end,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            is_overdue=is_overdue,
            is_due_soon=is_due_soon,
            breakdown_recommended=breakdown_recommended
        )

    async def _run_ai_analysis(self, task: Task):
        """Run AI analysis on a task"""
        try:
            # Prepare task data for AI
            task_context = {
                "title": task.title,
                "description": task.description,
                "complexity_level": task.complexity_level,
                "estimated_duration": task.estimated_duration_minutes,
                "executive_difficulty": task.executive_difficulty,
                "context_tags": task.context_tags,
                "natural_language_input": task.natural_language_input
            }

            # Get AI analysis
            analysis = await self.ai_service.analyze_task_priority(task_context)

            if analysis:
                task.ai_priority_score = analysis.get("priority_score")
                task.ai_suggestions = analysis.get("suggestions", {})
                task.ai_confidence = analysis.get("confidence")

                # Update quadrant if AI suggests different classification
                ai_quadrant = analysis.get("recommended_quadrant")
                if ai_quadrant and 1 <= ai_quadrant <= 4:
                    task.fc_quadrant = ai_quadrant

        except Exception as e:
            logger.error("AI analysis failed", task_id=str(task.id), error=str(e))
            # Set default values
            task.ai_priority_score = task.calculate_priority_score()
            task.ai_confidence = 0.5

    async def _check_user_overwhelm(self, user_id: UUID):
        """Check if user is approaching overwhelm threshold"""

        # Count active tasks
        active_task_count = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                Task.deleted_at.is_(None)
            )
        ).count()

        # Get user's overwhelm threshold
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            threshold = user.get_overwhelm_threshold()
            if active_task_count >= threshold:
                raise OverwhelmDetectedError(active_task_count / threshold)

    async def break_down_task(
        self,
        task_id: UUID,
        user_id: UUID,
        breakdown_request: TaskBreakdownRequest
    ) -> Optional[TaskBreakdownResponse]:
        """Use AI to break down a complex task into subtasks"""

        task = self.db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None)
            )
        ).first()

        if not task:
            return None

        try:
            # Prepare context for AI
            breakdown_context = {
                "task_title": task.title,
                "task_description": task.description,
                "complexity_level": task.complexity_level,
                "estimated_duration": task.estimated_duration_minutes,
                "executive_difficulty": task.executive_difficulty,
                "max_subtasks": breakdown_request.max_subtasks,
                "target_duration": breakdown_request.target_duration_minutes,
                "include_micro_tasks": breakdown_request.include_micro_tasks,
                "user_context": breakdown_request.user_context,
                "context_tags": task.context_tags,
                "required_materials": task.required_materials
            }

            # Get AI breakdown
            breakdown = await self.ai_service.break_down_task(breakdown_context)

            if breakdown:
                return TaskBreakdownResponse(
                    original_task_id=task.id,
                    subtasks=breakdown.get("subtasks", []),
                    ai_reasoning=breakdown.get("reasoning", ""),
                    confidence_score=breakdown.get("confidence", 0.5),
                    estimated_total_time=breakdown.get("total_time", 0)
                )

        except Exception as e:
            logger.error("Task breakdown failed", task_id=str(task.id), error=str(e))
            # Return a simple fallback breakdown
            return TaskBreakdownResponse(
                original_task_id=task.id,
                subtasks=[
                    {
                        "title": f"Step 1: Start {task.title}",
                        "description": "Begin working on this task",
                        "estimated_duration": 15,
                        "complexity": "simple"
                    },
                    {
                        "title": f"Step 2: Continue {task.title}",
                        "description": "Make progress on the main work",
                        "estimated_duration": max(15, (task.estimated_duration_minutes or 30) - 15),
                        "complexity": "medium"
                    }
                ],
                ai_reasoning="AI analysis unavailable, providing basic breakdown",
                confidence_score=0.3,
                estimated_total_time=task.estimated_duration_minutes or 30
            )

        return None
