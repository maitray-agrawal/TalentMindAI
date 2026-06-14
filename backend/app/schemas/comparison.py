from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class SkillData(BaseModel):
    name: str
    proficiency: str  # Expert, Intermediate, Beginner, Listed
    endorsements: int


class ExperienceData(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    duration_months: Optional[int] = None
    is_current: Optional[bool] = None
    industry: Optional[str] = None


class ExperienceInfo(BaseModel):
    years: float
    history: List[ExperienceData]
    level: str  # Entry Level, Mid Level, Senior, Principal


class EducationData(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    tier: Optional[str] = None


class VerifiedCredentials(BaseModel):
    email: bool
    phone: bool
    linkedin: bool


class BehavioralSignals(BaseModel):
    profile_completeness: float
    open_to_work: bool
    profile_views_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: Optional[float] = None
    connection_count: int
    endorsements_received: int
    notice_period_days: Optional[int] = None
    willing_to_relocate: bool
    github_activity_score: float
    interview_completion_rate: float
    offer_acceptance_rate: float
    verified_credentials: VerifiedCredentials


class RankingInfo(BaseModel):
    score: float
    tier: str
    explanation: Dict[str, Any]


class HiringRecommendation(BaseModel):
    level: str  # Strong Hire, Consider, Maybe, Pass
    confidence: float  # 0.0 to 1.0
    score: float
    reasoning: str
    key_strengths: List[str]
    key_concerns: List[str]


class CandidateComparisonData(BaseModel):
    id: int
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None
    experience: ExperienceInfo
    skills: List[SkillData]
    education: List[EducationData]
    behavioral_signals: BehavioralSignals
    ranking: RankingInfo
    recommendation: HiringRecommendation
    salary_expectation: Optional[int] = None


class ComparisonSummary(BaseModel):
    total_candidates: int
    highest_ranked: CandidateComparisonData
    average_experience_years: float
    average_ranking_score: float
    average_salary_expectation: float
    recommendation_distribution: Dict[str, int]
    best_experience: CandidateComparisonData
    best_ranking: CandidateComparisonData
    most_engaged: CandidateComparisonData


class CandidateComparisonResponse(BaseModel):
    candidates: List[CandidateComparisonData]
    summary: ComparisonSummary
