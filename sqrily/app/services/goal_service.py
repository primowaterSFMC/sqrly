"""
Goal service for business logic and database operations.

This service handles all goal-related operations including CRUD,
AI analysis, milestone management, and ADHD-specific functionality.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import structlog

from ..models.goal import Goal, Milestone, GoalStatus
from ..models.task import Task
from ..models.user import User
from ..schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalListResponse,
    GoalFilters, GoalAnalysisRequest, GoalAnalysisResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    GoalProgressUpdate
)
from ..services.ai_service import OpenAIService
from ..exceptions import (
    GoalNotFoundError, ValidationError, OverwhelmDetectedError
)

logger = structlog.get_logger()


class GoalService:
    """Service class for goal operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = OpenAIService()
    
    async def get_user_goals(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[GoalFilters] = None
    ) -> GoalListResponse:
        """Get paginated list of user's goals with filtering"""
        
        # Base query
        query = self.db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        )
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Goal.status.in_(filters.status))
            
            if filters.fc_quadrant:
                query = query.filter(Goal.fc_quadrant.in_(filters.fc_quadrant))
            
            if filters.role_category:
                query = query.filter(Goal.role_category.in_(filters.role_category))
            
            if filters.complexity_assessment:
                query = query.filter(Goal.complexity_assessment.in_(filters.complexity_assessment))
            
            if filters.overwhelm_risk:
                query = query.filter(Goal.overwhelm_risk.in_(filters.overwhelm_risk))
            
            if filters.target_before:
                query = query.filter(Goal.target_date <= filters.target_before)
            
            if filters.target_after:
                query = query.filter(Goal.target_date >= filters.target_after)
            
            if filters.min_priority:
                query = query.filter(Goal.priority_level >= filters.min_priority)
            
            if filters.max_priority:
                query = query.filter(Goal.priority_level <= filters.max_priority)
            
            if filters.values_alignment:
                # Filter by values alignment (JSON contains)
                for value in filters.values_alignment:
                    query = query.filter(Goal.values_alignment.contains([value]))
        
        # Order by priority and creation date
        query = query.order_by(
            Goal.priority_level.desc(),
            Goal.created_at.desc()
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        goals = query.offset(offset).limit(per_page).all()
        
        # Convert to response models
        goal_responses = []
        for goal in goals:
            goal_response = await self._goal_to_response(goal)
            goal_responses.append(goal_response)
        
        return GoalListResponse(
            goals=goal_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total,
            has_prev=page > 1
        )
    
    async def get_goal(self, goal_id: UUID, user_id: UUID) -> Optional[GoalResponse]:
        """Get a specific goal by ID"""
        
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()
        
        if not goal:
            return None
        
        return await self._goal_to_response(goal)
    
    async def create_goal(self, user_id: UUID, goal_data: GoalCreate) -> GoalResponse:
        """Create a new goal with AI analysis"""
        
        # Check for overwhelm before creating
        await self._check_user_overwhelm(user_id)
        
        # Create goal instance
        goal = Goal(
            user_id=user_id,
            title=goal_data.title,
            description=goal_data.description,
            values_alignment=goal_data.values_alignment,
            mission_connection=goal_data.mission_connection,
            role_category=goal_data.role_category,
            target_date=goal_data.target_date,
            success_metrics=goal_data.success_metrics,
            priority_level=goal_data.priority_level,
            complexity_assessment=goal_data.complexity_assessment,
            estimated_effort_hours=goal_data.estimated_effort_hours,
            overwhelm_risk=goal_data.overwhelm_risk
        )
        
        # Calculate Sqrily quadrant based on priority and urgency
        goal.fc_quadrant = self._calculate_goal_quadrant(goal)
        
        # Save to database first
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        
        # Run AI analysis asynchronously
        try:
            await self._run_ai_analysis(goal, goal_data.natural_language_input)
            self.db.commit()
        except Exception as e:
            logger.warning("AI analysis failed", goal_id=str(goal.id), error=str(e))
            # Continue without AI analysis - not critical
        
        return await self._goal_to_response(goal)
    
    async def update_goal(
        self,
        goal_id: UUID,
        user_id: UUID,
        goal_data: GoalUpdate
    ) -> Optional[GoalResponse]:
        """Update an existing goal"""
        
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()
        
        if not goal:
            return None
        
        # Track if significant changes were made for AI re-analysis
        significant_changes = False
        
        # Update fields
        update_data = goal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(goal, field):
                old_value = getattr(goal, field)
                setattr(goal, field, value)
                
                # Check for significant changes
                if field in ['title', 'description', 'complexity_assessment', 'estimated_effort_hours']:
                    if old_value != value:
                        significant_changes = True
        
        # Recalculate quadrant if priority changed
        if 'priority_level' in update_data:
            goal.fc_quadrant = self._calculate_goal_quadrant(goal)
            significant_changes = True
        
        goal.updated_at = datetime.utcnow()
        
        # Re-run AI analysis if significant changes
        if significant_changes:
            try:
                await self._run_ai_analysis(goal)
            except Exception as e:
                logger.warning("AI re-analysis failed", goal_id=str(goal.id), error=str(e))
        
        self.db.commit()
        self.db.refresh(goal)
        
        return await self._goal_to_response(goal)
    
    async def archive_goal(self, goal_id: UUID, user_id: UUID) -> bool:
        """Archive a goal (soft delete)"""
        
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()
        
        if not goal:
            return False
        
        goal.status = GoalStatus.ARCHIVED
        goal.deleted_at = datetime.utcnow()
        goal.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def update_progress(
        self,
        goal_id: UUID,
        user_id: UUID,
        progress_update: GoalProgressUpdate
    ) -> Optional[GoalResponse]:
        """Update goal progress"""
        
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()
        
        if not goal:
            return None
        
        # Update progress
        goal.update_progress(progress_update.progress_percentage)
        
        # Add progress notes
        if progress_update.notes:
            if not goal.ai_insights:
                goal.ai_insights = {}
            goal.ai_insights["progress_notes"] = goal.ai_insights.get("progress_notes", [])
            goal.ai_insights["progress_notes"].append({
                "date": datetime.utcnow().isoformat(),
                "notes": progress_update.notes,
                "progress": progress_update.progress_percentage
            })
        
        # Handle milestone completion
        if progress_update.milestone_completed:
            milestone = self.db.query(Milestone).filter(
                and_(
                    Milestone.id == progress_update.milestone_completed,
                    Milestone.goal_id == goal_id
                )
            ).first()
            
            if milestone:
                milestone.is_completed = True
                milestone.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(goal)
        
        return await self._goal_to_response(goal)
    
    def _calculate_goal_quadrant(self, goal: Goal) -> int:
        """Calculate Sqrily quadrant for a goal"""
        # For goals, we consider priority level and target date urgency
        urgency = 5  # Default
        
        if goal.target_date:
            days_until_target = (goal.target_date - datetime.utcnow()).days
            if days_until_target <= 7:
                urgency = 9  # Very urgent
            elif days_until_target <= 30:
                urgency = 7  # Urgent
            elif days_until_target <= 90:
                urgency = 5  # Moderate
            else:
                urgency = 3  # Not urgent
        
        importance = goal.priority_level
        
        if urgency >= 7 and importance >= 7:
            return 1  # Urgent & Important
        elif urgency < 7 and importance >= 7:
            return 2  # Not Urgent & Important
        elif urgency >= 7 and importance < 7:
            return 3  # Urgent & Not Important
        else:
            return 4  # Not Urgent & Not Important

    async def _goal_to_response(self, goal: Goal) -> GoalResponse:
        """Convert Goal model to GoalResponse schema"""

        # Calculate computed properties
        is_overdue = goal.is_overdue if hasattr(goal, 'is_overdue') else False
        days_until_target = None
        if goal.target_date:
            days_until_target = (goal.target_date - datetime.utcnow()).days

        quadrant_name = goal.quadrant_name if hasattr(goal, 'quadrant_name') else None

        # Get task counts
        task_count = self.db.query(Task).filter(
            and_(Task.goal_id == goal.id, Task.deleted_at.is_(None))
        ).count()

        completed_task_count = self.db.query(Task).filter(
            and_(
                Task.goal_id == goal.id,
                Task.status == "completed",
                Task.deleted_at.is_(None)
            )
        ).count()

        milestone_count = self.db.query(Milestone).filter(
            Milestone.goal_id == goal.id
        ).count()

        return GoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            values_alignment=goal.values_alignment,
            mission_connection=goal.mission_connection,
            role_category=goal.role_category,
            target_date=goal.target_date,
            success_metrics=goal.success_metrics,
            priority_level=goal.priority_level,
            complexity_assessment=goal.complexity_assessment,
            estimated_effort_hours=goal.estimated_effort_hours,
            overwhelm_risk=goal.overwhelm_risk,
            status=goal.status,
            progress_percentage=goal.progress_percentage,
            fc_quadrant=goal.fc_quadrant,
            quadrant_name=quadrant_name,
            ai_breakdown=goal.ai_breakdown,
            ai_insights=goal.ai_insights,
            ai_confidence=goal.ai_confidence,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            completed_at=goal.completed_at,
            is_overdue=is_overdue,
            days_until_target=days_until_target,
            task_count=task_count,
            completed_task_count=completed_task_count,
            milestone_count=milestone_count
        )

    async def _run_ai_analysis(self, goal: Goal, natural_language_input: Optional[str] = None):
        """Run AI analysis on a goal"""
        try:
            # Prepare goal data for AI
            goal_context = {
                "title": goal.title,
                "description": goal.description,
                "priority_level": goal.priority_level,
                "complexity_assessment": goal.complexity_assessment,
                "estimated_effort_hours": goal.estimated_effort_hours,
                "values_alignment": goal.values_alignment,
                "mission_connection": goal.mission_connection,
                "natural_language_input": natural_language_input
            }

            # Get AI analysis
            analysis = await self.ai_service.analyze_goal(goal_context)

            if analysis:
                goal.ai_breakdown = analysis.get("breakdown", {})
                goal.ai_insights = analysis.get("insights", {})
                goal.ai_confidence = analysis.get("confidence")

                # Update quadrant if AI suggests different classification
                ai_quadrant = analysis.get("recommended_quadrant")
                if ai_quadrant and 1 <= ai_quadrant <= 4:
                    goal.fc_quadrant = ai_quadrant

        except Exception as e:
            logger.error("AI analysis failed", goal_id=str(goal.id), error=str(e))
            # Set default values
            goal.ai_confidence = 0.5

    async def _check_user_overwhelm(self, user_id: UUID):
        """Check if user is approaching overwhelm threshold"""

        # Count active goals
        active_goal_count = self.db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status.in_([GoalStatus.ACTIVE]),
                Goal.deleted_at.is_(None)
            )
        ).count()

        # Get user's overwhelm threshold for goals (typically lower than tasks)
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Goals have a lower threshold since they're bigger commitments
            threshold = max(3, user.get_overwhelm_threshold() // 3)
            if active_goal_count >= threshold:
                raise OverwhelmDetectedError(active_goal_count / threshold)

    async def analyze_goal(
        self,
        goal_id: UUID,
        user_id: UUID,
        analysis_request: GoalAnalysisRequest
    ) -> Optional[GoalAnalysisResponse]:
        """Get AI analysis for a goal"""

        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()

        if not goal:
            return None

        try:
            # Prepare context for AI
            analysis_context = {
                "goal_title": goal.title,
                "goal_description": goal.description,
                "priority_level": goal.priority_level,
                "complexity_assessment": goal.complexity_assessment,
                "estimated_effort_hours": goal.estimated_effort_hours,
                "values_alignment": goal.values_alignment,
                "mission_connection": goal.mission_connection,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "include_breakdown": analysis_request.include_breakdown,
                "include_timeline": analysis_request.include_timeline,
                "include_risk_assessment": analysis_request.include_risk_assessment,
                "user_context": analysis_request.user_context
            }

            # Get AI analysis
            analysis = await self.ai_service.analyze_goal_comprehensive(analysis_context)

            if analysis:
                return GoalAnalysisResponse(
                    goal_id=goal.id,
                    quadrant_assignment=analysis.get("quadrant", goal.fc_quadrant),
                    quadrant_reasoning=analysis.get("quadrant_reasoning", ""),
                    complexity_assessment=analysis.get("complexity", goal.complexity_assessment),
                    overwhelm_risk=analysis.get("overwhelm_risk", goal.overwhelm_risk),
                    recommended_breakdown=analysis.get("breakdown", []),
                    timeline_suggestions=analysis.get("timeline", []),
                    adhd_considerations=analysis.get("adhd_tips", []),
                    confidence_score=analysis.get("confidence", 0.5)
                )

        except Exception as e:
            logger.error("Goal analysis failed", goal_id=str(goal.id), error=str(e))
            # Return a basic fallback analysis
            return GoalAnalysisResponse(
                goal_id=goal.id,
                quadrant_assignment=goal.fc_quadrant,
                quadrant_reasoning="AI analysis unavailable, using basic classification",
                complexity_assessment=goal.complexity_assessment,
                overwhelm_risk=goal.overwhelm_risk,
                recommended_breakdown=[],
                timeline_suggestions=[],
                adhd_considerations=[
                    "Break this goal into smaller, manageable tasks",
                    "Set regular check-ins to track progress",
                    "Celebrate small wins along the way"
                ],
                confidence_score=0.3
            )

        return None

    async def get_goal_tasks(self, goal_id: UUID, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all tasks for a goal"""

        # Verify goal ownership
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()

        if not goal:
            return []

        # Get tasks
        tasks = self.db.query(Task).filter(
            and_(
                Task.goal_id == goal_id,
                Task.deleted_at.is_(None)
            )
        ).order_by(Task.created_at.desc()).all()

        # Convert to dict format
        task_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "complexity_level": task.complexity_level,
                "progress_percentage": task.progress_percentage,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "is_overdue": task.is_overdue if hasattr(task, 'is_overdue') else False
            }
            task_list.append(task_dict)

        return task_list

    async def create_milestone(
        self,
        goal_id: UUID,
        user_id: UUID,
        milestone_data: MilestoneCreate
    ) -> Optional[MilestoneResponse]:
        """Create a milestone for a goal"""

        # Verify goal ownership
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()

        if not goal:
            return None

        # Create milestone
        milestone = Milestone(
            goal_id=goal_id,
            title=milestone_data.title,
            description=milestone_data.description,
            target_date=milestone_data.target_date
        )

        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)

        return MilestoneResponse(
            id=milestone.id,
            goal_id=milestone.goal_id,
            title=milestone.title,
            description=milestone.description,
            target_date=milestone.target_date,
            is_completed=milestone.is_completed,
            completed_at=milestone.completed_at,
            created_at=milestone.created_at,
            updated_at=milestone.updated_at
        )

    async def get_goal_milestones(
        self,
        goal_id: UUID,
        user_id: UUID
    ) -> List[MilestoneResponse]:
        """Get all milestones for a goal"""

        # Verify goal ownership
        goal = self.db.query(Goal).filter(
            and_(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()

        if not goal:
            return []

        # Get milestones
        milestones = self.db.query(Milestone).filter(
            Milestone.goal_id == goal_id
        ).order_by(Milestone.target_date.asc()).all()

        # Convert to response models
        milestone_responses = []
        for milestone in milestones:
            milestone_response = MilestoneResponse(
                id=milestone.id,
                goal_id=milestone.goal_id,
                title=milestone.title,
                description=milestone.description,
                target_date=milestone.target_date,
                is_completed=milestone.is_completed,
                completed_at=milestone.completed_at,
                created_at=milestone.created_at,
                updated_at=milestone.updated_at
            )
            milestone_responses.append(milestone_response)

        return milestone_responses

    async def update_milestone(
        self,
        milestone_id: UUID,
        user_id: UUID,
        milestone_data: MilestoneUpdate
    ) -> Optional[MilestoneResponse]:
        """Update a milestone"""

        # Get milestone and verify goal ownership
        milestone = self.db.query(Milestone).join(Goal).filter(
            and_(
                Milestone.id == milestone_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None)
            )
        ).first()

        if not milestone:
            return None

        # Update fields
        update_data = milestone_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(milestone, field):
                setattr(milestone, field, value)

        # Handle completion
        if milestone_data.is_completed and not milestone.is_completed:
            milestone.completed_at = datetime.utcnow()
        elif not milestone_data.is_completed and milestone.is_completed:
            milestone.completed_at = None

        milestone.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(milestone)

        return MilestoneResponse(
            id=milestone.id,
            goal_id=milestone.goal_id,
            title=milestone.title,
            description=milestone.description,
            target_date=milestone.target_date,
            is_completed=milestone.is_completed,
            completed_at=milestone.completed_at,
            created_at=milestone.created_at,
            updated_at=milestone.updated_at
        )
