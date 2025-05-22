import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from external.jsearch_client import fetch_jobs_from_jsearch
from database import client

db = client.job_database
jobs_collection = db.jobs

def store_jobs(query, region):
    jobs = fetch_jobs_from_jsearch(query=query, location=region)
    for job in jobs:
        if not jobs_collection.find_one({"url": job["url"]}):
            jobs_collection.insert_one(job)
            print(f"✅ Stored: {job['title']} at {job['company']}")

if __name__ == "__main__":
    store_jobs("flutter developer", "Delhi")
