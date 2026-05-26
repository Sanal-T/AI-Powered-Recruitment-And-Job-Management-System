from fastapi import FastAPI, BackgroundTasks
from database import jobs_collection
from scripts.job_queries import QUERIES
from scripts.fetch_all_jobs import store_jobs, print_all_jobs
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import jobs 

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def periodic_fetch():
        POPULAR_QUERIES = [
            "Software Engineer",
            "Data Analyst",
            "Full Stack Developer",
            "Graphic Designer",
            "Marketing Executive",
            "Accountant",
            "DevOps Engineer",
            "Product Manager"
        ]
        # Delay initial run slightly to let dev server spin up cleanly
        await asyncio.sleep(10)
        while True:
            print("🚀 Starting background job fetching for curated popular terms...")
            for query in POPULAR_QUERIES:
                try:
                    await store_jobs(query, "Thrissur")
                    await asyncio.sleep(5)  # Rest between regions/queries
                    await store_jobs(query, "KOCHI")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"Error in background fetch for query '{query}': {e}")
            print("😴 Background job fetching complete. Sleeping for 12 hours.")
            await asyncio.sleep(12 * 60 * 60)  # 12 hours
    task = asyncio.create_task(periodic_fetch())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs")
@app.get("/jobs")
async def get_jobs(region: str = None):
    query = {}
    if region:
        query["region"] = region
    jobs = await jobs_collection.find(query).to_list(length=1000)
    return jobs