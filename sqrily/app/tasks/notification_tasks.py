"""
Notification-related background tasks for Sqrily ADHD Planner.
"""
import structlog
from datetime import datetime, timedelta
from celery import current_task
from ..celery_app import celery_app
from ..database import get_db
from ..models.user import User
from ..models.task import Task, TaskStatus

logger = structlog.get_logger()


@celery_app.task(bind=True)
def send_focus_reminders(self):
    """
    Send focus reminders to users who have tasks due soon.
    """
    try:
        db = next(get_db())
        
        # Get users who have tasks due in the next 2 hours
        upcoming_deadline = datetime.utcnow() + timedelta(hours=2)
        
        tasks_due_soon = db.query(Task).filter(
            Task.due_date <= upcoming_deadline,
            Task.due_date > datetime.utcnow(),
            Task.status != TaskStatus.COMPLETED,
            Task.deleted_at.is_(None)
        ).all()
        
        # Group tasks by user
        user_tasks = {}
        for task in tasks_due_soon:
            if task.user_id not in user_tasks:
                user_tasks[task.user_id] = []
            user_tasks[task.user_id].append(task)
        
        # Send reminders to each user
        reminders_sent = 0
        for user_id, tasks in user_tasks.items():
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.notification_preferences.get("focus_reminders", True):
                # In a real implementation, this would send actual notifications
                # For now, we'll just log the reminder
                task_titles = [task.title for task in tasks]
                logger.info(
                    f"Focus reminder for user {user.email}",
                    tasks=task_titles,
                    count=len(tasks)
                )
                reminders_sent += 1
        
        db.close()
        
        logger.info(f"Sent {reminders_sent} focus reminders")
        return {"reminders_sent": reminders_sent}
        
    except Exception as e:
        logger.error(f"Error sending focus reminders: {str(e)}")
        return {"error": str(e)}


@celery_app.task(bind=True)
def send_break_reminders(self, user_id: int):
    """
    Send break reminders to a specific user.
    """
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Check if user wants break reminders
        if not user.notification_preferences.get("break_reminders", True):
            logger.info(f"Break reminders disabled for user {user_id}")
            return {"message": "Break reminders disabled"}
        
        # In a real implementation, this would send actual notifications
        logger.info(f"Break reminder sent to user {user.email}")
        
        db.close()
        
        return {"message": "Break reminder sent"}
        
    except Exception as e:
        logger.error(f"Error sending break reminder: {str(e)}")
        return {"error": str(e)}


@celery_app.task(bind=True)
def send_overwhelm_alert(self, user_id: int, overwhelm_level: str):
    """
    Send overwhelm alert to a specific user.
    """
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Check if user wants overwhelm alerts
        if not user.notification_preferences.get("overwhelm_alerts", True):
            logger.info(f"Overwhelm alerts disabled for user {user_id}")
            return {"message": "Overwhelm alerts disabled"}
        
        # In a real implementation, this would send actual notifications
        logger.info(
            f"Overwhelm alert sent to user {user.email}",
            level=overwhelm_level
        )
        
        db.close()
        
        return {"message": "Overwhelm alert sent", "level": overwhelm_level}
        
    except Exception as e:
        logger.error(f"Error sending overwhelm alert: {str(e)}")
        return {"error": str(e)}


@celery_app.task(bind=True)
def send_daily_summary(self, user_id: int):
    """
    Send daily summary to a specific user.
    """
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Check if user wants daily summaries
        if not user.notification_preferences.get("daily_summaries", True):
            logger.info(f"Daily summaries disabled for user {user_id}")
            return {"message": "Daily summaries disabled"}
        
        # Get user's tasks for today
        today = datetime.utcnow().date()
        today_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.due_date >= today,
            Task.due_date < today + timedelta(days=1),
            Task.deleted_at.is_(None)
        ).all()
        
        completed_tasks = [t for t in today_tasks if t.status == TaskStatus.COMPLETED]
        pending_tasks = [t for t in today_tasks if t.status != TaskStatus.COMPLETED]
        
        # In a real implementation, this would send actual notifications
        logger.info(
            f"Daily summary sent to user {user.email}",
            completed_count=len(completed_tasks),
            pending_count=len(pending_tasks)
        )
        
        db.close()
        
        return {
            "message": "Daily summary sent",
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error sending daily summary: {str(e)}")
        return {"error": str(e)}
