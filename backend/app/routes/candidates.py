from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from collections import Counter
from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateInDB
from app.schemas.explanation import CandidateExplanationResponse
from app.schemas.comparison import CandidateComparisonResponse
from app.services.ingestion import IngestionService
from app.services.ranker_service import RankerService
from app.services.comparison_service import ComparisonService


router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/import", status_code=status.HTTP_200_OK)
def import_candidates(
    file_path: Optional[str] = None,
    limit: Optional[int] = None,
    batch_size: int = 1000,
    db: Session = Depends(get_db)
):
    if not file_path:
        file_path = "d:\\TalentMindAI\\dataset\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\candidates.jsonl"
    try:
        result = IngestionService.ingest_candidates(db, file_path, limit, batch_size)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_candidate_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Candidate.id)).scalar() or 0
    if total == 0:
        return {
            "total_candidates": 0,
            "average_experience": 0.0,
            "experience_distribution": {},
            "work_preference_distribution": {},
            "top_skills": [],
            "open_to_work_count": 0,
            "open_to_work_percentage": 0.0,
            "average_profile_completeness": 0.0
        }

    # Experience
    avg_exp = db.query(func.avg(Candidate.experience_years)).scalar() or 0.0
    
    # Experience ranges
    entry = db.query(func.count(Candidate.id)).filter(Candidate.experience_years < 3.0).scalar() or 0
    mid = db.query(func.count(Candidate.id)).filter((Candidate.experience_years >= 3.0) & (Candidate.experience_years < 7.0)).scalar() or 0
    senior = db.query(func.count(Candidate.id)).filter((Candidate.experience_years >= 7.0) & (Candidate.experience_years < 12.0)).scalar() or 0
    principal = db.query(func.count(Candidate.id)).filter(Candidate.experience_years >= 12.0).scalar() or 0

    # Work Preference
    pref_counts = db.query(Candidate.work_preference, func.count(Candidate.id)).group_by(Candidate.work_preference).all()
    work_pref_dist = {pref or "Unknown": count for pref, count in pref_counts}

    # Open to work
    open_to_work_count = db.query(func.count(Candidate.id)).filter(func.json_extract(Candidate.redrob_signals, '$.open_to_work_flag') == 1).scalar() or 0
    open_to_work_pct = (open_to_work_count / total) * 100

    # Avg Profile Completeness
    avg_completeness = db.query(func.avg(func.json_extract(Candidate.redrob_signals, '$.profile_completeness_score'))).scalar() or 0.0

    # Top Skills (computed from all candidates in DB, limited to first 10000 to keep fast, or full if small)
    # Since we can query skills column
    skills_query = db.query(Candidate.skills).all()
    all_skills = []
    for (skills_list,) in skills_query:
        if skills_list:
            all_skills.extend(skills_list)
    top_skills_counted = Counter(all_skills).most_common(10)
    top_skills = [{"skill": s, "count": c} for s, c in top_skills_counted]

    return {
        "total_candidates": total,
        "average_experience": round(avg_exp, 2),
        "experience_distribution": {
            "Entry (<3 Yrs)": entry,
            "Mid (3-7 Yrs)": mid,
            "Senior (7-12 Yrs)": senior,
            "Principal (12+ Yrs)": principal
        },
        "work_preference_distribution": work_pref_dist,
        "top_skills": top_skills,
        "open_to_work_count": open_to_work_count,
        "open_to_work_percentage": round(open_to_work_pct, 2),
        "average_profile_completeness": round(avg_completeness, 2)
    }

