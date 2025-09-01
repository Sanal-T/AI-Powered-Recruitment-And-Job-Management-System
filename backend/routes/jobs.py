from fastapi import APIRouter, Query
from typing import List, Optional
from backend.database import jobs_collection
from backend.models import Job
from pydantic import ValidationError
# Assuming remotive_scraper is in a 'scraper' folder inside 'backend'
from backend.scraper.remotive_scraper import fetch_remotive_jobs
import datetime

router = APIRouter()

# 1. GET jobs from DB (NOW WITH SEARCH FUNCTIONALITY)
@router.get("/", response_model=List[Job])
async def get_jobs(
    region: Optional[str] = Query(None),
    sort_by: str = "posted_date",
    order: str = "desc",
    limit: int = 50,
    search: Optional[str] = None # <-- ADDED search parameter
):
    query = {}
    if region:
        query["region"] = region
    
    # --- START: ADDED SEARCH LOGIC ---
    if search:
        # Search for the term in either the title or description, case-insensitive
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    # --- END: ADDED SEARCH LOGIC ---

    sort_order = -1 if order == "desc" else 1

    jobs_cursor = jobs_collection.find(query).sort(sort_by, sort_order).limit(limit)
    
    # Use resilient validation logic to skip bad data
    valid_jobs = []
    async for job_data in jobs_cursor:
        try:
            job_model = Job(**job_data)
            valid_jobs.append(job_model)
        except ValidationError as e:
            print(f"Skipping invalid job data with ID {job_data.get('_id')}: {e}")
            continue
            
    return valid_jobs

# 2. REFRESH jobs from Remotive and save to DB (kept your existing function)
@router.get("/refresh/remotive")
async def refresh_remotive_jobs(search: str = "developer"):
    jobs = fetch_remotive_jobs(search)

    inserted_count = 0
    for job in jobs:
        job_doc = {
            "title": job["title"],
            "company": job["company_name"],
            "location": job["candidate_required_location"],
            "description": job["description"],
            "url": job["url"],
            "tags": job["tags"],
            "job_type": job["job_type"],
            "region": job["candidate_required_location"],
            "posted_date": datetime.datetime.strptime(job["publication_date"], "%Y-%m-%dT%H:%M:%S"),
            "source": "Remotive"
        }

        # Avoid duplicates by URL
        if not await jobs_collection.find_one({"url": job_doc["url"]}):
            await jobs_collection.insert_one(job_doc)
            inserted_count += 1

    return {"status": "success", "inserted": inserted_count}