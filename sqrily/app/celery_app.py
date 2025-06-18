"""
Celery application configuration for Sqrily ADHD Planner.
"""
from celery import Celery
from .config import get_settings

# Get settings
settings = get_settings()

# Create Celery app
celery_app = Celery(
    "sqrily",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.analytics_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "check-overwhelm-levels": {
        "task": "app.tasks.analytics_tasks.check_user_overwhelm_levels",
        "schedule": 300.0,  # Every 5 minutes
    },
    "send-focus-reminders": {
        "task": "app.tasks.notification_tasks.send_focus_reminders",
        "schedule": 900.0,  # Every 15 minutes
    },
    "cleanup-old-sessions": {
        "task": "app.tasks.analytics_tasks.cleanup_old_ai_sessions",
        "schedule": 3600.0,  # Every hour
    },
}

if __name__ == "__main__":
    celery_app.start()
