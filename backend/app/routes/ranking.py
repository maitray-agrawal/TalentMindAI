from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.schemas.ranking import RankingWithCandidate, SkillGapResponse
from app.services.ranker_service import RankerService
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/ranking", tags=["Ranking"])

@router.post("/rank/{job_id}", response_model=List[RankingWithCandidate])
def calculate_job_rankings(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(Candidate).all()
    if not candidates:
        return []

    rankings_response = []
    
    # Process each candidate through the ranking pipeline
    for candidate in candidates:
        score, explanation, tier = RankerService.calculate_match(candidate, job)
        
        # Check if ranking already exists
        ranking = db.query(Ranking).filter(
            Ranking.candidate_id == candidate.id,
            Ranking.job_id == job.id
        ).first()
        
        if ranking:
            ranking.match_score = score
            ranking.explanation = explanation
            ranking.tier = tier
        else:
            ranking = Ranking(
                candidate_id=candidate.id,
                job_id=job.id,
                match_score=score,
                explanation=explanation,
                tier=tier
            )
            db.add(ranking)
            
        db.commit()
        db.refresh(ranking)
        rankings_response.append(ranking)

    # Sort rankings descending by score
    rankings_response.sort(key=lambda x: x.match_score, reverse=True)
    return rankings_response

@router.get("/job/{job_id}", response_model=List[RankingWithCandidate])
def get_job_rankings(
    job_id: int, 
    min_score: Optional[float] = None, 
    tier: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    # If rankings are empty, auto-trigger the ranking pipeline
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    query = db.query(Ranking).filter(Ranking.job_id == job_id)
    if min_score is not None:
        query = query.filter(Ranking.match_score >= min_score)
    if tier:
        query = query.filter(Ranking.tier == tier)
        
    rankings = query.order_by(Ranking.match_score.desc()).all()
    
    if not rankings:
        # Auto-rank
        return calculate_job_rankings(job_id=job_id, db=db)
        
    return rankings

@router.get("/candidate/{candidate_id}/skill-gap/{job_id}", response_model=SkillGapResponse)
def get_candidate_skill_gap(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")
        
    # Get or calculate match details
    ranking = db.query(Ranking).filter(
        Ranking.candidate_id == candidate_id,
        Ranking.job_id == job_id
    ).first()
    
    if ranking:
        score = ranking.match_score
        explanation = ranking.explanation
    else:
        score, explanation, _ = RankerService.calculate_match(candidate, job)

    roadmap = CopilotService.generate_roadmap(candidate, job)
    
    return SkillGapResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        job_id=job.id,
        job_title=job.title,
        match_score=score,
        gained_skills=explanation.get("matched_skills", []),
        missing_skills=explanation.get("missing_skills", []),
        experience_gap_years=max(0.0, float(job.experience_required or 0.0) - float(candidate.experience_years or 0.0)),
        upskilling_roadmap=roadmap
    )
