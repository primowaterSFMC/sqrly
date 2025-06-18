"""
Analytics-related background tasks for Sqrily ADHD Planner.
"""
import structlog
from datetime import datetime, timedelta
from celery import current_task
from ..celery_app import celery_app
from ..database import get_db
from ..models.user import User
from ..models.task import Task, TaskStatus
from ..models.goal import Goal
from ..models import AISession

logger = structlog.get_logger()


@celery_app.task(bind=True)
def check_user_overwhelm_levels(self):
    """
    Check overwhelm levels for all active users.
    """
    try:
        db = next(get_db())
        
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        overwhelmed_users = 0
        for user in users:
            # Calculate overwhelm score based on various factors
            overwhelm_score = calculate_user_overwhelm_score(user, db)
            
            if overwhelm_score > 7:  # High overwhelm threshold
                # Trigger overwhelm alert
                from .notification_tasks import send_overwhelm_alert
                send_overwhelm_alert.delay(user.id, "high")
                overwhelmed_users += 1
                
                logger.info(
                    f"High overwhelm detected for user {user.email}",
                    score=overwhelm_score
                )
        
        db.close()
        
        logger.info(f"Checked overwhelm levels for {len(users)} users, {overwhelmed_users} alerts sent")
        return {"users_checked": len(users), "alerts_sent": overwhelmed_users}
        
    except Exception as e:
        logger.error(f"Error checking overwhelm levels: {str(e)}")
        return {"error": str(e)}


def calculate_user_overwhelm_score(user: User, db) -> float:
    """
    Calculate overwhelm score for a user based on various factors.
    """
    score = 0.0
    
    # Factor 1: Number of overdue tasks
    overdue_tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.due_date < datetime.utcnow(),
        Task.status != TaskStatus.COMPLETED,
        Task.deleted_at.is_(None)
    ).count()
    score += overdue_tasks * 1.5
    
    # Factor 2: Number of tasks due today
    today = datetime.utcnow().date()
    today_tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.due_date >= today,
        Task.due_date < today + timedelta(days=1),
        Task.status != TaskStatus.COMPLETED,
        Task.deleted_at.is_(None)
    ).count()
    score += today_tasks * 0.5
    
    # Factor 3: Number of high-priority tasks
    high_priority_tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.priority_level == "high",
        Task.status != TaskStatus.COMPLETED,
        Task.deleted_at.is_(None)
    ).count()
    score += high_priority_tasks * 1.0
    
    # Factor 4: Recent AI session frequency (might indicate stress)
    recent_sessions = db.query(AISession).filter(
        AISession.user_id == user.id,
        AISession.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    if recent_sessions > 10:  # More than 10 AI sessions in 24 hours
        score += 2.0
    
    return min(score, 10.0)  # Cap at 10


@celery_app.task(bind=True)
def cleanup_old_ai_sessions(self):
    """
    Clean up old AI sessions to keep the database tidy.
    """
    try:
        db = next(get_db())
        
        # Delete AI sessions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_sessions = db.query(AISession).filter(
            AISession.created_at < cutoff_date
        )
        
        count = old_sessions.count()
        old_sessions.delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {count} old AI sessions")
        return {"sessions_cleaned": count}
        
    except Exception as e:
        logger.error(f"Error cleaning up AI sessions: {str(e)}")
        return {"error": str(e)}


@celery_app.task(bind=True)
def generate_user_analytics(self, user_id: int):
    """
    Generate analytics data for a specific user.
    """
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Calculate various analytics
        analytics = {}
        
        # Task completion rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= thirty_days_ago,
            Task.deleted_at.is_(None)
        ).all()
        
        if recent_tasks:
            completed_tasks = [t for t in recent_tasks if t.status == TaskStatus.COMPLETED]
            analytics["completion_rate"] = len(completed_tasks) / len(recent_tasks)
        else:
            analytics["completion_rate"] = 0.0
        
        # Average task duration
        completed_with_duration = [
            t for t in recent_tasks 
            if t.status == TaskStatus.COMPLETED and t.actual_duration_minutes
        ]
        if completed_with_duration:
            avg_duration = sum(t.actual_duration_minutes for t in completed_with_duration) / len(completed_with_duration)
            analytics["avg_task_duration"] = avg_duration
        else:
            analytics["avg_task_duration"] = 0.0
        
        # Goal progress
        active_goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status.in_(["active", "in_progress"]),
            Goal.deleted_at.is_(None)
        ).count()
        analytics["active_goals"] = active_goals
        
        # Overwhelm score
        analytics["current_overwhelm_score"] = calculate_user_overwhelm_score(user, db)
        
        # Most productive time of day (based on task completions)
        # This would require more complex analysis in a real implementation
        analytics["most_productive_hour"] = 10  # Default to 10 AM
        
        db.close()
        
        logger.info(f"Generated analytics for user {user_id}")
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating user analytics: {str(e)}")
        return {"error": str(e)}


@celery_app.task(bind=True)
def update_goal_progress(self, goal_id: int):
    """
    Update progress for a specific goal based on completed tasks.
    """
    try:
        db = next(get_db())
        
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            logger.error(f"Goal {goal_id} not found")
            return {"error": "Goal not found"}
        
        # Get all tasks related to this goal
        related_tasks = db.query(Task).filter(
            Task.goal_id == goal_id,
            Task.deleted_at.is_(None)
        ).all()
        
        if not related_tasks:
            logger.info(f"No tasks found for goal {goal_id}")
            return {"message": "No tasks found for goal"}
        
        # Calculate progress
        completed_tasks = [t for t in related_tasks if t.status == TaskStatus.COMPLETED]
        progress_percentage = (len(completed_tasks) / len(related_tasks)) * 100
        
        # Update goal progress
        goal.progress_percentage = progress_percentage
        
        # Update goal status based on progress
        if progress_percentage == 100:
            goal.status = "completed"
            goal.completed_at = datetime.utcnow()
        elif progress_percentage > 0:
            goal.status = "in_progress"
        
        db.commit()
        db.close()
        
        logger.info(f"Updated progress for goal {goal_id}: {progress_percentage}%")
        return {"goal_id": goal_id, "progress": progress_percentage}
        
    except Exception as e:
        logger.error(f"Error updating goal progress: {str(e)}")
        return {"error": str(e)}
