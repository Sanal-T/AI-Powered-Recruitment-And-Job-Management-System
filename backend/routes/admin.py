# In backend/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend import auth, models
from backend.database import jobs_collection
from pydantic import ValidationError # <-- 1. ADDED THIS IMPORT

router = APIRouter()

# Dependency to protect admin routes (this remains the same)
async def get_current_admin_user(token: str = Depends(auth.oauth2_scheme)):
    # This is a placeholder for security. A real app would decode the token
    # and check if the user's role is "admin".
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"role": "admin"}


# 2. THIS ENTIRE FUNCTION HAS BEEN UPDATED
@router.get("/jobs", response_model=List[models.Job])
async def get_all_jobs_for_admin(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    This is the endpoint the frontend is trying to reach.
    It gets all jobs from the database and filters out any invalid ones.
    """
    query = {}
    if search:
        # Search for the term in either the title or description, case-insensitive
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    
    jobs_cursor = jobs_collection.find(query).limit(200)

    # --- Start of new resilient code ---
    valid_jobs = []
    async for job_data in jobs_cursor:
        try:
            # Try to validate each job individually against the Pydantic model
            job_model = models.Job(**job_data)
            valid_jobs.append(job_model)
        except ValidationError as e:
            # If a job from the DB is invalid, print an error to the backend console and skip it
            print(f"Skipping invalid job data with ID {job_data.get('_id')}: {e}")
            continue
    # --- End of new resilient code ---
    
    return valid_jobs


@router.get("/starred-jobs")
async def get_all_starred_jobs(current_user: dict = Depends(get_current_admin_user)):
    """
    This endpoint will now fetch the 2 most recent jobs and format them
    as if they were starred by a user.
    
    NOTE: This is a sample implementation. A real-world version would query a 
    separate 'starred_jobs' collection in the database.
    """
    
    # 1. Fetch the 2 most recent jobs from the database to use as samples.
    starred_jobs_cursor = jobs_collection.find({}).sort("posted_date", -1).limit(2)
    latest_jobs = await starred_jobs_cursor.to_list(length=2)

    # 2. Format the data into the structure the frontend expects.
    # The frontend expects a list of objects, where each object has a 'user' and a 'job'.
    formatted_starred_jobs = []
    for job in latest_jobs:
        try:
            # Validate the job data first
            job_model = models.Job(**job)
            formatted_starred_jobs.append({
                "user": "candidate", # Sample user who starred the job
                "job": job_model.dict(by_alias=True)
            })
        except Exception as e:
            print(f"Skipping starred job due to validation error: {e}")
            continue
            
    return formatted_starred_jobs
    return []