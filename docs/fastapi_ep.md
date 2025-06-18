# FastAPI Endpoints Reference
## Sqrily AI Planner with ADHD Support

### API Overview
- **Total Endpoints:** 89 REST endpoints + 5 WebSocket connections
- **ADHD-Specific Features:** 25 endpoints
- **AI-Powered Features:** 18 endpoints
- **OAuth Providers:** Google, Apple, Email/Password
- **Real-time Features:** WebSocket timers, notifications, collaboration

---

## 🔐 OAuth & Authentication

### POST `/auth/register`
Register new user with ADHD profile setup

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePass123",
  "first_name": "John",
  "last_name": "Doe",
  "timezone": "America/New_York",
  "adhd_profile": {
    "executive_strengths": ["planning", "working_memory"],
    "executive_challenges": ["initiation", "time_management"],
    "overwhelm_threshold": 6,
    "hyperfocus_tendency": 8,
    "peak_focus_hours": [
      {"start": "09:00", "end": "11:00", "energy": 9}
    ],
    "attention_span_minutes": 25,
    "preferred_task_size": "medium",
    "ai_communication_style": "collaborative"
  }
}
```

**Response Body:**
```json
{
  "user_id": "uuid",
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "onboarding_completed": false,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "onboarding_steps": [
    "adhd_assessment",
    "task_preferences", 
    "ai_collaboration_setup"
  ]
}
```

### POST `/auth/login`
Email/password authentication

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePass123",
  "remember_me": true,
  "device_info": {
    "device_type": "web",
    "user_agent": "Mozilla/5.0...",
    "timezone": "America/New_York"
  }
}
```

**Response Body:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://...",
    "onboarding_completed": true,
    "subscription_tier": "free",
    "adhd_preferences": {
      "ai_communication_style": "collaborative",
      "overwhelm_threshold": 6
    }
  }
}
```

### GET `/auth/google/callback`
Google OAuth callback handler

**Query Parameters:**
```json
{
  "code": "oauth_authorization_code",
  "state": "csrf_state_token",
  "scope": "openid email profile"
}
```

**Response Body:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "provider": "google",
    "onboarding_completed": false
  },
  "is_new_user": true,
  "onboarding_required": true
}
```

### POST `/auth/apple/callback`
Apple Sign In callback handler

**Request Body (Form Data):**
```json
{
  "id_token": "apple_id_token_jwt",
  "code": "authorization_code",
  "state": "csrf_state",
  "user": {
    "name": {
      "firstName": "John",
      "lastName": "Doe"
    },
    "email": "user@privaterelay.appleid.com"
  }
}
```

**Response Body:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@privaterelay.appleid.com",
    "first_name": "John",
    "last_name": "Doe",
    "provider": "apple",
    "onboarding_completed": false,
    "privacy_focused": true
  },
  "is_new_user": true
}
```

### POST `/auth/refresh`
Refresh JWT access tokens

**Request Body:**
```json
{
  "refresh_token": "current_refresh_token"
}
```

**Response Body:**
```json
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 👤 User Management & Profiles

### PATCH `/users/me/adhd-profile`
Update ADHD-specific preferences and settings

**Request Body:**
```json
{
  "executive_strengths": ["planning", "working_memory"],
  "executive_challenges": ["initiation", "task_switching"],
  "overwhelm_threshold": 7,
  "hyperfocus_tendency": 6,
  "peak_focus_hours": [
    {"start": "09:00", "end": "11:00", "energy": 9},
    {"start": "14:00", "end": "16:00", "energy": 7}
  ],
  "energy_pattern": "morning",
  "attention_span_minutes": 30,
  "break_frequency_minutes": 5,
  "preferred_task_size": "small",
  "breakdown_style": "sequential",
  "completion_motivation": ["progress_bars", "celebrations"],
  "ai_communication_style": "collaborative",
  "feedback_sensitivity": 4,
  "optimal_environment": {
    "noise": "quiet",
    "lighting": "bright",
    "temperature": "cool"
  },
  "distraction_triggers": ["notifications", "clutter"]
}
```

**Response Body:**
```json
{
  "updated_preferences": {
    "executive_strengths": ["planning", "working_memory"],
    "executive_challenges": ["initiation", "task_switching"],
    "overwhelm_threshold": 7,
    "attention_span_minutes": 30,
    "ai_communication_style": "collaborative"
  },
  "recalibration_needed": true,
  "ai_adjustments": [
    "Updated timer defaults to 30 minutes",
    "Adjusted collaboration style to collaborative",
    "Recalibrated overwhelm detection threshold"
  ],
  "updated_at": "2024-01-15T14:30:00Z"
}
```

### POST `/users/onboarding`
Complete ADHD-focused onboarding flow

**Request Body:**
```json
{
  "step": "adhd_assessment",
  "responses": {
    "diagnosed_adhd": true,
    "medication": "yes",
    "primary_challenges": [
      "task_initiation",
      "time_management",
      "organization"
    ],
    "coping_strategies": [
      "lists",
      "timers",
      "reminders"
    ],
    "work_style": "flexible",
    "goals": [
      "better_focus",
      "task_completion",
      "stress_reduction"
    ]
  },
  "ai_preferences": {
    "collaboration_level": "high",
    "suggestion_frequency": "moderate",
    "explanation_detail": "concise"
  }
}
```

