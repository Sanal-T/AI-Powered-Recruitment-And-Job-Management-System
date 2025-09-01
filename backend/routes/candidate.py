# In backend/routes/candidate.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId

from backend import auth, models
from backend.database import jobs_collection, starred_jobs_collection

router = APIRouter()

# Dependency to get the current logged-in user from a token
async def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except auth.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 1. Endpoint to STAR a job
@router.post("/starred-jobs", status_code=status.HTTP_201_CREATED)
async def star_a_job(star_request: models.StarRequest, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    job_id = star_request.job_id

    # Check if the job exists
    job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already starred
    already_starred = await starred_jobs_collection.find_one({"username": username, "job_id": job_id})
    if already_starred:
        return {"status": "already starred"}

    await starred_jobs_collection.insert_one({"username": username, "job_id": job_id})
    return {"status": "success", "job_id": job_id}

# 2. Endpoint to GET all starred jobs for the user
@router.get("/starred-jobs", response_model=List[models.Job])
async def get_starred_jobs(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]

    # Find all job_ids the user has starred
    starred_entries = await starred_jobs_collection.find({"username": username}).to_list(length=None)
    job_ids = [ObjectId(entry["job_id"]) for entry in starred_entries]

    if not job_ids:
        return []

    # Fetch the full job details for those IDs
    jobs_cursor = jobs_collection.find({"_id": {"$in": job_ids}})
    return await jobs_cursor.to_list(length=None)

# 3. Endpoint to UNSTAR a job
@router.delete("/starred-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unstar_a_job(job_id: str, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]

    result = await starred_jobs_collection.delete_one({"username": username, "job_id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Starred job not found")

    return