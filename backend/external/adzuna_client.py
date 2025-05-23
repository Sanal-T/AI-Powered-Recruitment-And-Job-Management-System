import requests
from datetime import datetime

ADZUNA_APP_ID = "4f48fc15"
ADZUNA_APP_KEY = "209c64876108b7c26edec1509944fed3"

def fetch_jobs_from_adzuna(query="developer", location="Bangalore", results=20):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": query,
        "where": location,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        jobs = []
        for item in data.get("results", []):
            job = {
                "title": item.get("title"),
                "company": item.get("company", {}).get("display_name"),
                "location": item.get("location", {}).get("display_name"),
                "region": location,
                "description": item.get("description"),
                "posted_date": datetime.strptime(item["created"], "%Y-%m-%dT%H:%M:%SZ"),
                "source": "adzuna",
                "url": item.get("redirect_url")
            }
            jobs.append(job)
        return jobs
    else:
        print("Adzuna error:", response.status_code, response.text)
        return []