**Response Body:**
```json
{
  "onboarding_completed": true,
  "adhd_profile_created": true,
  "ai_settings_configured": true,
  "next_steps": [
    "create_first_goal",
    "setup_calendar_integration",
    "try_focus_timer"
  ],
  "personalized_recommendations": {
    "suggested_timer_duration": 25,
    "recommended_break_frequency": 5,
    "optimal_task_size": "medium"
  },
  "welcome_message": "Welcome! Based on your responses, I've customized your experience for better focus and task management."
}
```

---

## 🎯 Goals & Tasks (Sqrily Method)

### POST `/goals`
Create goal with AI-assisted breakdown using Sqrily principles

**Request Body:**
```json
{
  "title": "Launch my freelance business",
  "description": "Start offering web design services to local businesses",
  "target_date": "2024-06-01",
  "values_alignment": ["independence", "creativity", "growth"],
  "mission_connection": "Build financial independence through creative work",
  "role_category": "professional",
  "success_metrics": [
    "3 paying clients",
    "$5000 monthly revenue",
    "professional website launched"
  ],
  "timeline": "6_months",
  "priority_level": 9,
  "context": {
    "current_situation": "Working full-time, planning transition",
    "available_time": "evenings and weekends",
    "resources": "design skills, portfolio examples",
    "constraints": ["limited time", "budget constraints"]
  }
}
```

