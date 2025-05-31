import sys
import os
import asyncio
from job_queries import QUERIES
from datetime import datetime
# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from external.jsearch_client import fetch_jobs_from_jsearch
from external.adzuna_client import fetch_jobs_from_adzuna
from database import jobs_collection

async def store_jobs(query, region):
    print(f"\n🔎 Fetching JSearch jobs for {query} in {region}")
    jobs = fetch_jobs_from_jsearch(query=query, location=region)
    await insert_new_jobs(jobs)

    print(f"\n🔎 Fetching Adzuna jobs for {query} in {region}")
    loop = asyncio.get_running_loop()
    jobs_adzuna = await loop.run_in_executor(None, fetch_jobs_from_adzuna, query, region)
    await insert_new_jobs(jobs_adzuna)


async def insert_new_jobs(jobs):
    today = datetime.utcnow().date()
    for job in jobs:
        # Upsert: update if exists, insert if not, and always set last_seen
        result = await jobs_collection.update_one(
            {"url": job["url"]},
            {"$set": {**job, "last_seen": today}},
            upsert=True
        )
        if result.upserted_id:
            print(f"✅ Stored: {job['title']} at {job['company']} ({job['source']})")
        elif result.modified_count > 0:
            print(f"🔄 Updated: {job['title']} at {job['company']} ({job['source']})")
        else:
            print(f"⚠️ Skipped (duplicate): {job['title']} ({job['source']})")

async def print_all_jobs(region=None):
    query = {}
    if region:
        query["region"] = region
    jobs = await jobs_collection.find(query).to_list(length=1000)
    print(f"\n🧾 Jobs in {region or 'All Regions'}:")
    for job in jobs:
        print(f"📌 {job['title']} at {job['company']} [{job['source']}]")

async def print_closed_jobs(region=None):
    today = datetime.utcnow().date()
    query = {"last_seen": {"$lt": today}}
    if region:
        query["region"] = region
    closed_jobs = await jobs_collection.find(query).to_list(length=1000)
    print(f"\n❌ Possibly closed jobs in {region or 'All Regions'}:")
    for job in closed_jobs:
        print(f"❌ {job['title']} at {job['company']} [{job['source']}]")

if __name__ == "__main__":
    async def main():
        for query in QUERIES:
            await store_jobs(query, "Thrissur")
        await print_all_jobs(region="Thrissur")
        await print_closed_jobs(region="Thrissur")
        for query in QUERIES:
            await store_jobs(query, "KOCHI")
        await print_all_jobs(region="KOCHI")
        await print_closed_jobs(region="KOCHI")

    asyncio.run(main())