from pydantic import BaseModel
from typing import List

class CandidateExplanationResponse(BaseModel):
    candidate_id: int
    job_id: int
    match_score: float
    tier: str
    why_matched: str
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    hiring_recommendation: str

    model_config = {
        "from_attributes": True
    }
