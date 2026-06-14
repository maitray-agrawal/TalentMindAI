from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict

class ProfileModel(BaseModel):
    anonymized_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[float] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    current_company_size: Optional[str] = None
    current_industry: Optional[str] = None

class CareerHistoryModel(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    is_current: Optional[bool] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None

class EducationModel(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None
    tier: Optional[str] = "unknown"

class SkillModel(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None
    endorsements: Optional[int] = None
    duration_months: Optional[int] = None

class CertificationModel(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None

class LanguageModel(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str] = None

class ExpectedSalaryRangeInrLpa(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

class RedrobSignalsModel(BaseModel):
    profile_completeness_score: Optional[float] = None
    signup_date: Optional[str] = None
    last_active_date: Optional[str] = None
    open_to_work_flag: Optional[bool] = None
    profile_views_received_30d: Optional[int] = None
    applications_submitted_30d: Optional[int] = None
    recruiter_response_rate: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    skill_assessment_scores: Optional[Dict[str, float]] = None
    connection_count: Optional[int] = None
    endorsements_received: Optional[int] = None
    notice_period_days: Optional[int] = None
    expected_salary_range_inr_lpa: Optional[ExpectedSalaryRangeInrLpa] = None
    preferred_work_mode: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    github_activity_score: Optional[float] = None
    search_appearance_30d: Optional[int] = None
    saved_by_recruiters_30d: Optional[int] = None
    interview_completion_rate: Optional[float] = None
    offer_acceptance_rate: Optional[float] = None
    verified_email: Optional[bool] = None
    verified_phone: Optional[bool] = None
    linkedin_connected: Optional[bool] = None

class CandidateBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = "Remote"
    experience_years: Optional[float] = 0.0
    skills: Optional[List[str]] = []
    resume_text: Optional[str] = None
    status: Optional[str] = "Sourcing"
    salary_expectation: Optional[int] = None
    avatar_url: Optional[str] = None

    # Redrob nested fields
    candidate_id: Optional[str] = None
    profile: Optional[ProfileModel] = None
    career_history: Optional[List[CareerHistoryModel]] = []
    education: Optional[List[EducationModel]] = []
    certifications: Optional[List[CertificationModel]] = []
    languages: Optional[List[LanguageModel]] = []
    redrob_signals: Optional[RedrobSignalsModel] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = None
    resume_text: Optional[str] = None
    status: Optional[str] = None
    salary_expectation: Optional[int] = None
    avatar_url: Optional[str] = None

    candidate_id: Optional[str] = None
    profile: Optional[ProfileModel] = None
    career_history: Optional[List[CareerHistoryModel]] = []
    education: Optional[List[EducationModel]] = []
    certifications: Optional[List[CertificationModel]] = []
    languages: Optional[List[LanguageModel]] = []
    redrob_signals: Optional[RedrobSignalsModel] = None

class CandidateInDB(CandidateBase):
    id: int

    model_config = {
        "from_attributes": True
    }

