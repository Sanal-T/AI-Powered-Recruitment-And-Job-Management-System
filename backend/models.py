# In backend/models.py

from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Any, Annotated
from datetime import datetime
from bson import ObjectId

# This new PyObjectId class is compatible with Pydantic V2
PyObjectId = Annotated[str, BeforeValidator(str)]

class Job(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    company: str
    location: str
    region: str
    description: Optional[str] = None
    posted_date: datetime
    url: str
    salary: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(BaseModel):
    username: str
    role: str # "admin" or "candidate"

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None