**Response Body:**
```json
{
  "goal_id": "uuid",
  "title": "Launch my freelance business",
  "fc_quadrant": 2,
  "ai_breakdown": {
    "phases": [
      {
        "name": "Foundation Setup",
        "duration_weeks": 4,
        "tasks": ["create_business_plan", "setup_website", "build_portfolio"]
      },
      {
        "name": "Client Acquisition", 
        "duration_weeks": 6,
        "tasks": ["networking", "marketing", "proposals"]
      }
    ],
    "suggested_milestones": [
      {
        "title": "Business registration complete",
        "target_date": "2024-02-15"
      },
      {
        "title": "First client signed",
        "target_date": "2024-04-01"
      }
    ]
  },
  "ai_insights": {
    "complexity_assessment": "high",
    "estimated_effort": "120_hours",
    "success_probability": 0.75,
    "risk_factors": ["time_management", "client_acquisition"],
    "recommendations": [
      "Break into smaller weekly goals",
      "Set up accountability system",
      "Focus on networking first"
    ]
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

### POST `/tasks`
Create task with AI priority and quadrant assignment

**Request Body:**
```json
{
  "title": "Write project proposal for ABC Company",
  "description": "Detailed proposal for their website redesign project",
  "goal_id": "uuid",
  "due_date": "2024-01-20T17:00:00Z",
  "estimated_duration_minutes": 120,
  "context_tags": ["computer", "research", "writing"],
  "natural_language": "I need to write a compelling proposal that shows my understanding of their brand and includes timeline and pricing",
  "energy_level": 7,
  "complexity_hint": "medium",
  "required_materials": [
    "company_research",
    "portfolio_examples", 
    "pricing_template"
  ],
  "optimal_environment": {
    "location": "home_office",
    "noise_level": "quiet",
    "tools": ["laptop", "notes"]
  }
}
```

**Response Body:**
```json
{
  "task_id": "uuid",
  "title": "Write project proposal for ABC Company",
  "fc_quadrant": 1,
  "ai_priority_score": 8.5,
  "importance_level": 9,
  "urgency_level": 7,
  "complexity_level": "medium",
  "executive_difficulty": 6,
  "initiation_difficulty": 5,
  "completion_difficulty": 4,
  "required_energy_level": 7,
  "ai_suggestions": {
    "suggested_schedule": {
      "start_time": "2024-01-18T09:00:00Z",
      "end_time": "2024-01-18T11:00:00Z",
      "reasoning": "Peak focus hours, sufficient time buffer"
    },
    "breakdown_recommended": true,
    "subtask_count": 4,
    "preparation_steps": [
      "Review company website and materials",
      "Gather portfolio examples",
      "Set up distraction-free workspace"
    ]
  },
  "ai_confidence": 0.85,
  "created_at": "2024-01-15T14:00:00Z"
}
```

### POST `/tasks/bulk-process`
AI processes multiple tasks for ADHD overwhelm management

**Request Body:**
```json
{
  "task_list": [
    "Finish quarterly report",
    "Plan team meeting agenda", 
    "Review and respond to emails",
    "Update project timeline",
    "Call insurance company",
    "Grocery shopping",
    "Schedule dentist appointment"
  ],
  "energy_level": 5,
  "available_time": 180,
  "stress_level": 7,
  "preferences": {
    "prioritize_urgent": true,
    "batch_similar": true,
    "limit_context_switching": true
  },
  "current_context": "work_from_home",
  "time_of_day": "14:00"
}
```

**Response Body:**
```json
{
  "prioritized_tasks": [
    {
      "title": "Review and respond to emails",
      "priority": 1,
      "estimated_duration": 30,
      "reasoning": "Quick win, reduces mental load"
    },
    {
      "title": "Finish quarterly report", 
      "priority": 2,
      "estimated_duration": 90,
      "reasoning": "High importance, requires focus"
    },
    {
      "title": "Plan team meeting agenda",
      "priority": 3, 
      "estimated_duration": 20,
      "reasoning": "Can batch with report work"
    }
  ],
  "suggested_deferrals": [
    {
      "title": "Call insurance company",
      "reason": "Low energy task, better for tomorrow morning",
      "suggested_time": "2024-01-16T09:00:00Z"
    },
    {
      "title": "Grocery shopping",
      "reason": "Personal task, suggest evening or weekend",
      "suggested_time": "2024-01-16T18:00:00Z"
    }
  ],
  "overwhelm_reduction": "45%",
  "estimated_completion": "2.5 hours",
  "energy_management": {
    "current_load": "high",
    "recommended_breaks": 2,
    "warning": "Consider limiting to 3 tasks given current stress level"
  }
}
```

---

## 🧩 Subtasks & Executive Function Support

### POST `/tasks/{task_id}/breakdown`
AI-powered task breakdown for executive dysfunction support

**Request Body:**
```json
{
  "complexity_level": "medium",
  "user_energy": 6,
  "available_time": 120,
  "breakdown_style": "sequential",
  "executive_needs": {
    "initiation_support": true,
    "progress_tracking": true,
    "completion_signals": true
  },
  "preferences": {
    "max_subtask_duration": 20,
    "include_breaks": true,
    "micro_tasks_preferred": false
  },
  "context": {
    "time_of_day": "morning",
    "environment": "home_office",
    "distractions": "minimal"
  }
}
```

**Response Body:**
```json
{
  "subtasks": [
    {
      "id": "uuid",
      "title": "Gather company research materials",
      "sequence_order": 1,
      "difficulty_level": "easy",
      "estimated_minutes": 10,
      "task_type": "preparation",
      "completion_criteria": "All company materials saved in project folder",
      "success_indicators": ["website_saved", "notes_compiled"],
      "dopamine_reward": "Check mark and brief celebration",
      "initiation_support": "Start by opening company website"
    },
    {
      "id": "uuid", 
      "title": "Create proposal outline",
      "sequence_order": 2,
      "difficulty_level": "medium",
      "estimated_minutes": 20,
      "task_type": "planning",
      "completion_criteria": "Clear outline with all sections defined",
      "depends_on_subtask_ids": ["previous_uuid"],
      "preparation_steps": ["review_proposal_template", "organize_research"],
      "energy_required": 6,
      "focus_required": 7
    }
  ],
  "total_estimate": "90 minutes",
  "completion_strategy": {
    "approach": "sequential_with_breaks",
    "break_frequency": "every_30_minutes",
    "motivation_system": "progress_bar_with_rewards"
  },
  "ai_confidence": 0.88
}
```

### POST `/tasks/{task_id}/micro-tasks`
Generate micro-tasks (2-5 minute chunks) for severe executive dysfunction

**Request Body:**
```json
{
  "current_state": "feeling_stuck",
  "overwhelm_level": 8,
  "energy_available": 3,
  "context": "been_avoiding_task_for_days",
  "immediate_needs": ["momentum", "confidence", "clarity"],
  "session_length": 15,
  "environment": {
    "location": "desk",
    "tools_available": ["laptop", "notebook", "phone"],
    "distractions": "moderate"
  }
}
```

**Response Body:**
```json
{
  "micro_tasks": [
    {
      "id": "uuid",
      "action": "Open the document or file",
      "duration": 1,
      "materials_needed": ["laptop"],
      "completion_signal": "Document is open and visible",
      "motivation": "Just opening it is progress!"
    },
    {
      "id": "uuid",
      "action": "Read the first paragraph or section",
      "duration": 3,
      "materials_needed": [],
      "completion_signal": "You've read and understand the context",
      "momentum_builder": true
    },
    {
      "id": "uuid",
      "action": "Write one sentence about your goal",
      "duration": 5,
      "materials_needed": ["keyboard"],
      "completion_signal": "One complete sentence written",
      "confidence_boost": "You're making real progress!"
    }
  ],
  "success_tips": [
    "Focus only on the current micro-task",
    "Celebrate each completion",
    "If you feel momentum, keep going"
  ],
  "reward_suggestions": [
    "favorite_drink",
    "brief_walk",
    "encouraging_self_talk"
  ],
  "total_commitment": "15 minutes maximum"
}
```

### POST `/executive/stuck-helper`
AI assistant for when user feels stuck or unable to start tasks

**Request Body:**
```json
{
  "current_feeling": "overwhelmed",
  "task_id": "uuid",
  "stuck_duration": "2_days",
  "previous_attempts": [
    "tried_to_start_yesterday",
    "opened_document_but_closed_it",
    "made_coffee_to_procrastinate"
  ],
  "current_environment": {
    "location": "home_office",
    "noise_level": "quiet",
    "lighting": "good",
    "tools_ready": true
  },
  "emotional_state": {
    "anxiety_level": 7,
    "motivation": 3,
    "confidence": 4,
    "energy": 5
  },
  "barriers_perceived": [
    "task_seems_too_big",
    "perfectionism",
    "unclear_where_to_start"
  ]
}
```

**Response Body:**
```json
{
  "immediate_actions": [
    {
      "type": "breathing_exercise",
      "instruction": "Take 3 deep breaths to reduce anxiety",
      "duration": 1
    },
    {
      "type": "environment_prep",
      "instruction": "Clear your desk of everything except what you need",
      "duration": 2
    },
    {
      "type": "commitment_reduction",
      "instruction": "Commit to just 10 minutes of work",
      "duration": 10
    }
  ],
  "barrier_analysis": {
    "primary_barrier": "task_seems_too_big",
    "solution": "Break into smallest possible first step",
    "reframe": "You don't need to finish, just start"
  },
  "micro_steps": [
    "Just open the document",
    "Read what you already have",
    "Write one imperfect sentence"
  ],
  "environmental_changes": [
    "Play focus music if helpful",
    "Set a gentle timer for 10 minutes",
    "Have water nearby"
  ],
  "support_strategies": {
    "body_doubling": "Consider virtual co-working session",
    "accountability": "Text someone when you start",
    "reward": "Plan something nice after 10 minutes"
  },
  "encouragement": "Feeling stuck is normal with ADHD. Taking tiny steps is still progress."
}
```

---

## 🤖 AI Planning & Human-in-the-Loop

### POST `/ai/collaborate`
Interactive AI collaboration session with conversation tracking

**Request Body:**
```json
{
  "session_id": "uuid",
  "human_input": "I'm feeling overwhelmed with my project deadlines and don't know how to prioritize",
  "collaboration_mode": "consultative",
  "context": {
    "current_tasks": ["project_a", "project_b", "project_c"],
    "energy_level": 4,
    "time_available": "2_hours",
    "stress_level": 8,
    "previous_attempts": "tried_making_lists_but_got_stuck"
  },
  "preferences": {
    "communication_style": "gentle",
    "detail_level": "moderate",
    "solution_focus": true
  }
}
```

**Response Body:**
```json
{
  "ai_response": "I understand feeling overwhelmed with multiple deadlines - that's really challenging. Let's break this down together step by step.",
  "suggestions": [
    {
      "type": "clarifying_question",
      "content": "Which project has the soonest hard deadline that can't be moved?"
    },
    {
      "type": "immediate_action", 
      "content": "Let's start by listing just the deadlines for each project"
    }
  ],
  "questions": [
    "What's the absolute deadline for each project?",
    "Which project would have the biggest impact if delayed?",
    "How much work is left on each one?"
  ],
  "confidence": 0.75,
  "next_steps": [
    "Gather deadline information",
    "Assess remaining work for each",
    "Create simple priority matrix"
  ],
  "session_progress": {
    "stage": "problem_clarification",
    "completion": 0.2
  },
  "supportive_note": "You're taking the right step by asking for help. We'll figure this out together."
}
```

### POST `/ai/natural-input`
Process natural language planning input with intent recognition

**Request Body:**
```json
{
  "text": "Tomorrow I need to finish the Johnson proposal, call the dentist to reschedule my appointment, pick up groceries for dinner, and work on my presentation for Friday's meeting. I'm feeling anxious about the proposal because it's for a big client.",
  "voice_transcript": null,
  "context": {
    "current_time": "2024-01-15T16:30:00Z",
    "user_energy": 6,
    "calendar_availability": "9am-5pm tomorrow",
    "location": "work_from_home"
  },
  "intent_hints": ["task_creation", "scheduling", "priority_setting"]
}
```

**Response Body:**
```json
{
  "parsed_intent": "task_planning_and_scheduling",
  "extracted_tasks": [
    {
      "title": "Finish Johnson proposal",
      "type": "work",
      "priority": "high",
      "deadline": "implied_urgent",
      "emotional_context": "anxiety_detected",
      "estimated_duration": 120,
      "complexity": "high"
    },
    {
      "title": "Call dentist to reschedule appointment",
      "type": "personal_admin",
      "priority": "medium", 
      "estimated_duration": 10,
      "context_tags": ["phone", "appointment"]
    },
    {
      "title": "Pick up groceries for dinner",
      "type": "personal_errands",
      "priority": "medium",
      "estimated_duration": 45,
      "context_tags": ["errands", "evening"]
    },
    {
      "title": "Work on presentation for Friday meeting",
      "type": "work",
      "priority": "medium",
      "deadline": "2024-01-19",
      "estimated_duration": 90
    }
  ],
  "suggested_actions": [
    {
      "action": "create_tasks",
      "tasks_count": 4
    },
    {
      "action": "schedule_optimization",
      "focus": "anxiety_management_for_proposal"
    },
    {
      "action": "break_down_complex_task",
      "target": "Johnson proposal"
    }
  ],
  "clarification_needed": [
    "What time is Friday's meeting?",
    "How much of the presentation is already done?",
    "Any specific requirements for the Johnson proposal?"
  ],
  "emotional_support": {
    "anxiety_acknowledged": true,
    "suggestion": "Let's break down the proposal into smaller steps to make it feel more manageable"
  }
}
```

### POST `/ai/overwhelm-check`
AI detects and helps manage cognitive overwhelm

**Request Body:**
```json
{
  "current_load": {
    "active_tasks": 8,
    "overdue_tasks": 2,
    "upcoming_deadlines": 5,
    "meetings_today": 4,
    "context_switches": 12
  },
  "energy_level": 3,
  "stress_indicators": [
    "multiple_task_postponements",
    "difficulty_focusing",
    "feeling_scattered"
  ],
  "schedule": {
    "remaining_hours_today": 4,
    "scheduled_meetings": 2,
    "free_time_blocks": 1
  },
  "user_state": {
    "focus_quality": 4,
    "motivation": 3,
    "anxiety_level": 8,
    "last_break": "2_hours_ago"
  }
}
```

**Response Body:**
```json
{
  "overwhelm_risk": "high",
  "risk_factors": [
    "High task count relative to available time",
    "Multiple context switches detected",
    "Energy level below optimal threshold",
    "Anxiety level concerning"
  ],
  "suggested_reductions": [
    {
      "action": "defer_non_urgent",
      "tasks": ["update_linkedin_profile", "organize_files"],
      "rationale": "These can wait until tomorrow"
    },
    {
      "action": "simplify_complex_tasks",
      "tasks": ["quarterly_report"],
      "suggestion": "Focus on just the summary section today"
    }
  ],
  "coping_strategies": [
    {
      "strategy": "take_immediate_break",
      "duration": 15,
      "activity": "walk_or_breathe"
    },
    {
      "strategy": "limit_to_3_tasks",
      "rationale": "More manageable cognitive load"
    },
    {
      "strategy": "batch_similar_tasks",
      "example": "Group all email responses together"
    }
  ],
  "immediate_actions": [
    "Take a 5-minute breathing break",
    "Choose only 3 most important tasks for today",
    "Set a gentle reminder to check in after 1 hour"
  ],
  "supportive_message": "You're taking on a lot right now. It's okay to do less and do it well.",
  "follow_up": {
    "check_in_time": 60,
    "metrics_to_monitor": ["task_completion", "stress_level", "energy"]
  }
}
```

---

## 📅 Calendar & Time Management

### POST `/calendar/time-block`
AI-assisted time blocking with ADHD considerations

**Request Body:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Write quarterly report",
      "estimated_duration": 120,
      "priority": 9,
      "energy_required": 8,
      "complexity": "high"
    },
    {
      "id": "uuid",
      "title": "Team check-ins",
      "estimated_duration": 60,
      "priority": 6,
      "energy_required": 5,
      "complexity": "low"
    }
  ],
  "preferences": {
    "work_hours": {"start": "09:00", "end": "17:00"},
    "buffer_time": 15,
    "max_continuous_work": 90,
    "break_frequency": 25
  },
  "energy_patterns": [
    {"time": "09:00", "energy": 9},
    {"time": "11:00", "energy": 8},
    {"time": "13:00", "energy": 6},
    {"time": "15:00", "energy": 7}
  ],
  "existing_commitments": [
    {
      "start": "10:00",
      "end": "10:30",
      "title": "Daily standup"
    }
  ]
}
```

