from fastapi import APIRouter, Query
from typing import List
from database import jobs_collection
from models import Job
import datetime

router = APIRouter()

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

