import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from external.jsearch_client import fetch_jobs_from_jsearch
from database import jobs_collection

async def store_jobs(query, region):
    jobs = fetch_jobs_from_jsearch(query=query, location=region)
    for job in jobs:
        # Use await for async Motor operations
        exists = await jobs_collection.find_one({"url": job["url"]})
        if not exists:
            await jobs_collection.insert_one(job)
            print(f"✅ Stored: {job['title']} at {job['company']}")

async def print_all_jobs():
    jobs = await jobs_collection.find().to_list(length=1000)
    for job in jobs:
        print(job)

if __name__ == "__main__":
    async def main():
        await store_jobs("flutter developer", "Delhi")
        await print_all_jobs()
    asyncio.run(main())