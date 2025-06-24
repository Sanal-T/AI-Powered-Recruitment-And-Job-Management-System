from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from scripts.fetch_all_jobs import store_jobs
from scripts.job_queries import QUERIES
from routes import jobs

FETCH_INTERVAL_HOURS = 3  # Set your desired fetch interval here

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def periodic_fetch():
        while True:
            print("\n🔄 Starting job fetch cycle...")
            for query in QUERIES:
                await store_jobs(query, "Thrissur")
                await store_jobs(query, "KOCHI")
            print("✅ Completed cycle. Sleeping...\n")
            await asyncio.sleep(FETCH_INTERVAL_HOURS * 60 * 60)  # e.g., 3 hours

    task = asyncio.create_task(periodic_fetch())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# Optional CORS config (for future frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs")