@router.get("/search", response_model=List[CandidateInDB])
def search_candidates(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    work_preference: Optional[str] = None,
    open_to_work: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    
    if q:
        query = query.filter(
            (Candidate.name.ilike(f"%{q}%")) | 
            (Candidate.title.ilike(f"%{q}%")) |
            (Candidate.resume_text.ilike(f"%{q}%"))
        )
    if location:
        query = query.filter(func.json_extract(Candidate.profile, '$.location').ilike(f"%{location}%"))
    if min_experience:
        query = query.filter(Candidate.experience_years >= min_experience)
    if max_experience:
        query = query.filter(Candidate.experience_years <= max_experience)
    if work_preference:
        query = query.filter(Candidate.work_preference.ilike(work_preference))
    if open_to_work is not None:
        flag_val = 1 if open_to_work else 0
        query = query.filter(func.json_extract(Candidate.redrob_signals, '$.open_to_work_flag') == flag_val)
        
    if skill:
        for s in skill.split(","):
            s_clean = s.strip()
            if s_clean:
                query = query.filter(Candidate.skills.like(f'%"{s_clean}"%'))
                
    return query.offset(offset).limit(limit).all()

@router.get("/", response_model=List[CandidateInDB])
def read_candidates(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    status: Optional[str] = None,
    min_experience: Optional[float] = None,
    work_preference: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    response: Response = None
):
    query = db.query(Candidate)
    
    if q:
        query = query.filter(
            (Candidate.name.ilike(f"%{q}%")) | 
            (Candidate.title.ilike(f"%{q}%")) |
            (Candidate.resume_text.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter(Candidate.status == status)
    if work_preference:
        prefs = [p.strip() for p in work_preference.split(",") if p.strip()]
        if prefs:
            title_prefs = [p.capitalize() for p in prefs]
            query = query.filter(Candidate.work_preference.in_(title_prefs))
    if min_experience:
        query = query.filter(Candidate.experience_years >= min_experience)
        
    if skill:
        for s in skill.split(","):
            s_clean = s.strip()
            if s_clean:
                query = query.filter(Candidate.skills.like(f'%"{s_clean}"%'))
                
    if response is not None:
        total_count = query.count()
        response.headers["X-Total-Count"] = str(total_count)
        response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
                
    # Handle Query defaults when called directly in Python tests
    from fastapi.params import Query as QueryParam
    actual_limit = limit.default if isinstance(limit, QueryParam) else limit
    actual_offset = offset.default if isinstance(offset, QueryParam) else offset
    
    return query.offset(actual_offset).limit(actual_limit).all()

@router.get("/{candidate_id}", response_model=CandidateInDB)
def read_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.post("/", response_model=CandidateInDB, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    db_cand = db.query(Candidate).filter(Candidate.email == candidate_in.email).first()
    if db_cand:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_candidate = Candidate(**candidate_in.model_dump())
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return new_candidate

@router.put("/{candidate_id}", response_model=CandidateInDB)
def update_candidate(candidate_id: int, candidate_in: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    update_data = candidate_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(candidate, key, val)
        
    db.commit()
    db.refresh(candidate)
    return candidate

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return None

@router.get("/{candidate_id}/explanation", response_model=CandidateExplanationResponse)
def get_candidate_explanation(
    candidate_id: int,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Resolve job
    if job_id is not None:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
    else:
        # fallback to first job
        job = db.query(Job).first()
        if not job:
            raise HTTPException(status_code=404, detail="No jobs found in the database")

    # Find ranking or calculate match
    ranking = db.query(Ranking).filter(
        Ranking.candidate_id == candidate.id,
        Ranking.job_id == job.id
    ).first()

    if ranking:
        score = ranking.match_score
        explanation = ranking.explanation
        tier = ranking.tier
    else:
        # Calculate dynamically
        score, explanation, tier = RankerService.calculate_match(candidate, job)

    # 1. Why Candidate Matched
    why_matched = (
        f"{candidate.name} is classified as a '{tier}' for the {job.title} position, "
        f"matching with an overall compatibility score of {score}%. "
        f"They possess {candidate.experience_years or 0.0} years of professional experience (required: {job.experience_required or 0.0} years) "
        f"and align with {len(explanation.get('matched_skills', []))} out of {len(explanation.get('matched_skills', [])) + len(explanation.get('missing_skills', []))} required skills."
    )

    # 2. Key Strengths
    strengths = []
    skills_score = explanation.get("skills_score", 0.0)
    if skills_score >= 80.0:
        strengths.append(f"High technical alignment: Matches {skills_score}% of the required skill categories.")
    elif skills_score >= 50.0:
        strengths.append("Foundational technical alignment: Matches primary skill requirements.")

    matched_skills = explanation.get("matched_skills", [])
    if matched_skills:
        strengths.append(f"Demonstrated core proficiency: Strong experience with {', '.join(matched_skills[:3])}.")

    exp_diff = explanation.get("experience_difference_years", 0.0)
    if exp_diff >= 3.0:
        strengths.append(f"Seniority surplus: Exceeds the role's targeted experience requirement by {round(exp_diff, 1)} years.")
    elif exp_diff >= 0.0:
        strengths.append(f"Meets experience criteria: Possesses {candidate.experience_years or 0.0} years of experience.")

    if explanation.get("has_retrieval_experience"):
        strengths.append("Domain expertise: Proven career background in search, recommendation systems, or information retrieval.")

    edu_score = explanation.get("education_score", 0.0)
    if edu_score >= 80.0:
        strengths.append("Strong academic credentials: High-tier computer science or technical degree background.")

    beh_score = explanation.get("behavioral_score", 0.0)
    if beh_score >= 80.0:
        strengths.append("High platform engagement: Excellent profile completeness and responsiveness indicators.")

    # Fallback if list is too short
    if len(strengths) < 2:
        strengths.append("Basic requirements met: Matches key qualifications for the role.")
        strengths.append("Responsive profile: Actively reachable on the platform.")

    # 3. Weaknesses / Risks
    weaknesses = []
    missing_skills = explanation.get("missing_skills", [])
    if missing_skills:
        weaknesses.append(f"Skill gaps detected: Lacks proven experience in key requested capabilities: {', '.join(missing_skills[:3])}.")

    exp_diff = explanation.get("experience_difference_years", 0.0)
    if exp_diff < 0:
        weaknesses.append(f"Experience deficit: Under-qualified by {round(abs(exp_diff), 1)} years relative to the job requirements.")

    # Average company tenure
    if candidate.career_history and len(candidate.career_history) >= 2:
        total_months = sum(jh.get("duration_months") or 0 for jh in candidate.career_history)
        if total_months > 0:
            avg_tenure = total_months / len(candidate.career_history)
            if avg_tenure < 15.0:
                weaknesses.append(f"Retention risk warning: Candidate exhibits a high-turnover pattern with an average tenure of {round(avg_tenure, 1)} months.")

    loc_score = explanation.get("location_score", 0.0)
    if loc_score < 50.0:
        weaknesses.append(f"Location mismatch: Prefers {candidate.work_preference or 'Remote'} mode but the role is {job.work_preference or 'Onsite'} in {job.location or 'any office'}.")

    cand_skills_set = {s.lower().strip() for s in (candidate.skills or [])}
    has_wrapper = any(s in cand_skills_set for s in ["langchain", "openai", "openai embeddings"])
    has_core = any(s in cand_skills_set for s in ["pytorch", "tensorflow", "scikit-learn", "xgboost", "lightgbm", "search", "retrieval", "ranking", "recommendation"])
    if has_wrapper and not has_core:
        weaknesses.append("Foundational gap: Demonstrates knowledge of wrapper APIs (LangChain/OpenAI) but lacks core ML/algorithmic foundations.")

    if not weaknesses:
        weaknesses.append("No major technical or cultural risk factors identified.")

    # 4. Hiring Recommendation
    if score >= 85.0:
        hiring_recommendation = (
            f"Fast-Track to Interview: Highly recommended. {candidate.name} is an exceptional fit ({score}%) who meets "
            f"or exceeds all key criteria. Their engineering background is highly compatible with obsidian architectures."
        )
    elif score >= 70.0:
        hiring_recommendation = (
            f"Proceed to Screening: Recommended. {candidate.name} is a strong candidate ({score}%) with minor skill gaps "
            f"in {', '.join(missing_skills[:2]) if missing_skills else 'certain technologies'} that can be easily addressed via onboarding upskilling."
        )
    elif score >= 50.0:
        hiring_recommendation = (
            f"Conditional Review: Neutral. {candidate.name} matches basic criteria ({score}%), but shows notable gaps in experience "
            f"or skills. Recommend scheduling a preliminary technical call if top-tier options are limited."
        )
    else:
        hiring_recommendation = (
            f"Do Not Proceed: Unsuitable. {candidate.name} ({score}%) lacks core qualifications, required experience, "
            f"or critical technical capabilities needed for this role."
        )

    return CandidateExplanationResponse(
        candidate_id=candidate.id,
        job_id=job.id,
        match_score=score,
        tier=tier,
        why_matched=why_matched,
        strengths=strengths,
        weaknesses=weaknesses,
        missing_skills=missing_skills,
        hiring_recommendation=hiring_recommendation
    )


@router.post("/compare", response_model=CandidateComparisonResponse, status_code=status.HTTP_200_OK)
def compare_candidates(
    candidate_ids: List[int],
    job_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Compare multiple candidates side-by-side.
    
    Shows:
    - Skills and proficiency levels
    - Experience and career history
    - Education background
    - Behavioral signals and engagement
    - Ranking scores (if job_id provided)
    - Hiring recommendations
    
    Args:
        candidate_ids: List of candidate IDs to compare (minimum 2)
        job_id: Optional job ID for ranking comparison
        db: Database session
        
    Returns:
        Comprehensive comparison data for all candidates
    """
    try:
        comparison_data = ComparisonService.compare_candidates(
            candidate_ids=candidate_ids,
            job_id=job_id,
            db=db
        )
        return CandidateComparisonResponse(
            candidates=comparison_data["candidates"],
            summary=comparison_data["summary"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

