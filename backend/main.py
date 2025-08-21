# In backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

# CORRECTED IMPORTS
from backend.scripts.fetch_all_jobs import store_jobs
from backend.scripts.job_queries import QUERIES
from backend.routes import jobs, users, admin # <-- Make sure 'admin' is imported

FETCH_INTERVAL_HOURS = 3

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def periodic_fetch():
        while True:
            print("\n🔄 Starting job fetch cycle...")
            # This line is commented out to prevent errors if the script has issues
            # await store_jobs("developer", "Thrissur")
            print("✅ Completed cycle. Sleeping...\n")
            await asyncio.sleep(FETCH_INTERVAL_HOURS * 60 * 60)

    task = asyncio.create_task(periodic_fetch())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We are now including the admin router.
app.include_router(users.router, tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"]) # <-- This line is now active
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
# The candidate router remains commented out until we build it.
# app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])