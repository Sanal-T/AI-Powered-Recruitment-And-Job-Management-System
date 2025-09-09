import sys
import os
import asyncio
import datetime

# This allows the script to import from the parent 'backend' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from job_queries import QUERIES
from external.jsearch_client import fetch_jobs_from_jsearch
from external.adzuna_client import fetch_jobs_from_adzuna
from database import jobs_collection

async def store_jobs(query, region):
    """Fetches jobs from JSearch and Adzuna for a given query and region."""
    print(f"\n🔎 Fetching JSearch jobs for {query} in {region}")
    jobs_jsearch_raw = fetch_jobs_from_jsearch(query=query, location=region)
    jobs_jsearch = [standardize_job(job, region, "JSearch") for job in jobs_jsearch_raw]
    await insert_new_jobs(jobs_jsearch)

    print(f"\n🔎 Fetching Adzuna jobs for {query} in {region}")
    loop = asyncio.get_running_loop()
    jobs_adzuna_raw = await loop.run_in_executor(None, fetch_jobs_from_adzuna, query, region)
    jobs_adzuna = [standardize_job(job, region, "Adzuna") for job in jobs_adzuna_raw]
    await insert_new_jobs(jobs_adzuna)

def standardize_job(job, region, source):
    """Converts a job from an API into our standard database format."""
    return {
        "title": job.get("title", "No title"),
        "company": job.get("company", "Unknown"),
        "location": job.get("location", "Unknown"),
        "description": job.get("description", ""),
        "url": job.get("url", ""),
        "region": region,
        "source": source,
        "posted_date": job.get("posted_date", datetime.datetime.utcnow()),
        "salary": job.get("salary")
    }

async def insert_new_jobs(jobs):
    """Inserts a list of jobs into the database, avoiding duplicates."""
    for job in jobs:
        if not job.get("url"):
            print(f"❌ Skipped job with missing URL")
            continue

        exists = await jobs_collection.find_one({"url": job["url"]})
        if not exists:
            await jobs_collection.insert_one(job)
            print(f"✅ Stored: {job.get('title')} at {job.get('company')} ({job.get('source')})")
        else:
            print(f"⚠️ Skipped (duplicate): {job.get('title')} ({job.get('source')})")

async def print_all_jobs(region=None):
    """Prints a summary of jobs in the database for a given region."""
    query = {}
    if region:
        query["region"] = region
    jobs = await jobs_collection.find(query).to_list(length=1000)
    print(f"\n🧾 Jobs in {region or 'All Regions'}:")
    for job in jobs:
        print(f"📌 {job.get('title')} at {job.get('company')} [{job.get('source')}]")

if __name__ == "__main__":
    # --- Define all the locations you want to fetch here ---
    LOCATIONS_TO_FETCH = ["Thrissur", "Kochi", "Ernakulam"]

    async def main():
        for location in LOCATIONS_TO_FETCH:
            print(f"\n=================================================")
            print(f"   STARTING FETCH FOR LOCATION: {location.upper()}   ")
            print(f"=================================================\n")
            for query in QUERIES:
                await store_jobs(query, location)
            await print_all_jobs(region=location)

    asyncio.run(main())