**Response Body:**
```json
{
  "time_blocks": [
    {
      "task_id": "uuid",
      "title": "Write quarterly report",
      "start_time": "09:00",
      "end_time": "10:00",
      "duration": 60,
      "block_type": "focused_work",
      "rationale": "Peak energy time for high-complexity task"
    },
    {
      "task_id": "uuid", 
      "title": "Write quarterly report (continued)",
      "start_time": "10:30",
      "end_time": "11:30",
      "duration": 60,
      "block_type": "focused_work",
      "rationale": "Continuation after meeting, still high energy"
    },
    {
      "task_id": "uuid",
      "title": "Team check-ins",
      "start_time": "14:00",
      "end_time": "15:00",
      "duration": 60,
      "block_type": "communication",
      "rationale": "Good energy for social interaction"
    }
  ],
  "rationale": "Scheduled high-energy task during peak hours, split to accommodate existing meeting",
  "flexibility_options": [
    "Report writing can be moved to afternoon if morning energy dips",
    "Team check-ins can be shortened if needed"
  ],
  "transition_time": {
    "included": true,
    "buffer_minutes": 15,
    "reasoning": "Helps with context switching"
  },
  "quadrant_balance": {
    "quadrant_1": 60,
    "quadrant_2": 120,
    "quadrant_3": 60,
    "quadrant_4": 0
  }
}
```

