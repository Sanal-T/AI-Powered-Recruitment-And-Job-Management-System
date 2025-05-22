import requests
from datetime import datetime

RAPIDAPI_KEY = "069d1b4de4msh7ebd7dead412e6cp14ce4djsn6af18c497cce"

RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

def fetch_jobs_from_jsearch(query="developer", location="Bangalore", page=1):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {
        "query": query,
        "location": location,
        "page": str(page)
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        jobs = []
        for item in response.json().get("data", []):
            job = {
                "title": item.get("job_title"),
                "company": item.get("employer_name"),
                "location": item.get("job_city"),
                "region": location,
                "description": item.get("job_description"),
                "posted_date": datetime.strptime(item.get("job_posted_at_datetime_utc"), "%Y-%m-%dT%H:%M:%S.%fZ"),
                "source": "jsearch",
                "url": item.get("job_apply_link")
            }
            jobs.append(job)
        return jobs
    else:
        print("JSearch error:", response.status_code, response.text)
        return []
