"""
Custom exceptions for the Sqrly ADHD Planner application.

This module provides ADHD-friendly error handling with supportive,
non-judgmental error messages that help users understand what went wrong
without causing additional stress or overwhelm.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class ADHDFriendlyException(HTTPException):
    """
    Base exception class for ADHD-friendly error handling.
    
    All custom exceptions inherit from this class to ensure consistent,
    supportive error messaging that doesn't blame the user or cause overwhelm.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        adhd_friendly_message: str,
        suggestions: Optional[list] = None,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.adhd_friendly_message = adhd_friendly_message
        self.suggestions = suggestions or []
        self.error_code = error_code or f"ERR_{uuid.uuid4().hex[:8].upper()}"
        self.timestamp = datetime.utcnow().isoformat()
        
        # Create detailed error response
        error_detail = {
            "error": detail,
            "message": adhd_friendly_message,
            "suggestions": self.suggestions,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "support_note": "Remember: This isn't your fault. Technology can be tricky sometimes!"
        }
        
        super().__init__(status_code=status_code, detail=error_detail, headers=headers)


# Authentication and Authorization Exceptions

class AuthenticationError(ADHDFriendlyException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            adhd_friendly_message="Looks like we need to verify who you are. No worries - this happens to everyone!",
            suggestions=[
                "Try logging in again",
                "Check if your password is correct",
                "Make sure you're using the right email address",
                "If you're still having trouble, try the 'Forgot Password' option"
            ],
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedError(ADHDFriendlyException):
    """User doesn't have permission for this action"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            adhd_friendly_message="You don't have permission to do that right now. This isn't a reflection on you!",
            suggestions=[
                "Check if you're logged into the right account",
                "Contact support if you think this is a mistake",
                "Try refreshing the page and logging in again"
            ]
        )


class TokenExpiredError(ADHDFriendlyException):
    """JWT token has expired"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            adhd_friendly_message="Your session has timed out. This is normal for security - just sign in again!",
            suggestions=[
                "Click the login button to sign in again",
                "Your data is safe and will be there when you get back",
                "Consider using 'Remember Me' next time for longer sessions"
            ]
        )


# Resource Not Found Exceptions

class TaskNotFoundError(ADHDFriendlyException):
    """Task not found"""
    def __init__(self, task_id: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
            adhd_friendly_message="We couldn't find that task. Don't worry - this happens sometimes!",
            suggestions=[
                "Double-check the task ID or link",
                "The task might have been moved or deleted",
                "Try searching for the task by name",
                "Check if you're looking in the right goal or project"
            ]
        )


class GoalNotFoundError(ADHDFriendlyException):
    """Goal not found"""
    def __init__(self, goal_id: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal not found: {goal_id}",
            adhd_friendly_message="We couldn't find that goal. No stress - let's figure this out together!",
            suggestions=[
                "Check if the goal ID or link is correct",
                "The goal might have been archived or deleted",
                "Try looking in your archived goals",
                "Search for the goal by name in your goal list"
            ]
        )


class UserNotFoundError(ADHDFriendlyException):
    """User not found"""
    def __init__(self, user_id: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
            adhd_friendly_message="We couldn't find that user account. This might be a technical hiccup!",
            suggestions=[
                "Check if the user ID is correct",
                "The account might have been deactivated",
                "Try refreshing the page",
                "Contact support if this keeps happening"
            ]
        )


# Validation Exceptions

class ValidationError(ADHDFriendlyException):
    """Input validation failed"""
    def __init__(self, detail: str, field: str = "", suggestions: list = None):
        default_suggestions = [
            "Double-check the information you entered",
            "Make sure all required fields are filled out",
            "Try using simpler, shorter text if the field seems too long",
            "Take a break and come back if you're feeling overwhelmed"
        ]
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            adhd_friendly_message=f"There's a small issue with the {field} field. No big deal - let's fix it together!",
            suggestions=suggestions or default_suggestions
        )


class DuplicateResourceError(ADHDFriendlyException):
    """Resource already exists"""
    def __init__(self, resource_type: str = "item", detail: str = ""):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            adhd_friendly_message=f"You already have a {resource_type} with that name. That's actually good organization!",
            suggestions=[
                f"Try a slightly different name for your {resource_type}",
                f"Check if you want to update the existing {resource_type} instead",
                "Add a number or date to make it unique",
                "Consider if this is actually what you were looking for"
            ]
        )