### GET `/calendar/focus-time`
Find optimal focus time based on ADHD patterns

**Query Parameters:**
```json
{
  "duration_needed": 90,
  "task_type": "creative",
  "date_range": {
    "start": "2024-01-16",
    "end": "2024-01-18"
  },
  "preferences": {
    "minimum_duration": 45,
    "energy_threshold": 7,
    "avoid_late_afternoon": true
  }
}
```

**Response Body:**
```json
{
  "optimal_slots": [
    {
      "start_time": "2024-01-16T09:00:00Z",
      "end_time": "2024-01-16T10:30:00Z",
      "duration": 90,
      "energy_prediction": 9,
      "distraction_risk": "low",
      "confidence": 0.92,
      "reasoning": "Peak morning energy, no meetings scheduled"
    },
    {
      "start_time": "2024-01-17T09:30:00Z", 
      "end_time": "2024-01-17T11:00:00Z",
      "duration": 90,
      "energy_prediction": 8,
      "distraction_risk": "medium",
      "confidence": 0.85,
      "reasoning": "Good energy, but shorter buffer before next commitment"
    }
  ],
  "energy_prediction": {
    "based_on": "21_days_of_patterns",
    "accuracy": 0.87,
    "factors": ["time_of_day", "day_of_week", "previous_night_sleep"]
  },
  "protection_needed": {
    "notification_blocking": true,
    "calendar_protection": "suggest_blocking_time",
    "environment_prep": ["quiet_space", "focus_music"]
  },
  "backup_options": [
    {
      "start_time": "2024-01-16T14:00:00Z",
      "duration": 60,
      "note": "Shorter session but still viable"
    }
  ]
}
```

