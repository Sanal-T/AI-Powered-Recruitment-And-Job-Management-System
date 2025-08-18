# In models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

# Helper to allow ObjectId in Pydantic models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Job(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    company: str
    location: str
    description: Optional[str]
    salary: Optional[str] = None # Add salary field
    url: str
    
    class Config:
        json_encoders = {ObjectId: str}

class User(BaseModel):
    username: str
    role: str # "admin" or "candidate"

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str