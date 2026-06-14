from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.schemas.ranking import (
    RankingWithCandidate, 
    SkillGapResponse, 
    RankingGenerateRequest, 
    CandidateRankResponse
)
from app.services.ranker_service import RankerService
from app.services.copilot_service import CopilotService
from app.services.jd_analyzer import JDAnalyzerService


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

@router.post("/generate", response_model=List[CandidateRankResponse])
def generate_ranking(req: RankingGenerateRequest, db: Session = Depends(get_db)):
    # Validate that we have at least one non-empty source of job information
    has_jd = bool(req.job_description and req.job_description.strip())
    has_structured = any([
        bool(req.title and req.title.strip()),
        bool(req.required_skills),
        req.experience_required is not None,
        bool(req.education_requirements),
        bool(req.work_preference and req.work_preference.strip()),
        bool(req.location and req.location.strip())
    ])
    
    if not has_jd and not has_structured:
        raise HTTPException(
            status_code=400,
            detail="Must provide either a non-empty job_description or structured job analysis fields."
        )

    # 1. Resolve analyzed/provided job attributes
    analysis = {}
    if req.job_description:
        analysis = JDAnalyzerService.analyze_detailed(req.job_description)

    title = req.title or analysis.get("title") or "Untitled Role"
    description = req.job_description or req.title or "Pre-analyzed Job Description"
    required_skills = req.required_skills if req.required_skills is not None else (analysis.get("required_skills") or [])
    experience_required = req.experience_required if req.experience_required is not None else float(analysis.get("experience_required") or 0.0)
    work_preference = req.work_preference or analysis.get("work_preference") or "Remote"
    location = req.location or analysis.get("location") or "Remote"
    edu_reqs = req.education_requirements if req.education_requirements is not None else (analysis.get("education_requirements") or [])

    # 2. Create a temporary in-memory Job object
    temp_job = Job(
        title=title,
        description=description,
        required_skills=required_skills,
        experience_required=experience_required,
        work_preference=work_preference,
        location=location
    )
    temp_job.education_requirements = edu_reqs

    # 3. Rank candidates against this job
    candidates = db.query(Candidate).all()
    if not candidates:
        return []

    ranked_results = []
    for candidate in candidates:
        score, explanation, tier = RankerService.calculate_match(candidate, temp_job)
        
        # 4. Generate ranking explanation reasoning
        matched_skills_str = ", ".join(explanation.get("matched_skills", [])) if explanation.get("matched_skills") else "None"
        missing_skills_str = ", ".join(explanation.get("missing_skills", [])) if explanation.get("missing_skills") else "None"
        
        reasoning = (
            f"Candidate matches {len(explanation.get('matched_skills', []))} out of {len(explanation.get('matched_skills', [])) + len(explanation.get('missing_skills', []))} required skills. "
            f"Matched skills: {matched_skills_str}. "
            f"Missing skills: {missing_skills_str}. "
            f"Candidate has {candidate.experience_years or 0.0} years of experience (Required: {temp_job.experience_required or 0.0} years). "
            f"Location / preference fit: {candidate.location or 'Not Specified'} ({candidate.work_preference or 'Remote'}) vs job's {temp_job.location or 'Not Specified'} ({temp_job.work_preference or 'Remote'}). "
            f"Education Match: {explanation.get('education_score') or 0.0}%. "
            f"Behavioral Signals Score: {explanation.get('behavioral_score') or 0.0}%. "
            f"Fit Score details: Skills {explanation.get('skills_score') or 0.0}%, Experience {explanation.get('experience_score') or 0.0}%, Text Sim {explanation.get('text_similarity_score') or 0.0}%, Location {explanation.get('location_score') or 0.0}%, Education {explanation.get('education_score') or 0.0}%, Behavioral {explanation.get('behavioral_score') or 0.0}%."
        )

        ranked_results.append({
            "candidate_id": candidate.id,
            "candidate_uuid": candidate.candidate_id,
            "candidate_name": candidate.name,
            "score": score,
            "reasoning": reasoning
        })

    # 5. Sort candidates by score descending
    ranked_results.sort(key=lambda x: x["score"], reverse=True)

    # 6. Assign ranks
    final_results = []
    for idx, res in enumerate(ranked_results):
        res["rank"] = idx + 1
        final_results.append(CandidateRankResponse(**res))

    # Apply limit if specified
    if req.limit is not None and req.limit > 0:
        final_results = final_results[:req.limit]

    return final_results

