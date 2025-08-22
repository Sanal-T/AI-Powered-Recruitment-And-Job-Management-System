# In backend/scripts/clear_db.py
import asyncio
import sys
import os

# This allows the script to import from the parent 'backend' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import jobs_collection

async def clear_jobs():
    print("Connecting to the database...")
    count = await jobs_collection.count_documents({})
    if count > 0:
        print(f"Found {count} jobs. Deleting all of them...")
        result = await jobs_collection.delete_many({})
        print(f"✅ Successfully deleted {result.deleted_count} jobs.")
    else:
        print("✅ No jobs found in the collection. Nothing to delete.")

if __name__ == "__main__":
    asyncio.run(clear_jobs())