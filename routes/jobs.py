from fastapi import APIRouter, Query
from typing import List
from database import jobs_collection
from models import Job
import datetime

router = APIRouter()

@router.get("/", response_model=List[Job])
async def get_jobs(region: str = Query(None)):
    query = {}
    if region:
        query["region"] = region
    jobs = await jobs_collection.find(query).to_list(100)
    return jobs
