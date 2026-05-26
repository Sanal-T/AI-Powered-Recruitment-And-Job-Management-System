# In backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

# CORRECTED IMPORTS
from backend.scripts.fetch_all_jobs import store_jobs
from backend.scripts.job_queries import QUERIES
from backend.routes import jobs, users, admin # <-- Make sure 'admin' is imported
from backend.routes import jobs, users, admin, candidate # <-- Add 'candidate' here

FETCH_INTERVAL_HOURS = 3

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

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",  # Add this for Live Server
    "http://127.0.0.1:5500",   # And this one to be safe
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the specific list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We are now including the admin router.
app.include_router(users.router, tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"]) # <-- This line is now active
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"]) 

# The candidate router remains commented out until we build it.
# app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])