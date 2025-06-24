from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.job_database
jobs_collection = db.jobs

import asyncio

async def insert_test():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.job_database
    result = await db.jobs.insert_one({"test": "value"})
    print("Inserted:", result.inserted_id)

