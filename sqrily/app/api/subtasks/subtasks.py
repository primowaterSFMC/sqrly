from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_subtasks():
    """Placeholder endpoint for subtasks functionality."""
    return {"message": "Subtasks API - Implementation coming soon"}


@router.post("/")
async def create_subtask():
    """Placeholder endpoint for creating subtasks."""
    return {"message": "Create subtask - Implementation coming soon"}


@router.get("/{subtask_id}")
async def get_subtask(subtask_id: int):
    """Placeholder endpoint for getting a specific subtask."""
    return {"message": f"Get subtask {subtask_id} - Implementation coming soon"}


@router.put("/{subtask_id}")
async def update_subtask(subtask_id: int):
    """Placeholder endpoint for updating a subtask."""
    return {"message": f"Update subtask {subtask_id} - Implementation coming soon"}


@router.delete("/{subtask_id}")
async def delete_subtask(subtask_id: int):
    """Placeholder endpoint for deleting a subtask."""
    return {"message": f"Delete subtask {subtask_id} - Implementation coming soon"}