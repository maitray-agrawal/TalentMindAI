import os
import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate
from pydantic import ValidationError

try:
    import psutil
except ImportError:
    psutil = None

class IngestionService:
    @staticmethod
    def get_memory_usage() -> float:
        """Returns current memory usage of the process in MB."""
        if psutil:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        return 0.0

    @classmethod
    def ingest_candidates(
        cls,
        db: Session,
        file_path: str,
        limit: Optional[int] = None,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Parses and ingests the candidates.jsonl file into the SQLite database.
        Uses streaming to process line-by-line and batch transactions for performance.
        Ensures idempotency using Candidate.candidate_id upserts.
        """
        start_time = time.time()
        start_mem = cls.get_memory_usage()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")

        # Prefetch existing candidate_ids to keep upserts fast in memory
        existing_ids = {
            c[0] for c in db.query(Candidate.candidate_id)
            .filter(Candidate.candidate_id.isnot(None))
            .all()
        }

        success_count = 0
        error_count = 0
        update_count = 0
        errors = []

        batch = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if limit is not None and success_count + update_count >= limit:
                    break

                line_num = line_idx + 1
                clean_line = line.strip()
                if not clean_line:
                    continue

                try:
                    candidate_data = json.loads(clean_line)
                    
                    # Validate candidate_id existence and format
                    cand_id = candidate_data.get("candidate_id")
                    if not cand_id:
                        raise ValueError("Missing candidate_id")

                    # Map raw JSON to Candidate schema structures
                    profile = candidate_data.get("profile", {})
                    name = profile.get("anonymized_name", "Anonymized Candidate")
                    title = profile.get("current_title")
                    location = profile.get("location")
                    
                    signals = candidate_data.get("redrob_signals", {})
                    work_pref = signals.get("preferred_work_mode", "remote").capitalize()
                    exp_years = float(profile.get("years_of_experience", 0.0))
                    
                    skills_raw = candidate_data.get("skills", [])
                    skills = [s.get("name") for s in skills_raw if s.get("name")]
                    
                    # Compute expected salary
                    sal_range = signals.get("expected_salary_range_inr_lpa", {})
                    salary_expectation = int(sal_range.get("max", 0))

                    # Generate dynamic resume text
                    summary = profile.get("summary", "")
                    career_lines = []
                    for job in candidate_data.get("career_history", []):
                        job_title = job.get("title", "Unknown Role")
                        comp = job.get("company", "Unknown Company")
                        desc = job.get("description", "")
                        career_lines.append(f"- {job_title} at {comp}: {desc}")
                    career_summary = "\n".join(career_lines)
                    resume_text = f"Headline: {profile.get('headline', '')}\nSummary: {summary}\n\nCareer History:\n{career_summary}"

                    # Unique email derived from candidate_id to avoid DB unique constraint violations
                    email = f"{cand_id.lower()}@redrob.ai"

                    if cand_id in existing_ids:
                        # Update existing candidate
                        db_cand = db.query(Candidate).filter(Candidate.candidate_id == cand_id).first()
                        if db_cand:
                            db_cand.name = name
                            db_cand.email = email
                            db_cand.title = title
                            db_cand.location = location
                            db_cand.work_preference = work_pref
                            db_cand.experience_years = exp_years
                            db_cand.skills = skills
                            db_cand.resume_text = resume_text
                            db_cand.salary_expectation = salary_expectation
                            db_cand.profile = profile
                            db_cand.career_history = candidate_data.get("career_history", [])
                            db_cand.education = candidate_data.get("education", [])
                            db_cand.certifications = candidate_data.get("certifications", [])
                            db_cand.languages = candidate_data.get("languages", [])
                            db_cand.redrob_signals = signals
                            update_count += 1
                    else:
                        # Insert new candidate
                        db_cand = Candidate(
                            candidate_id=cand_id,
                            name=name,
                            email=email,
                            title=title,
                            location=location,
                            work_preference=work_pref,
                            experience_years=exp_years,
                            skills=skills,
                            resume_text=resume_text,
                            status="Sourcing",
                            salary_expectation=salary_expectation,
                            profile=profile,
                            career_history=candidate_data.get("career_history", []),
                            education=candidate_data.get("education", []),
                            certifications=candidate_data.get("certifications", []),
                            languages=candidate_data.get("languages", []),
                            redrob_signals=signals
                        )
                        batch.append(db_cand)
                        success_count += 1

                    # Commit batch if limit reached
                    if len(batch) >= batch_size:
                        db.add_all(batch)
                        db.commit()
                        batch = []

                except (json.JSONDecodeError, ValueError, KeyError, ValidationError) as e:
                    error_count += 1
                    if len(errors) < 20: # Cap detailed errors to prevent bloat
                        errors.append(f"Line {line_num}: {str(e)}")
                    continue

        # Commit remaining batch
        if batch:
            db.add_all(batch)
            db.commit()

        end_time = time.time()
        end_mem = cls.get_memory_usage()

        elapsed = end_time - start_time
        processed = success_count + update_count
        rate = processed / elapsed if elapsed > 0 else 0

        return {
            "status": "success",
            "file_path": file_path,
            "records_processed": processed,
            "inserted": success_count,
            "updated": update_count,
            "errors_count": error_count,
            "errors_sample": errors,
            "elapsed_seconds": round(elapsed, 2),
            "ingestion_rate_per_second": round(rate, 2),
            "memory_usage_start_mb": round(start_mem, 2),
            "memory_usage_end_mb": round(end_mem, 2),
            "memory_growth_mb": round(end_mem - start_mem, 2),
        }
