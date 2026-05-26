import asyncio
from database import jobs_collection

async def delete_jobs_by_locations(locations):
    query = {"region": {"$in": locations}}
    result = await jobs_collection.delete_many(query)
    print(f"🗑️ Deleted {result.deleted_count} job(s) from locations: {locations}")

if __name__ == "__main__":
    locations_to_delete = ["Delhi", "Bangalore", "Washington"]
    asyncio.run(delete_jobs_by_locations(locations_to_delete))
