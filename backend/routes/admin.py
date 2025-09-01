# In backend/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend import auth, models
from backend.database import jobs_collection, starred_jobs_collection
from pydantic import ValidationError
from bson import ObjectId # <-- Make sure ObjectId is imported

router = APIRouter()

# Dependency to protect admin routes (this remains the same)
async def get_current_admin_user(token: str = Depends(auth.oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"role": "admin"}


@router.get("/jobs", response_model=List[models.Job])
async def get_all_jobs_for_admin(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    # This function remains the same
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    
    jobs_cursor = jobs_collection.find(query).limit(200)

    valid_jobs = []
    async for job_data in jobs_cursor:
        try:
            job_model = models.Job(**job_data)
            valid_jobs.append(job_model)
        except ValidationError as e:
            print(f"Skipping invalid job data with ID {job_data.get('_id')}: {e}")
            continue
    
    return valid_jobs

# In backend/routes/admin.py

# Use the new response_model we created
@router.get("/starred-jobs", response_model=List[models.StarredJobResponse])
async def get_all_starred_jobs(current_user: dict = Depends(get_current_admin_user)):
    """
    This endpoint now correctly fetches all starred jobs and validates the
    response against the StarredJobResponse model.
    """

    pipeline = [
        {
            "$addFields": {
                "job_object_id": { "$toObjectId": "$job_id" }
            }
        },
        {
            "$lookup": {
                "from": "jobs",
                "localField": "job_object_id",
                "foreignField": "_id",
                "as": "job_details"
            }
        },
        {
            "$unwind": "$job_details"
        },
        {
            "$project": {
                "_id": 0,
                "user": "$username",
                "job": "$job_details"
            }
        }
    ]

    starred_jobs_cursor = starred_jobs_collection.aggregate(pipeline)

    # --- FIX: Convert raw DB data to Pydantic models before returning ---
    results = await starred_jobs_cursor.to_list(length=None)
    validated_results = [models.StarredJobResponse(**res) for res in results]
    return validated_results

    starred_jobs_cursor = starred_jobs_collection.aggregate(pipeline)
    return await starred_jobs_cursor.to_list(length=None)