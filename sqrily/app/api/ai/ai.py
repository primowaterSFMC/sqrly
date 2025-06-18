"""
AI API endpoints for the Sqrly ADHD Planner.

This module provides AI-powered features including task analysis,
goal planning, collaboration sessions, and ADHD-specific support.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import structlog

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...services.ai_service import OpenAIService
from ...exceptions import AIServiceError, ValidationError

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_ai_status():
    """Get AI service status and availability."""
    return {
        "status": "available",
        "message": "AI services are ready to help with your ADHD planning needs!",
        "features": [
            "Task analysis and priority scoring",
            "Goal breakdown and planning",
            "Task decomposition for executive function support",
            "Overwhelm detection and management",
            "Interactive collaboration sessions"
        ]
    }


@router.post("/analyze-task")
async def analyze_task(
    task_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a task using AI for priority, complexity, and ADHD considerations.

    Provides Sqrily quadrant assignment, breakdown recommendations,
    and executive function support suggestions.
    """
    logger.info("AI task analysis requested", user_id=str(current_user.id))

    try:
        ai_service = OpenAIService()
        analysis = await ai_service.analyze_task_priority(task_data)

        if not analysis:
            raise AIServiceError("Task analysis failed")

        return {
            "analysis": analysis,
            "adhd_friendly_message": "Here's what I think about your task! Remember, this is just a suggestion - you know yourself best.",
            "suggestions": analysis.get("suggestions", []),
            "confidence": analysis.get("confidence", 0.5)
        }

    except Exception as e:
        logger.error("AI task analysis failed", error=str(e), user_id=str(current_user.id))
        raise AIServiceError("AI analysis temporarily unavailable")


@router.post("/analyze-goal")
async def analyze_goal(
    goal_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a goal using AI for strategic planning and ADHD considerations.

    Provides breakdown into phases, timeline suggestions,
    and overwhelm risk assessment.
    """
    logger.info("AI goal analysis requested", user_id=str(current_user.id))

    try:
        ai_service = OpenAIService()
        analysis = await ai_service.analyze_goal_comprehensive(goal_data)

        if not analysis:
            raise AIServiceError("Goal analysis failed")

        return {
            "analysis": analysis,
            "adhd_friendly_message": "I've looked at your goal and have some ideas! Take what works for you and leave the rest.",
            "breakdown": analysis.get("breakdown", []),
            "timeline": analysis.get("timeline", []),
            "adhd_considerations": analysis.get("adhd_tips", [])
        }

    except Exception as e:
        logger.error("AI goal analysis failed", error=str(e), user_id=str(current_user.id))
        raise AIServiceError("AI analysis temporarily unavailable")


@router.post("/break-down-task")
async def break_down_task(
    breakdown_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Break down a complex task into smaller, manageable subtasks.

    Especially helpful for ADHD users who struggle with task initiation
    and executive function challenges.
    """
    logger.info("AI task breakdown requested", user_id=str(current_user.id))

    try:
        ai_service = OpenAIService()
        breakdown = await ai_service.break_down_task(breakdown_request)

        if not breakdown:
            raise AIServiceError("Task breakdown failed")

        return {
            "breakdown": breakdown,
            "adhd_friendly_message": "I've broken this down into bite-sized pieces! Start with whichever feels easiest right now.",
            "subtasks": breakdown.get("subtasks", []),
            "reasoning": breakdown.get("reasoning", ""),
            "total_time": breakdown.get("total_time", 0),
            "tips": [
                "You don't have to do all of these today",
                "Pick the one that feels most doable right now",
                "Celebrate completing each small step!"
            ]
        }

    except Exception as e:
        logger.error("AI task breakdown failed", error=str(e), user_id=str(current_user.id))
        raise AIServiceError("AI breakdown temporarily unavailable")


@router.post("/collaboration")
async def ai_collaboration(
    session_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start an AI collaboration session for planning and problem-solving.

    Provides interactive support for ADHD-specific challenges like
    overwhelm, procrastination, and executive function difficulties.
    """
    logger.info("AI collaboration session requested", user_id=str(current_user.id))

    try:
        ai_service = OpenAIService()

        # Get user context for personalized responses
        user_context = {
            "user_id": str(current_user.id),
            "session_type": session_data.get("type", "general"),
            "current_challenge": session_data.get("challenge", ""),
            "user_input": session_data.get("message", ""),
            "context": session_data.get("context", {})
        }

        response = await ai_service.collaborate(user_context)

        if not response:
            raise AIServiceError("Collaboration session failed")

        return {
            "response": response,
            "session_id": response.get("session_id"),
            "suggestions": response.get("suggestions", []),
            "follow_up_questions": response.get("follow_up", []),
            "adhd_support": response.get("adhd_support", {}),
            "encouragement": "You're doing great by reaching out for help! That takes courage and self-awareness."
        }

    except Exception as e:
        logger.error("AI collaboration failed", error=str(e), user_id=str(current_user.id))
        raise AIServiceError("AI collaboration temporarily unavailable")


@router.post("/overwhelm-check")
async def overwhelm_check(
    check_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check for signs of overwhelm and provide ADHD-friendly support.

    Analyzes current task load, stress indicators, and provides
    personalized recommendations for managing overwhelm.
    """
    logger.info("Overwhelm check requested", user_id=str(current_user.id))

    try:
        ai_service = OpenAIService()

        # Prepare overwhelm assessment data
        assessment_data = {
            "current_tasks": check_data.get("current_tasks", []),
            "stress_level": check_data.get("stress_level", 5),
            "energy_level": check_data.get("energy_level", 5),
            "recent_completions": check_data.get("recent_completions", []),
            "user_feedback": check_data.get("feedback", ""),
            "time_of_day": check_data.get("time_of_day", ""),
            "user_context": check_data.get("context", {})
        }

        assessment = await ai_service.assess_overwhelm(assessment_data)

        if not assessment:
            # Provide fallback assessment
            assessment = {
                "overwhelm_level": "moderate",
                "recommendations": [
                    "Take a 5-minute break and do some deep breathing",
                    "Pick just one small task to focus on right now",
                    "Remember: You don't have to do everything today"
                ],
                "confidence": 0.3
            }

        return {
            "assessment": assessment,
            "overwhelm_level": assessment.get("overwhelm_level", "moderate"),
            "recommendations": assessment.get("recommendations", []),
            "immediate_actions": assessment.get("immediate_actions", []),
            "supportive_message": "It's okay to feel overwhelmed sometimes. You're not alone, and this feeling will pass.",
            "emergency_resources": {
                "breathing_exercise": "Try the 4-7-8 breathing technique",
                "grounding": "Name 5 things you can see, 4 you can touch, 3 you can hear",
                "self_compassion": "Talk to yourself like you would a good friend"
            }
        }

    except Exception as e:
        logger.error("Overwhelm check failed", error=str(e), user_id=str(current_user.id))
        # Always provide some support, even if AI fails
        return {
            "assessment": {"overwhelm_level": "unknown"},
            "recommendations": [
                "Take a moment to breathe deeply",
                "You're doing your best, and that's enough",
                "Consider taking a short break"
            ],
            "supportive_message": "I'm having trouble analyzing right now, but I want you to know that you're doing great.",
            "fallback": True
        }