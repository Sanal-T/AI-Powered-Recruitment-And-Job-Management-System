# In backend/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend import auth, models
from backend.database import jobs_collection, db
from bson import ObjectId

router = APIRouter()

# Dependency to protect admin routes
async def get_current_admin_user(token: str = Depends(auth.oauth2_scheme)):
    # This is a placeholder for security. A real app would decode the token
    # and check if the user's role is "admin".
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"role": "admin"}

@router.get("/jobs", response_model=List[models.Job])
async def get_all_jobs_for_admin(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    This is the endpoint the frontend is trying to reach.
    It gets all jobs from the database.
    """
    query = {}
    if search:
        # Search for the term in either the title or description, case-insensitive
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    
    jobs_cursor = jobs_collection.find(query).limit(200)
    jobs = await jobs_cursor.to_list(length=200)
    return jobs

@router.get("/starred-jobs")
async def get_all_starred_jobs(current_user: dict = Depends(get_current_admin_user)):
    """
    This endpoint will return an empty list for now, so the frontend doesn't crash.
    We can build the full logic for this later.
    """
    return []

