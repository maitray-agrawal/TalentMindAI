from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from collections import Counter
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateInDB
from app.services.ingestion import IngestionService

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
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    
    if q:
        query = query.filter(
            (Candidate.name.ilike(f"%{q}%")) | 
            (Candidate.title.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter(Candidate.status == status)
    if work_preference:
        query = query.filter(Candidate.work_preference == work_preference)
    if min_experience:
        query = query.filter(Candidate.experience_years >= min_experience)
        
    candidates = query.all()
    
    if skill:
        skill_lower = skill.lower()
        candidates = [
            c for c in candidates 
            if any(skill_lower in (s or "").lower() for s in (c.skills or []))
        ]
        
    return candidates

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
