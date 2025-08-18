from fastapi import APIRouter, Query
from typing import List
from backend.database import jobs_collection
from backend.models import Job
# Assuming remotive_scraper is in a 'scraper' folder inside 'backend'
from backend.scraper.remotive_scraper import fetch_remotive_jobs
import datetime

router = APIRouter()

# 1. GET jobs from DB
@router.get("/", response_model=List[Job])
async def get_jobs(
    region: str = Query(None),
    sort_by: str = "posted_date",
    order: str = "desc",
    limit: int = 20
):
    query = {}
    if region:
        query["region"] = region

    sort_order = -1 if order == "desc" else 1

    jobs_cursor = jobs_collection.find(query).sort(sort_by, sort_order).limit(limit)
    jobs = await jobs_cursor.to_list(length=limit)
    return jobs

# 2. REFRESH jobs from Remotive and save to DB
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

        # Avoid duplicates by URL or title+company
        if not await jobs_collection.find_one({"url": job_doc["url"]}):
            await jobs_collection.insert_one(job_doc)
            inserted_count += 1

    return {"status": "success", "inserted": inserted_count}