---

## 📊 Analytics & Continuous Learning

### GET `/analytics/productivity`
ADHD-aware productivity analytics and patterns

**Query Parameters:**
```json
{
  "timeframe": "last_30_days",
  "include_patterns": true,
  "breakdown_by": ["day_of_week", "time_of_day"],
  "focus_areas": ["energy_patterns", "completion_rates", "overwhelm_incidents"]
}
```

**Response Body:**
```json
{
  "energy_patterns": {
    "peak_hours": ["09:00-11:00", "14:00-15:30"],
    "low_energy": ["13:00-14:00", "16:00-17:00"],
    "weekly_variation": {
      "monday": 7.2,
      "tuesday": 8.1,
      "wednesday": 7.8,
      "thursday": 6.9,
      "friday": 6.1
    },
    "consistency_score": 0.78
  },
  "completion_rates": {
    "overall": 0.73,
    "by_quadrant": {
      "quadrant_1": 0.89,
      "quadrant_2": 0.68,
      "quadrant_3": 0.71,
      "quadrant_4": 0.45
    },
    "by_complexity": {
      "micro": 0.95,
      "simple": 0.84,
      "medium": 0.69,
      "complex": 0.52
    }
  },
  "focus_sessions": {
    "average_duration": 42,
    "completion_rate": 0.81,
    "hyperfocus_incidents": 3,
    "optimal_duration": 28,
    "break_effectiveness": 0.76
  },
  "improvement_areas": [
    {
      "area": "complex_task_completion",
      "current_rate": 0.52,
      "improvement_potential": 0.25,
      "suggested_actions": ["better_task_breakdown", "energy_matching"]
    }
  ],
  "positive_trends": [
    "22% improvement in morning focus sessions",
    "Reduced overwhelm incidents by 35%",
    "Better energy management on Tuesdays"
  ]
}
```

### GET `/analytics/habits`
AI-analyzed habit patterns and improvement suggestions

**Query Parameters:**
```json
{
  "analysis_depth": "comprehensive",
  "pattern_types": ["temporal", "behavioral", "environmental"],
  "include_predictions": true,
  "timeframe": "last_60_days"
}
```

**Response Body:**
```json
{
  "detected_patterns": [
    {
      "pattern_type": "temporal",
      "pattern_name": "monday_morning_avoidance",
      "confidence": 0.89,
      "description": "Tends to avoid difficult tasks on Monday mornings",
      "frequency": "weekly",
      "impact": "medium",
      "suggestion": "Schedule easier tasks for Monday AM, save complex work for Tuesday"
    },
    {
      "pattern_type": "environmental",
      "pattern_name": "music_boost_correlation",
      "confidence": 0.76,
      "description": "37% better focus when instrumental music is playing",
      "trigger": "focus_sessions",
      "impact": "high",
      "suggestion": "Auto-suggest music for focus sessions"
    }
  ],
  "behavior_chains": [
    {
      "trigger": "feeling_overwhelmed",
      "sequence": ["check_phone", "get_coffee", "organize_desk"],
      "outcome": "avoidance_for_20_minutes",
      "frequency": "daily",
      "intervention_point": "after_phone_check",
      "suggested_replacement": "take_3_deep_breaths"
    }
  ],
  "predictions": {
    "next_overwhelm_risk": {
      "date": "2024-01-18",
      "probability": 0.72,
      "factors": ["high_task_load", "low_energy_day", "deadline_pressure"]
    },
    "optimal_scheduling": {
      "best_days": ["tuesday", "wednesday"],
      "best_times": ["09:00-11:00", "14:30-16:00"],
      "avoid_times": ["monday_morning", "friday_afternoon"]
    }
  },
  "habit_recommendations": [
    {
      "habit": "morning_planning_ritual",
      "rationale": "Reduces decision fatigue throughout day",
      "implementation": "5-minute review of top 3 priorities",
      "success_probability": 0.84
    },
    {
      "habit": "energy_check_ins",
      "rationale": "Better task-energy matching",
      "implementation": "Rate energy 1-10 every 2 hours",
      "success_probability": 0.73
    }
  ]
}
```

### GET `/analytics/weekly-review`
Sqrily style weekly review with AI insights

**Query Parameters:**
```json
{
  "week_start": "2024-01-15",
  "include_goal_progress": true,
  "focus_areas": ["role_balance", "quadrant_analysis", "wins_challenges"]
}
```

