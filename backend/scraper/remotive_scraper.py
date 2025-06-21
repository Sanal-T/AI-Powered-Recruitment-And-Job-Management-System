# backend/scraper/remotive_scraper.py

import requests

def fetch_remotive_jobs(search_term="developer"):
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": search_term}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
        return jobs
    except Exception as e:
        print(f"Error fetching Remotive jobs: {e}")
        return []
