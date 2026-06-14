from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.schemas.candidate import CandidateInDB

class RankingInDB(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    match_score: float
    explanation: Dict[str, Any]
    tier: str

    model_config = {
        "from_attributes": True
    }

class RankingWithCandidate(RankingInDB):
    candidate: CandidateInDB

    model_config = {
        "from_attributes": True
    }

class SkillGapResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    job_id: int
    job_title: str
    match_score: float
    gained_skills: List[str]
    missing_skills: List[str]
    experience_gap_years: float
    upskilling_roadmap: List[Dict[str, Any]]

class RankingGenerateRequest(BaseModel):
    job_description: Optional[str] = None
    title: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[float] = None
    education_requirements: Optional[List[str]] = None
    work_preference: Optional[str] = None
    location: Optional[str] = None
    limit: Optional[int] = None

class CandidateRankResponse(BaseModel):
    candidate_id: int
    candidate_uuid: Optional[str] = None
    candidate_name: str
    score: float
    reasoning: str
    rank: int

