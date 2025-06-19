#!/usr/bin/env python3
"""
Database seeding script for Sqrly ADHD Planner
Creates comprehensive sample data for development and testing
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set the database URL explicitly
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres123@192.168.4.148:5432/sqrly_db'

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqrily.app.models import (
    User, AuthProvider, SubscriptionTier,
    Task, TaskStatus, TaskComplexity, TaskType,
    Subtask, SubtaskType, SubtaskDifficulty, SubtaskStatus,
    Goal, GoalStatus, SqrilyQuadrant
)
from sqrily.app.api.auth.auth import hash_password

def create_sample_user(db: Session) -> User:
    """Create the main test user account"""
    print("Creating sample user account...")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "jwhiteprimo@gmail.com").first()
    if existing_user:
        print("User already exists, using existing account")
        return existing_user
    
    # Create ADHD profile with realistic preferences
    adhd_profile = {
        "energy_tracking_enabled": True,
        "overwhelm_notifications": True,
        "break_reminders": True,
        "focus_session_length": 25,  # Pomodoro default
        "preferred_work_hours": {
            "start": "09:00",
            "end": "17:00"
        },
        "energy_patterns": {
            "morning_energy": 4,
            "afternoon_energy": 3,
            "evening_energy": 2
        },
        "executive_function_support": {
            "task_breakdown_threshold": 45,  # minutes
            "initiation_support_level": "high",
            "completion_reminders": True
        },
        "sensory_preferences": {
            "background_noise": "white_noise",
            "lighting": "bright",
            "workspace": "organized"
        },
        "medication_schedule": {
            "enabled": True,
            "morning_dose": "08:00",
            "afternoon_dose": "13:00"
        },
        "overwhelm_triggers": [
            "too_many_tasks",
            "unclear_instructions",
            "time_pressure"
        ],
        "coping_strategies": [
            "break_tasks_down",
            "use_timers",
            "take_breaks"
        ]
    }
    
    # Create user
    user = User(
        email="jwhiteprimo@gmail.com",
        password_hash=hash_password("SecuredPassword123"),
        provider=AuthProvider.EMAIL,
        first_name="J",
        last_name="White",
        timezone="America/New_York",
        is_active=True,
        is_verified=True,
        subscription_tier=SubscriptionTier.PREMIUM,
        onboarding_completed=True,
        adhd_profile=adhd_profile
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Created user: {user.full_name} ({user.email})")
    return user

def create_sample_goals(db: Session, user: User) -> list[Goal]:
    """Create sample goals for the user"""
    print("Creating sample goals...")
    
    goals_data = [
        {
            "title": "Improve Work-Life Balance",
            "description": "Create better boundaries between work and personal time to reduce overwhelm",
            "fc_quadrant": 2,  # Important, Not Urgent (Schedule)
            "values_alignment": ["health", "family", "personal_growth"],
            "mission_connection": "Living a balanced life that supports both professional success and personal well-being",
            "role_category": "personal",
            "priority_level": 8,
            "status": GoalStatus.ACTIVE,
            "progress_percentage": 35.0,
            "complexity_assessment": "medium",
            "estimated_effort_hours": 40,
            "overwhelm_risk": "low"
        },
        {
            "title": "Complete Professional Certification",
            "description": "Finish the project management certification to advance career",
            "fc_quadrant": 1,  # Important, Urgent (Focus)
            "values_alignment": ["achievement", "learning", "career_growth"],
            "mission_connection": "Building expertise to create more impact in my professional role",
            "role_category": "professional",
            "priority_level": 9,
            "status": GoalStatus.ACTIVE,
            "progress_percentage": 60.0,
            "complexity_assessment": "high",
            "estimated_effort_hours": 80,
            "overwhelm_risk": "medium",
            "target_date": datetime.utcnow() + timedelta(days=45)
        }
    ]
    
    goals = []
    for goal_data in goals_data:
        goal = Goal(user_id=user.id, **goal_data)
        db.add(goal)
        goals.append(goal)
    
    db.commit()
    print(f"Created {len(goals)} goals")
    return goals

def create_sample_tasks(db: Session, user: User, goals: list[Goal]) -> list[Task]:
    """Create comprehensive sample tasks across all quadrants"""
    print("Creating sample tasks...")
    
    # Get current time for realistic due dates
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    tasks_data = [
        # FOCUS QUADRANT (Important + Urgent) - fc_quadrant = 1
        {
            "title": "Complete project proposal presentation",
            "description": "Finalize slides for the Q1 project proposal presentation to the executive team",
            "fc_quadrant": 1,
            "importance_level": 9,
            "urgency_level": 8,
            "status": TaskStatus.IN_PROGRESS,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.COMPLEX,
            "estimated_duration_minutes": 90,
            "due_date": today + timedelta(days=1),
            "required_energy_level": 8,
            "executive_difficulty": 6,
            "initiation_difficulty": 4,
            "completion_difficulty": 7,
            "context_tags": ["computer", "quiet_space", "presentation_software"],
            "ai_suggestions": {
                "breakdown_recommended": True,
                "best_time": "morning",
                "preparation_needed": ["gather_data", "review_requirements"]
            },
            "progress_percentage": 25.0
        },
        {
            "title": "Review and respond to client feedback",
            "description": "Address urgent client concerns about the recent deliverable",
            "fc_quadrant": 1,
            "importance_level": 8,
            "urgency_level": 9,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 45,
            "due_date": today,
            "required_energy_level": 6,
            "executive_difficulty": 5,
            "initiation_difficulty": 3,
            "completion_difficulty": 6,
            "context_tags": ["email", "phone", "client_portal"]
        },
        {
            "title": "Fix critical bug in production system",
            "description": "Resolve the authentication issue affecting user logins",
            "fc_quadrant": 1,
            "importance_level": 10,
            "urgency_level": 10,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.COMPLEX,
            "estimated_duration_minutes": 60,
            "due_date": today,
            "required_energy_level": 9,
            "executive_difficulty": 7,
            "initiation_difficulty": 5,
            "completion_difficulty": 8,
            "context_tags": ["development_environment", "debugging_tools"],
            "ai_suggestions": {
                "breakdown_recommended": True,
                "urgency_note": "High priority - affects all users"
            }
        },
        
        # SCHEDULE QUADRANT (Important + Not Urgent) - fc_quadrant = 2
        {
            "title": "Plan quarterly team goals",
            "description": "Define objectives and key results for Q2 team performance",
            "fc_quadrant": 2,
            "importance_level": 8,
            "urgency_level": 4,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.COMPLEX,
            "estimated_duration_minutes": 120,
            "due_date": today + timedelta(days=14),
            "required_energy_level": 7,
            "executive_difficulty": 6,
            "initiation_difficulty": 7,
            "completion_difficulty": 5,
            "context_tags": ["meeting_room", "whiteboard", "team_input"],
            "ai_suggestions": {
                "breakdown_recommended": True,
                "best_time": "morning",
                "collaboration_needed": True
            }
        },
        {
            "title": "Research new productivity tools",
            "description": "Evaluate task management and automation tools for team adoption",
            "fc_quadrant": 2,
            "importance_level": 6,
            "urgency_level": 3,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.LEARNING,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 30,
            "due_date": today + timedelta(days=7),
            "required_energy_level": 4,
            "executive_difficulty": 3,
            "initiation_difficulty": 2,
            "completion_difficulty": 4,
            "context_tags": ["computer", "internet", "note_taking"]
        },
        {
            "title": "Schedule annual health checkups",
            "description": "Book appointments with doctor, dentist, and eye doctor",
            "fc_quadrant": 2,
            "importance_level": 7,
            "urgency_level": 2,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 15,
            "due_date": today + timedelta(days=30),
            "required_energy_level": 2,
            "executive_difficulty": 4,
            "initiation_difficulty": 6,
            "completion_difficulty": 2,
            "context_tags": ["phone", "calendar", "insurance_info"]
        },
        
        # DELEGATE QUADRANT (Not Important + Urgent) - fc_quadrant = 3
        {
            "title": "Organize desk workspace",
            "description": "Clean and organize desk area for better focus and productivity",
            "fc_quadrant": 3,
            "importance_level": 4,
            "urgency_level": 6,
            "status": TaskStatus.COMPLETED,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 25,
            "completed_at": now - timedelta(days=2),
            "required_energy_level": 5,
            "executive_difficulty": 3,
            "initiation_difficulty": 4,
            "completion_difficulty": 2,
            "context_tags": ["physical_space", "organizing_supplies"],
            "progress_percentage": 100.0
        },
        {
            "title": "Update team calendar with meetings",
            "description": "Add recurring team meetings and project deadlines to shared calendar",
            "fc_quadrant": 3,
            "importance_level": 3,
            "urgency_level": 7,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 20,
            "due_date": today + timedelta(days=2),
            "required_energy_level": 3,
            "executive_difficulty": 2,
            "initiation_difficulty": 3,
            "completion_difficulty": 2,
            "context_tags": ["calendar_app", "meeting_details"]
        }
    ]
    
    tasks = []
    for i, task_data in enumerate(tasks_data):
        # Assign some tasks to goals
        if i < 4:  # First 4 tasks get assigned to goals
            task_data["goal_id"] = goals[i % len(goals)].id
        
        task = Task(user_id=user.id, **task_data)
        db.add(task)
        tasks.append(task)
    
    db.commit()
    for task in tasks:
        db.refresh(task)
    print(f"Created {len(tasks)} tasks")
    return tasks

def create_more_sample_tasks(db: Session, user: User) -> list[Task]:
    """Create additional sample tasks to reach 15-20 total"""
    print("Creating additional sample tasks...")

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    additional_tasks = [
        {
            "title": "Order office supplies",
            "description": "Restock printer paper, pens, and sticky notes",
            "fc_quadrant": 3,
            "importance_level": 2,
            "urgency_level": 5,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 10,
            "due_date": today + timedelta(days=3),
            "required_energy_level": 2,
            "executive_difficulty": 2,
            "initiation_difficulty": 3,
            "completion_difficulty": 1,
            "context_tags": ["computer", "company_portal", "budget_approval"]
        },

        # ELIMINATE QUADRANT (Not Important + Not Urgent) - fc_quadrant = 4
        {
            "title": "Clean out old email folders",
            "description": "Archive or delete emails from 2022 and earlier",
            "fc_quadrant": 4,
            "importance_level": 2,
            "urgency_level": 2,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 45,
            "due_date": today + timedelta(days=21),
            "required_energy_level": 3,
            "executive_difficulty": 4,
            "initiation_difficulty": 5,
            "completion_difficulty": 3,
            "context_tags": ["email_client", "archive_system"]
        },
        {
            "title": "Reorganize digital photos",
            "description": "Sort and organize photos from the last year into proper folders",
            "fc_quadrant": 4,
            "importance_level": 1,
            "urgency_level": 1,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 60,
            "due_date": today + timedelta(days=60),
            "required_energy_level": 2,
            "executive_difficulty": 3,
            "initiation_difficulty": 6,
            "completion_difficulty": 4,
            "context_tags": ["computer", "photo_software", "external_drive"]
        },

        # Additional FOCUS tasks
        {
            "title": "Prepare for performance review",
            "description": "Compile achievements and prepare talking points for annual review",
            "fc_quadrant": 1,
            "importance_level": 9,
            "urgency_level": 7,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 75,
            "due_date": today + timedelta(days=5),
            "required_energy_level": 7,
            "executive_difficulty": 5,
            "initiation_difficulty": 6,
            "completion_difficulty": 4,
            "context_tags": ["documents", "achievements_list", "quiet_space"],
            "ai_suggestions": {
                "breakdown_recommended": True,
                "preparation_needed": ["gather_feedback", "review_goals"]
            }
        },

        # Additional SCHEDULE tasks
        {
            "title": "Plan vacation time",
            "description": "Research destinations and book time off for summer vacation",
            "fc_quadrant": 2,
            "importance_level": 6,
            "urgency_level": 3,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 90,
            "due_date": today + timedelta(days=45),
            "required_energy_level": 5,
            "executive_difficulty": 4,
            "initiation_difficulty": 3,
            "completion_difficulty": 5,
            "context_tags": ["computer", "travel_sites", "calendar"]
        },
        {
            "title": "Learn new programming framework",
            "description": "Complete online course on React Native development",
            "fc_quadrant": 2,
            "importance_level": 7,
            "urgency_level": 2,
            "status": TaskStatus.IN_PROGRESS,
            "task_type": TaskType.LEARNING,
            "complexity_level": TaskComplexity.COMPLEX,
            "estimated_duration_minutes": 180,
            "due_date": today + timedelta(days=30),
            "required_energy_level": 8,
            "executive_difficulty": 6,
            "initiation_difficulty": 4,
            "completion_difficulty": 7,
            "context_tags": ["computer", "development_environment", "course_materials"],
            "progress_percentage": 40.0,
            "ai_suggestions": {
                "breakdown_recommended": True,
                "learning_path": "structured_modules"
            }
        },

        # Completed tasks for progress demonstration
        {
            "title": "Submit monthly expense report",
            "description": "Compile and submit receipts for business expenses",
            "fc_quadrant": 3,
            "importance_level": 4,
            "urgency_level": 8,
            "status": TaskStatus.COMPLETED,
            "task_type": TaskType.WORK,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 25,
            "actual_duration_minutes": 30,
            "completed_at": now - timedelta(days=1),
            "required_energy_level": 3,
            "executive_difficulty": 3,
            "initiation_difficulty": 4,
            "completion_difficulty": 2,
            "context_tags": ["expense_app", "receipts", "calculator"],
            "progress_percentage": 100.0
        },
        {
            "title": "Call insurance company",
            "description": "Clarify coverage details for recent medical appointment",
            "fc_quadrant": 1,
            "importance_level": 7,
            "urgency_level": 6,
            "status": TaskStatus.COMPLETED,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.SIMPLE,
            "estimated_duration_minutes": 20,
            "actual_duration_minutes": 35,
            "completed_at": now - timedelta(days=3),
            "required_energy_level": 4,
            "executive_difficulty": 5,
            "initiation_difficulty": 7,
            "completion_difficulty": 3,
            "context_tags": ["phone", "insurance_card", "medical_records"],
            "progress_percentage": 100.0
        },

        # Overdue task for testing
        {
            "title": "Update LinkedIn profile",
            "description": "Add recent projects and skills to professional profile",
            "fc_quadrant": 2,
            "importance_level": 5,
            "urgency_level": 4,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.PERSONAL,
            "complexity_level": TaskComplexity.MEDIUM,
            "estimated_duration_minutes": 40,
            "due_date": today - timedelta(days=5),  # Overdue
            "required_energy_level": 4,
            "executive_difficulty": 4,
            "initiation_difficulty": 5,
            "completion_difficulty": 3,
            "context_tags": ["computer", "linkedin", "resume"]
        }
    ]

    tasks = []
    for task_data in additional_tasks:
        task = Task(user_id=user.id, **task_data)
        db.add(task)
        tasks.append(task)

    db.commit()
    for task in tasks:
        db.refresh(task)
    print(f"Created {len(tasks)} additional tasks")
    return tasks

def create_sample_subtasks(db: Session, tasks: list[Task]) -> list[Subtask]:
    """Create subtasks for tasks that have AI breakdown enabled"""
    print("Creating sample subtasks...")

    subtasks = []

    # Find tasks that should have subtasks (complex tasks or those with AI suggestions)
    tasks_with_breakdown = [
        task for task in tasks
        if (task.complexity_level == TaskComplexity.COMPLEX or
            (task.ai_suggestions and task.ai_suggestions.get("breakdown_recommended")))
    ]

    for task in tasks_with_breakdown[:5]:  # Limit to first 5 for demo
        if task.title == "Complete project proposal presentation":
            task_subtasks = [
                {
                    "title": "Gather project requirements and data",
                    "action": "Collect all necessary information, metrics, and requirements for the proposal",
                    "completion_criteria": "All data points and requirements documented in one place",
                    "sequence_order": 1,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 25,
                    "energy_required": 6,
                    "focus_required": 7,
                    "initiation_support": "Start by opening the project folder and reviewing the initial brief",
                    "preparation_steps": ["Open project folder", "Review initial brief", "Create data collection checklist"],
                    "materials_needed": ["Project files", "Previous presentations", "Data sources"],
                    "ai_generated": True,
                    "ai_confidence": 0.85
                },
                {
                    "title": "Create presentation outline",
                    "action": "Structure the presentation flow and key talking points",
                    "completion_criteria": "Clear outline with slide titles and main points for each section",
                    "sequence_order": 2,
                    "depends_on_subtask_ids": [],  # Will be filled after creation
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 20,
                    "energy_required": 7,
                    "focus_required": 8,
                    "initiation_support": "Begin with the standard presentation template structure",
                    "preparation_steps": ["Open presentation template", "Review similar past presentations"],
                    "materials_needed": ["Presentation software", "Template", "Gathered data"],
                    "ai_generated": True,
                    "ai_confidence": 0.90
                },
                {
                    "title": "Design and create slides",
                    "action": "Build the actual presentation slides with content and visuals",
                    "completion_criteria": "All slides created with proper formatting and content",
                    "sequence_order": 3,
                    "subtask_type": SubtaskType.EXECUTION,
                    "difficulty_level": SubtaskDifficulty.HARD,
                    "estimated_minutes": 35,
                    "energy_required": 8,
                    "focus_required": 9,
                    "initiation_support": "Start with the title slide and work through the outline sequentially",
                    "preparation_steps": ["Ensure quiet workspace", "Close distracting applications", "Have all materials ready"],
                    "materials_needed": ["Presentation software", "Images/charts", "Company branding"],
                    "ai_generated": True,
                    "ai_confidence": 0.80,
                    "momentum_builder": True
                },
                {
                    "title": "Practice and refine presentation",
                    "action": "Rehearse the presentation and make final adjustments",
                    "completion_criteria": "Comfortable with timing and flow, all slides polished",
                    "sequence_order": 4,
                    "subtask_type": SubtaskType.REVIEW,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 10,
                    "energy_required": 5,
                    "focus_required": 6,
                    "initiation_support": "Run through the presentation once without stopping",
                    "dopamine_reward": "Celebrate completion with a favorite beverage",
                    "ai_generated": True,
                    "ai_confidence": 0.75,
                    "confidence_boost": True
                }
            ]

        elif task.title == "Plan quarterly team goals":
            task_subtasks = [
                {
                    "title": "Review previous quarter performance",
                    "action": "Analyze what worked well and what needs improvement from Q1",
                    "completion_criteria": "Summary document of Q1 achievements and lessons learned",
                    "sequence_order": 1,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 30,
                    "energy_required": 6,
                    "focus_required": 7,
                    "initiation_support": "Start by pulling up Q1 metrics and team feedback",
                    "materials_needed": ["Q1 reports", "Team feedback", "Performance metrics"],
                    "ai_generated": True,
                    "ai_confidence": 0.88
                },
                {
                    "title": "Gather team input on priorities",
                    "action": "Collect team member perspectives on goals and priorities for Q2",
                    "completion_criteria": "Input collected from all team members via survey or meetings",
                    "sequence_order": 2,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 45,
                    "energy_required": 5,
                    "focus_required": 4,
                    "initiation_support": "Send out a brief survey or schedule 15-minute check-ins",
                    "materials_needed": ["Survey tool", "Calendar", "Meeting notes template"],
                    "ai_generated": True,
                    "ai_confidence": 0.82
                },
                {
                    "title": "Draft OKRs and success metrics",
                    "action": "Create specific, measurable objectives and key results for Q2",
                    "completion_criteria": "3-5 clear OKRs with quantifiable success metrics",
                    "sequence_order": 3,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.HARD,
                    "estimated_minutes": 45,
                    "energy_required": 8,
                    "focus_required": 9,
                    "initiation_support": "Use the OKR template and start with one objective at a time",
                    "materials_needed": ["OKR template", "Team input", "Company goals"],
                    "ai_generated": True,
                    "ai_confidence": 0.85,
                    "momentum_builder": True
                }
            ]

        elif task.title == "Fix critical bug in production system":
            task_subtasks = [
                {
                    "title": "Reproduce the bug locally",
                    "action": "Set up local environment to replicate the authentication issue",
                    "completion_criteria": "Bug consistently reproducible in development environment",
                    "sequence_order": 1,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.HARD,
                    "estimated_minutes": 20,
                    "energy_required": 8,
                    "focus_required": 9,
                    "initiation_support": "Start by checking the error logs and user reports",
                    "materials_needed": ["Development environment", "Error logs", "Test accounts"],
                    "ai_generated": True,
                    "ai_confidence": 0.90
                },
                {
                    "title": "Identify root cause",
                    "action": "Debug the code to find the exact source of the authentication failure",
                    "completion_criteria": "Root cause identified and documented",
                    "sequence_order": 2,
                    "subtask_type": SubtaskType.PREPARATION,
                    "difficulty_level": SubtaskDifficulty.HARD,
                    "estimated_minutes": 25,
                    "energy_required": 9,
                    "focus_required": 10,
                    "initiation_support": "Use debugging tools to step through the authentication flow",
                    "materials_needed": ["Debugger", "Code editor", "Authentication logs"],
                    "ai_generated": True,
                    "ai_confidence": 0.85
                },
                {
                    "title": "Implement and test fix",
                    "action": "Code the solution and verify it resolves the issue",
                    "completion_criteria": "Fix implemented and tested with multiple user scenarios",
                    "sequence_order": 3,
                    "subtask_type": SubtaskType.EXECUTION,
                    "difficulty_level": SubtaskDifficulty.MEDIUM,
                    "estimated_minutes": 15,
                    "energy_required": 7,
                    "focus_required": 8,
                    "initiation_support": "Start with the simplest solution that addresses the root cause",
                    "materials_needed": ["Code editor", "Test accounts", "Testing framework"],
                    "ai_generated": True,
                    "ai_confidence": 0.80,
                    "confidence_boost": True
                }
            ]
        else:
            continue  # Skip tasks without predefined subtasks

        # Create subtasks for this task
        created_subtasks = []
        for subtask_data in task_subtasks:
            subtask = Subtask(task_id=task.id, **subtask_data)
            db.add(subtask)
            created_subtasks.append(subtask)
            subtasks.append(subtask)

        # Update dependencies after creation
        if len(created_subtasks) > 1:
            for i, subtask in enumerate(created_subtasks[1:], 1):
                subtask.depends_on_subtask_ids = [str(created_subtasks[i-1].id)]

    db.commit()
    for subtask in subtasks:
        db.refresh(subtask)
    print(f"Created {len(subtasks)} subtasks")
    return subtasks

def main():
    """Main function to seed the database with comprehensive sample data"""
    print("🌱 Starting database seeding process...")
    print("=" * 50)

    # Create direct database connection
    DATABASE_URL = 'postgresql://postgres:postgres123@192.168.4.148:5432/sqrly_db'
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create database tables if they don't exist
    from sqrily.app.database import Base
    Base.metadata.create_all(bind=engine)

    # Get database session
    db = SessionLocal()

    try:
        # Create sample data
        user = create_sample_user(db)
        goals = create_sample_goals(db, user)
        initial_tasks = create_sample_tasks(db, user, goals)
        additional_tasks = create_more_sample_tasks(db, user)
        all_tasks = initial_tasks + additional_tasks
        subtasks = create_sample_subtasks(db, all_tasks)

        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   • User accounts: 1")
        print(f"   • Goals: {len(goals)}")
        print(f"   • Tasks: {len(all_tasks)}")
        print(f"   • Subtasks: {len(subtasks)}")
        print(f"   • Completed tasks: {len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])}")
        print(f"   • In-progress tasks: {len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS])}")
        print(f"   • Pending tasks: {len([t for t in all_tasks if t.status == TaskStatus.PENDING])}")

        print(f"\n🎯 Task distribution by quadrant:")
        quadrant_counts = {}
        for task in all_tasks:
            quad = task.fc_quadrant
            quadrant_names = {1: "Focus", 2: "Schedule", 3: "Delegate", 4: "Eliminate"}
            quad_name = quadrant_names.get(quad, "Unknown")
            quadrant_counts[quad_name] = quadrant_counts.get(quad_name, 0) + 1

        for quad_name, count in quadrant_counts.items():
            print(f"   • {quad_name}: {count} tasks")

        print(f"\n🧠 ADHD-specific features:")
        print(f"   • Energy levels: 1-5 (realistic distribution)")
        print(f"   • Executive function difficulty ratings included")
        print(f"   • AI breakdown suggestions: {len([t for t in all_tasks if t.ai_suggestions])}")
        print(f"   • Tasks with context tags: {len([t for t in all_tasks if t.context_tags])}")

        print(f"\n📅 Due date distribution:")
        overdue = len([t for t in all_tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != TaskStatus.COMPLETED])
        today_due = len([t for t in all_tasks if t.due_date and t.due_date.date() == datetime.utcnow().date()])
        future_due = len([t for t in all_tasks if t.due_date and t.due_date > datetime.utcnow()])

        print(f"   • Overdue: {overdue}")
        print(f"   • Due today: {today_due}")
        print(f"   • Future due dates: {future_due}")

        print(f"\n🔐 Login credentials:")
        print(f"   • Email: jwhiteprimo@gmail.com")
        print(f"   • Password: SecuredPassword123")

        print(f"\n🚀 Ready for UI development and testing!")

    except Exception as e:
        print(f"❌ Error during database seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