**Response Body:**
```json
{
  "week_summary": {
    "week_of": "2024-01-15",
    "overall_rating": 7.2,
    "completion_rate": 0.68,
    "energy_average": 6.8
  },
  "goal_progress": [
    {
      "goal_id": "uuid",
      "title": "Launch freelance business",
      "progress_this_week": 0.15,
      "total_progress": 0.45,
      "on_track": true,
      "milestones_hit": 1,
      "challenges": ["time_management", "client_outreach"]
    }
  ],
  "role_balance": {
    "professional": {
      "time_spent": 32,
      "satisfaction": 7,
      "key_activities": ["project_work", "client_calls", "skill_development"]
    },
    "personal": {
      "time_spent": 18,
      "satisfaction": 6,
      "key_activities": ["exercise", "family_time", "hobbies"]
    },
    "self_care": {
      "time_spent": 8,
      "satisfaction": 5,
      "improvement_needed": true
    }
  },
  "quadrant_analysis": {
    "quadrant_1": {"hours": 12, "percentage": 30, "trend": "decreasing"},
    "quadrant_2": {"hours": 18, "percentage": 45, "trend": "increasing"},
    "quadrant_3": {"hours": 8, "percentage": 20, "trend": "stable"},
    "quadrant_4": {"hours": 2, "percentage": 5, "trend": "decreasing"}
  },
  "wins": [
    "Completed Johnson proposal ahead of schedule",
    "Maintained consistent morning routine",
    "Successfully managed overwhelm on Wednesday"
  ],
  "challenges": [
    "Procrastinated on tax preparation",
    "Skipped planned exercise twice",
    "Got overwhelmed by email backlog"
  ],
  "ai_recommendations": [
    "Schedule tax prep as micro-tasks to reduce avoidance",
    "Link exercise to existing habits for better consistency",
    "Implement daily email processing limit"
  ],
  "next_week_focus": [
    "Increase Quadrant 2 activities",
    "Improve self-care role balance",
    "Continue momentum on business goal"
  ]
}
```

---

## 🔗 Integrations

### POST `/integrations/google-calendar`
Connect Google Calendar with ADHD-optimized sync

**Request Body:**
```json
{
  "authorization_code": "google_oauth_code",
  "sync_preferences": {
    "import_existing_events": true,
    "sync_direction": "bidirectional",
    "calendar_selection": ["primary", "work"],
    "adhd_optimizations": {
      "add_buffer_time": true,
      "buffer_minutes": 15,
      "block_focus_time": true,
      "gentle_reminders": true
    }
  },
  "privacy_settings": {
    "share_task_details": false,
    "use_generic_titles": true,
    "sync_personal_events": false
  }
}
```

**Response Body:**
```json
{
  "integration_id": "uuid",
  "status": "connected",
  "calendars_synced": [
    {
      "calendar_id": "primary",
      "name": "Personal",
      "events_imported": 47,
      "sync_enabled": true
    },
    {
      "calendar_id": "work_calendar_id",
      "name": "Work Calendar", 
      "events_imported": 23,
      "sync_enabled": true
    }
  ],
  "sync_summary": {
    "total_events_imported": 70,
    "conflicts_detected": 2,
    "adhd_optimizations_applied": {
      "buffer_time_added": 15,
      "focus_blocks_protected": 8,
      "reminders_adjusted": 23
    }
  },
  "next_sync": "2024-01-16T09:00:00Z",
  "webhook_configured": true,
  "features_enabled": [
    "real_time_sync",
    "conflict_detection", 
    "adhd_buffer_time",
    "focus_protection"
  ]
}
```

### POST `/integrations/spotify`
Connect Spotify for focus music recommendations

**Request Body:**
```json
{
  "authorization_code": "spotify_oauth_code",
  "preferences": {
    "auto_play_focus_music": true,
    "preferred_genres": ["ambient", "classical", "lo-fi"],
    "volume_level": 0.6,
    "playlist_preferences": {
      "instrumental_only": true,
      "no_vocals": true,
      "tempo_range": {"min": 60, "max": 120}
    }
  },
  "adhd_features": {
    "smart_playlist_selection": true,
    "session_length_matching": true,
    "fade_in_out": true,
    "break_time_music": false
  }
}
```

**Response Body:**
```json
{
  "integration_id": "uuid",
  "status": "connected",
  "spotify_account": {
    "display_name": "John Doe",
    "premium": true,
    "available_devices": [
      {"name": "Desktop", "type": "computer"},
      {"name": "Phone", "type": "smartphone"}
    ]
  },
  "curated_playlists": [
    {
      "name": "Deep Focus - 25min",
      "duration": 25,
      "track_count": 8,
      "spotify_id": "playlist_id",
      "optimized_for": "pomodoro_sessions"
    },
    {
      "name": "Creative Flow - 45min",
      "duration": 45, 
      "track_count": 15,
      "spotify_id": "playlist_id",
      "optimized_for": "creative_work"
    }
  ],
  "ai_recommendations": {
    "based_on_listening_history": true,
    "adhd_optimized": true,
    "personalization_accuracy": 0.87
  },
  "features_enabled": [
    "timer_sync",
    "auto_play",
    "smart_playlists",
    "session_matching"
  ]
}
```

### GET `/integrations`
List all connected integrations and their status

**Query Parameters:**
```json
{
  "include_status": true,
  "include_usage_stats": true
}
```

