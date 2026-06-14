from pydantic import BaseModel
from typing import List, Optional

class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = "Remote"
    description: Optional[str] = None
    required_skills: Optional[List[str]] = []
    experience_required: Optional[float] = 0.0
    status: Optional[str] = "Active"
    priority: Optional[str] = "Medium"

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class JobInDB(JobBase):
    id: int

    model_config = {
        "from_attributes": True
    }
