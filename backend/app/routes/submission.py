from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import os
import csv
import re

from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.services.ranker_service import RankerService

router = APIRouter(prefix="/submission", tags=["Submission"])

CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_submission(
    job_id: int = Query(5, description="The job ID to generate rankings submission for"),
    db: Session = Depends(get_db)
):
    # 1. Fetch job description / details
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=404, 
            detail=f"Job with ID {job_id} not found."
        )

    # 2. Get rankings sorted by match_score descending
    rankings = db.query(Ranking).filter(Ranking.job_id == job_id).order_by(Ranking.match_score.desc()).all()

    # 3. If rankings are empty, calculate them dynamically
    if not rankings:
        candidates = db.query(Candidate).all()
        if not candidates:
            raise HTTPException(
                status_code=400,
                detail="No candidates in database to rank."
            )
        for candidate in candidates:
            score, explanation, tier = RankerService.calculate_match(candidate, job)
            ranking = Ranking(
                candidate_id=candidate.id,
                job_id=job_id,
                match_score=score,
                explanation=explanation,
                tier=tier
            )
            db.add(ranking)
        db.commit()
        # Fetch rankings again after calculation
        rankings = db.query(Ranking).filter(Ranking.job_id == job_id).order_by(Ranking.match_score.desc()).all()

    # 4. Filter, Sort, and Enforce tie-breaks
    valid_items = []
    for r in rankings:
        candidate = r.candidate
        if not candidate:
            continue

        cand_id_str = candidate.candidate_id or f"CAND_{candidate.id:07d}"
        
        if not CANDIDATE_ID_PATTERN.match(cand_id_str):
            continue

        score_val = f"{r.match_score / 100.0:.4f}"
        float_score = float(score_val)

        valid_items.append({
            "ranking": r,
            "candidate": candidate,
            "cand_id_str": cand_id_str,
            "score_val": score_val,
            "float_score": float_score
        })

    # Sort by descending score, then ascending candidate ID for tie-breaking
    valid_items.sort(key=lambda x: (-x["float_score"], x["cand_id_str"]))
    top_100 = valid_items[:100]

    # 5. Generate CSV
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])

    seen_ranks = set()
    prev_score = float('inf')

    for idx, item in enumerate(top_100):
        r = item["ranking"]
        candidate = item["candidate"]
        cand_id_str = item["cand_id_str"]
        score_val = item["score_val"]
        rank_val = idx + 1
        
        current_float_score = item["float_score"]
        if current_float_score > prev_score:
            raise HTTPException(
                status_code=500,
                detail=f"Validation error: Score {current_float_score} at rank {rank_val} is higher than previous score {prev_score}."
            )
        prev_score = current_float_score

        # Validate unique rank
        if rank_val in seen_ranks:
            raise HTTPException(
                status_code=500,
                detail=f"Validation error: Rank {rank_val} is not unique."
            )
        seen_ranks.add(rank_val)

        # Structure reasoning matching sample submission:
        # e.g., "HR Manager with 6.1 yrs; 9 AI core skills; response rate 0.76."
        explanation = r.explanation or {}
        matched_skills = []
        if isinstance(explanation, dict):
            matched_skills = explanation.get("matched_skills", []) or []
        num_skills = len(matched_skills)
        
        response_rate = 0.0
        if candidate.redrob_signals and isinstance(candidate.redrob_signals, dict):
            response_rate = candidate.redrob_signals.get("recruiter_response_rate", 0.0) or 0.0

        title = candidate.title or "Candidate"
        exp = candidate.experience_years or 0.0
        
        reasoning_str = f"{title} with {exp:.1f} yrs; {num_skills} matched skills; response rate {response_rate:.2f}."
        
        # Validate reasoning is populated
        if not reasoning_str.strip():
            raise HTTPException(
                status_code=500,
                detail=f"Validation error: Reasoning is empty for candidate {cand_id_str}."
            )

        writer.writerow([cand_id_str, rank_val, score_val, reasoning_str])

    csv_content = output.getvalue()

    # 6. Write submission.csv to workspace root
    workspace_csv_path = r"d:\TalentMindAI\submission.csv"
    try:
        with open(workspace_csv_path, "w", newline="", encoding="utf-8") as f:
            f.write(csv_content)
    except Exception as e:
        # Non-blocking, log failure to write local file
        print(f"Warning: Could not save submission.csv to workspace root: {e}")

    # 7. Stream file download response
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=submission.csv"}
    )
