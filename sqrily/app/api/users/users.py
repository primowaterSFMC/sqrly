from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_users():
    return {"message": "Users endpoint - will be implemented"}

@router.get("/me")
async def get_current_user():
    return {"message": "Current user endpoint - will be implemented"}