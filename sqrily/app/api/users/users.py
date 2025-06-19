from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...schemas.auth import UserResponse
from ...schemas.user import UserUpdate, ADHDProfileUpdate

logger = structlog.get_logger()
router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    logger.info("Getting user profile", user_id=str(current_user.id))

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        avatar_url=current_user.avatar_url,
        provider=current_user.provider.value,
        onboarding_completed=current_user.onboarding_completed,
        subscription_tier=current_user.subscription_tier.value,
        adhd_preferences=current_user.adhd_profile,
        created_at=current_user.created_at
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    logger.info("Updating user profile", user_id=str(current_user.id))

    # Update basic profile fields
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    if user_data.timezone is not None:
        current_user.timezone = user_data.timezone
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        avatar_url=current_user.avatar_url,
        provider=current_user.provider.value,
        onboarding_completed=current_user.onboarding_completed,
        subscription_tier=current_user.subscription_tier.value,
        adhd_preferences=current_user.adhd_profile,
        created_at=current_user.created_at
    )

@router.get("/me/adhd-profile")
async def get_adhd_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user's ADHD profile"""
    logger.info("Getting ADHD profile", user_id=str(current_user.id))

    return {
        "adhd_profile": current_user.adhd_profile or {},
        "onboarding_completed": current_user.onboarding_completed
    }

@router.put("/me/adhd-profile")
async def update_adhd_profile(
    profile_data: ADHDProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's ADHD profile"""
    logger.info("Updating ADHD profile", user_id=str(current_user.id))

    # Update ADHD profile
    current_user.update_adhd_profile(profile_data.dict(exclude_unset=True))

    # Mark onboarding as completed if not already
    if not current_user.onboarding_completed:
        current_user.onboarding_completed = True

    db.commit()
    db.refresh(current_user)

    return {
        "message": "ADHD profile updated successfully",
        "adhd_profile": current_user.adhd_profile,
        "onboarding_completed": current_user.onboarding_completed
    }

@router.post("/me/onboarding")
async def complete_onboarding_step(
    step_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an onboarding step"""
    logger.info("Completing onboarding step", user_id=str(current_user.id), step=step_data.get("step"))

    step = step_data.get("step")
    if not step:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step is required"
        )

    # Update onboarding step
    current_user.onboarding_step = step

    # If this is the final step, mark onboarding as completed
    final_steps = ["ai_collaboration_setup", "task_preferences"]
    if step in final_steps:
        current_user.onboarding_completed = True

    db.commit()
    db.refresh(current_user)

    return {
        "message": f"Onboarding step '{step}' completed",
        "current_step": current_user.onboarding_step,
        "onboarding_completed": current_user.onboarding_completed
    }