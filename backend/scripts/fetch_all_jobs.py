import sys
import os
import asyncio

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
    for job in jobs:
        exists = await jobs_collection.find_one({"url": job["url"]})
        if not exists:
            await jobs_collection.insert_one(job)
            print(f"✅ Stored: {job['title']} at {job['company']} ({job['source']})")
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

if __name__ == "__main__":
    async def main():
        await store_jobs("flutter developer", "Delhi")
        await print_all_jobs(region="Delhi")
    asyncio.run(main())