**Response Body:**
```json
{
  "integrations": [
    {
      "id": "uuid",
      "provider": "google_calendar",
      "status": "active",
      "connected_at": "2024-01-10T14:30:00Z",
      "last_sync": "2024-01-15T16:45:00Z",
      "sync_frequency": "real_time",
      "features_used": [
        "bidirectional_sync",
        "buffer_time",
        "focus_protection"
      ],
      "usage_stats": {
        "events_synced": 247,
        "conflicts_resolved": 8,
        "focus_blocks_protected": 23
      }
    },
    {
      "id": "uuid",
      "provider": "spotify",
      "status": "active",
      "connected_at": "2024-01-12T09:15:00Z",
      "last_used": "2024-01-15T14:20:00Z",
      "features_used": [
        "auto_play",
        "session_matching",
        "smart_playlists"
      ],
      "usage_stats": {
        "focus_sessions_with_music": 34,
        "playlists_created": 5,
        "avg_session_improvement": "23%"
      }
    },
    {
      "id": "uuid",
      "provider": "apple_calendar",
      "status": "disconnected",
      "disconnected_at": "2024-01-05T12:00:00Z",
      "disconnect_reason": "user_requested"
    }
  ],
  "available_integrations": [
    {
      "provider": "microsoft_outlook",
      "status": "available",
      "features": ["calendar_sync", "email_integration", "teams_integration"]
    },
    {
      "provider": "notion",
      "status": "coming_soon",
      "features": ["task_sync", "note_integration", "database_sync"]
    }
  ],
  "integration_health": {
    "overall_status": "healthy",
    "active_connections": 2,
    "sync_errors_24h": 0,
    "last_health_check": "2024-01-15T16:50:00Z"
  }
}
```

---

## 🔌 WebSocket Connections

### WebSocket `/ws/timer/{user_id}`
Real-time timer with ADHD hyperfocus detection and gentle notifications

**Connection Events:**

**Timer Start Event:**
```json
{
  "event": "timer_started",
  "type": "focus",
  "duration": 25,
  "task_id": "uuid",
  "adhd_features": {
    "hyperfocus_monitoring": true,
    "gentle_warnings": true,
    "energy_tracking": true
  }
}
```

**Timer Tick Event:**
```json
{
  "event": "timer_tick",
  "elapsed_seconds": 300,
  "remaining_seconds": 1200,
  "percentage": 20.0,
  "energy_check": {
    "current_energy": 7,
    "recommended_break": false
  }
}
```

**Hyperfocus Warning Event:**
```json
{
  "event": "hyperfocus_warning",
  "session_duration": 120,
  "risk_level": "medium",
  "suggestion": "Consider a 5-minute break",
  "next_commitment": "2024-01-15T15:30:00Z",
  "interventions": [
    "gentle_reminder_break",
    "suggest_natural_stopping_point"
  ]
}
```

### WebSocket `/ws/collaboration/{user_id}`
Live AI collaboration sessions with conversation tracking

**Collaboration Events:**

**Session Start:**
```json
{
  "event": "collaboration_started",
  "session_id": "uuid",
  "mode": "consultative",
  "ai_personality": "supportive",
  "user_context": {
    "energy_level": 6,
    "stress_level": 4,
    "available_time": 30
  }
}
```

**AI Response:**
```json
{
  "event": "ai_response",
  "session_id": "uuid",
  "message": "I understand you're feeling overwhelmed. Let's break this down step by step.",
  "suggestions": [
    {
      "type": "immediate_action",
      "content": "Start with the most urgent deadline"
    }
  ],
  "confidence": 0.82,
  "next_questions": ["What's your biggest concern right now?"]
}
```

### WebSocket `/ws/notifications/{user_id}`
ADHD-friendly real-time notifications and reminders

**Notification Events:**

**Gentle Reminder:**
```json
{
  "event": "gentle_reminder",
  "type": "task_due_soon",
  "message": "Your proposal is due in 2 hours. You're doing great!",
  "urgency": "medium",
  "adhd_optimized": {
    "tone": "encouraging",
    "dismissible": true,
    "snooze_options": [15, 30, 60]
  },
  "suggested_actions": [
    "Take a 5-minute break first",
    "Review your progress so far",
    "Set a focus timer"
  ]
}
```

**Achievement Notification:**
```json
{
  "event": "achievement_unlocked",
  "achievement_id": "focus_streak_5",
  "title": "Focus Champion",
  "description": "5 successful focus sessions this week!",
  "dopamine_boost": true,
  "celebration": {
    "visual": "confetti_animation",
    "sound": "gentle_chime",
    "duration": 3
  }
}
```

---

## 📈 API Summary

### Implementation Statistics
- **Total REST Endpoints:** 89
- **WebSocket Connections:** 5
- **ADHD-Specific Features:** 25 endpoints
- **AI-Powered Features:** 18 endpoints
- **OAuth Providers:** Google, Apple, Email/Password
- **Sqrily Integration:** 15 endpoints
- **Real-time Features:** Timer, notifications, collaboration

### Key Features
- **Complete OAuth Integration** with ADHD-friendly onboarding
- **Executive Function Support** with task breakdown and micro-tasks
- **Human-AI Collaboration** with interactive sessions and learning
- **Sqrily Integration** with quadrant-based planning
- **Real-time Features** via WebSocket connections
- **Privacy-First Design** with GDPR compliance and user control
- **Cross-Platform Support** for web, mobile, and desktop applications

### Authentication Requirements
- **Public Endpoints:** 8 (registration, login, OAuth callbacks)
- **Authenticated Endpoints:** 81 (require JWT token)
- **Admin Endpoints:** 0 (all user-focused)

### Data Formats
- **Request Format:** JSON with comprehensive validation
- **Response Format:** JSON with consistent error handling
- **WebSocket Format:** JSON events with real-time updates
- **File Upload:** Multipart form data support
- **Internationalization:** UTF-8 encoding throughout

This complete API specification provides everything needed to build a production-ready ADHD-friendly AI planner with full OAuth support, executive function assistance, and intelligent automation features. 