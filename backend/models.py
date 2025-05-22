from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Job(BaseModel):
    title: str
    company: str
    location: str
    region: str
    description: Optional[str]
    posted_date: datetime
    url: str