# Business Logic Exceptions

class OverwhelmDetectedError(ADHDFriendlyException):
    """User overwhelm detected"""
    def __init__(self, overwhelm_score: float = 0.0):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Overwhelm threshold exceeded",
            adhd_friendly_message="Hey, it looks like you might be taking on a lot right now. Let's pause and breathe!",
            suggestions=[
                "Take a 5-minute break and do some deep breathing",
                "Consider breaking down your current task into smaller pieces",
                "Maybe postpone some non-urgent items for later",
                "Remember: You don't have to do everything today",
                "Try the 'Overwhelm Helper' feature for personalized suggestions"
            ]
        )


class TaskTooComplexError(ADHDFriendlyException):
    """Task is too complex and should be broken down"""
    def __init__(self, task_title: str = ""):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task complexity exceeds recommended threshold",
            adhd_friendly_message=f"'{task_title}' looks like a big task! Let's break it down into smaller, manageable pieces.",
            suggestions=[
                "Use the 'Break Down Task' feature to split this into smaller tasks",
                "Think about the first small step you could take",
                "Consider what materials or information you need first",
                "Remember: Small progress is still progress!"
            ]
        )


class EnergyMismatchError(ADHDFriendlyException):
    """Task energy requirements don't match user's current energy"""
    def __init__(self, required_energy: int, current_energy: int):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Energy level mismatch",
            adhd_friendly_message=f"This task needs high energy, but you're running at {current_energy}/10 right now. That's totally normal!",
            suggestions=[
                "Try a lower-energy task first to build momentum",
                "Take a short break or do something energizing",
                "Save this task for when you're feeling more energetic",
                "Consider if there's a simpler version of this task you could do now"
            ]
        )


# AI Service Exceptions

class AIServiceError(ADHDFriendlyException):
    """AI service is unavailable or failed"""
    def __init__(self, detail: str = "AI service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            adhd_friendly_message="Our AI assistant is taking a little break right now. Don't worry - you can still use everything else!",
            suggestions=[
                "Try again in a few minutes",
                "You can still create and manage tasks manually",
                "The AI features will be back soon",
                "All your data is safe and saved"
            ]
        )


class AIAnalysisFailedError(ADHDFriendlyException):
    """AI analysis failed for a specific request"""
    def __init__(self, analysis_type: str = "analysis"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"AI {analysis_type} failed",
            adhd_friendly_message=f"The AI couldn't complete the {analysis_type} right now, but that's okay! You can still proceed manually.",
            suggestions=[
                "Try the analysis again with simpler language",
                "Break down your request into smaller parts",
                "Use the manual tools instead",
                "The AI will learn and get better over time"
            ]
        )


# Database and System Exceptions

class DatabaseError(ADHDFriendlyException):
    """Database operation failed"""
    def __init__(self, detail: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            adhd_friendly_message="We're having a small technical hiccup. This isn't your fault - our systems are just being a bit moody!",
            suggestions=[
                "Try again in a moment",
                "Your data is safe and backed up",
                "If this keeps happening, let us know",
                "Take a quick break while we sort this out"
            ]
        )


class RateLimitExceededError(ADHDFriendlyException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            adhd_friendly_message="Whoa there, speedy! You're moving fast today. Let's take a quick breather.",
            suggestions=[
                f"Wait about {retry_after} seconds and try again",
                "This helps keep the system running smoothly for everyone",
                "Use this time to review what you've already accomplished",
                "Maybe grab a drink or stretch while you wait"
            ],
            headers={"Retry-After": str(retry_after)}
        )


# Helper function to create ADHD-friendly error responses
def create_adhd_friendly_error(
    status_code: int,
    detail: str,
    friendly_message: str,
    suggestions: list = None,
    error_code: str = None
) -> ADHDFriendlyException:
    """
    Helper function to create ADHD-friendly error responses.
    
    Args:
        status_code: HTTP status code
        detail: Technical error detail
        friendly_message: ADHD-friendly message
        suggestions: List of helpful suggestions
        error_code: Optional error code for tracking
    
    Returns:
        ADHDFriendlyException instance
    """
    return ADHDFriendlyException(
        status_code=status_code,
        detail=detail,
        adhd_friendly_message=friendly_message,
        suggestions=suggestions or [],
        error_code=error_code
    )
