import sys
import os
import asyncio
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from job_queries import QUERIES
from external.jsearch_client import fetch_jobs_from_jsearch
from external.adzuna_client import fetch_jobs_from_adzuna
from scraper.remotive_scraper import fetch_remotive_jobs
from database import jobs_collection

async def store_jobs(query, region):
    print(f"\n🔎 Fetching JSearch jobs for {query} in {region}")
    jobs_jsearch = fetch_jobs_from_jsearch(query=query, location=region)
    jobs_jsearch = [standardize_job(job, region, "JSearch") for job in jobs_jsearch]
    await insert_new_jobs(jobs_jsearch)

    print(f"\n🔎 Fetching Adzuna jobs for {query} in {region}")
    loop = asyncio.get_running_loop()
    jobs_adzuna_raw = await loop.run_in_executor(None, fetch_jobs_from_adzuna, query, region)
    jobs_adzuna = [standardize_job(job, region, "Adzuna") for job in jobs_adzuna_raw]
    await insert_new_jobs(jobs_adzuna)

    print(f"\n🔎 Fetching Remotive jobs for {query}")
    jobs_remotive_raw = fetch_remotive_jobs(search_term=query)
    jobs_remotive = [standardize_job_from_remotive(job, region) for job in jobs_remotive_raw]
    await insert_new_jobs(jobs_remotive)

def standardize_job(job, region, source):
    return {
        "title": job.get("title", "No title"),
        "company": job.get("company", "Unknown"),
        "location": job.get("location", "Unknown"),
        "description": job.get("description", ""),
        "url": job.get("url", ""),
        "tags": job.get("tags", []),
        "job_type": job.get("job_type", "Unknown"),
        "region": region,
        #"source": source,
        "posted_date": job.get("posted_date", datetime.datetime.utcnow())
    }

def standardize_job_from_remotive(job, region):
    try:
        posted_date = datetime.datetime.strptime(
            job.get("publication_date", "2000-01-01T00:00:00"),
            "%Y-%m-%dT%H:%M:%S"
        )
    except Exception:
        posted_date = datetime.datetime.utcnow()

    return {
        "title": job.get("title", "No title"),
        "company": job.get("company_name", "Unknown"),
        "location": job.get("candidate_required_location", "Remote"),
        "description": job.get("description", ""),
        "url": job.get("url", ""),
        "tags": job.get("tags", []),
        "job_type": job.get("job_type", "Unknown"),
        "region": region,
        "posted_date": posted_date
    }

async def insert_new_jobs(jobs):
    for job in jobs:
        if not job.get("url"):
            print(f"❌ Skipped job with missing URL")
            continue

        exists = await jobs_collection.find_one({"url": job["url"]})
        if not exists:
            await jobs_collection.insert_one(job)
            print(f"✅ Stored: {job.get('title', 'No title')} at {job.get('company', 'Unknown')} ({job.get('source', 'Unknown')})")
        else:
            print(f"⚠️ Skipped (duplicate): {job.get('title', 'No title')} ({job.get('source', 'Unknown')})")

async def print_all_jobs(region=None):
    query = {}
    if region:
        query["region"] = region
    jobs = await jobs_collection.find(query).to_list(length=1000)
    print(f"\n🧾 Jobs in {region or 'All Regions'}:")
    for job in jobs:
        print(f"📌 {job.get('title', 'No title')} at {job.get('company', 'Unknown')} [{job.get('source', 'Unknown')}]")

if __name__ == "__main__":
    async def main():
        for query in QUERIES:
            await store_jobs(query, "Thrissur")
        await print_all_jobs(region="Thrissur")

        for query in QUERIES:
            await store_jobs(query, "KOCHI")
        await print_all_jobs(region="KOCHI")

    asyncio.run(main())
