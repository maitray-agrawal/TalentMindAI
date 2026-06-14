import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
from app.models.candidate import Candidate
from app.models.job import Job

class RankerService:
    @staticmethod
    def calculate_match(candidate: Candidate, job: Job) -> Tuple[float, Dict[str, Any], str]:
        # 1. Text Similarity using TF-IDF and Cosine Similarity
        # Combine candidate data into a single corpus string
        cand_skills_str = " ".join(candidate.skills or [])
        cand_corpus = f"{candidate.title or ''} {cand_skills_str} {candidate.resume_text or ''}"
        
        # Combine job data into a single corpus string
        job_skills_str = " ".join(job.required_skills or [])
        job_corpus = f"{job.title or ''} {job_skills_str} {job.description or ''}"
        
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform([cand_corpus, job_corpus])
            text_sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        except Exception:
            text_sim = 0.0

        # 2. Skills Match (Exact case-insensitive match check)
        cand_skills_set = {s.lower().strip() for s in (candidate.skills or [])}
        job_skills_set = {s.lower().strip() for s in (job.required_skills or [])}
        
        matched_skills = []
        missing_skills = []
        
        for skill in job.required_skills or []:
            if skill.lower().strip() in cand_skills_set:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        skills_match_ratio = 1.0
        if len(job_skills_set) > 0:
            skills_match_ratio = len(matched_skills) / len(job_skills_set)

        # 3. Experience Match
        exp_score = 1.0
        exp_diff = float(candidate.experience_years or 0.0) - float(job.experience_required or 0.0)
        if job.experience_required and job.experience_required > 0:
            if candidate.experience_years >= job.experience_required:
                exp_score = 1.0
            else:
                exp_score = float(candidate.experience_years or 0.0) / float(job.experience_required)
        
        # 4. Location & Work Preference Match
        location_score = 1.0
        if job.work_preference and job.work_preference.lower() != "remote":
            # If job is hybrid or onsite, location alignment is checked
            cand_loc = (candidate.location or "").lower()
            job_loc = (job.location or "").lower()
            if cand_loc == job_loc or cand_loc in job_loc or job_loc in cand_loc:
                location_score = 1.0
            elif candidate.work_preference and candidate.work_preference.lower() == "remote":
                location_score = 0.2  # Candidate wants remote but job is hybrid/onsite
            else:
                location_score = 0.5  # Mixed preference / nearby location
        else:
            # Job is remote
            if candidate.work_preference and candidate.work_preference.lower() == "remote":
                location_score = 1.0
            else:
                location_score = 0.9  # Job is remote, candidate is flexible

        # 5. Weighted Score Calculation
        # Weights: 45% Skills, 25% Experience, 15% Text Similarity, 15% Location Fit
        final_score = (
            (skills_match_ratio * 0.45) +
            (exp_score * 0.25) +
            (text_sim * 0.15) +
            (location_score * 0.15)
        ) * 100.0
        
        # Clip score between 0 and 100
        final_score = round(max(0.0, min(100.0, final_score)), 1)

        # Determine Match Tier
        if final_score >= 85.0:
            tier = "Top Match"
        elif final_score >= 70.0:
            tier = "Strong Match"
        elif final_score >= 50.0:
            tier = "Good Match"
        else:
            tier = "Potentially Unsuitable"

        explanation = {
            "skills_score": round(skills_match_ratio * 100.0, 1),
            "experience_score": round(exp_score * 100.0, 1),
            "text_similarity_score": round(text_sim * 100.0, 1),
            "location_score": round(location_score * 100.0, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_difference_years": round(exp_diff, 1)
        }

        return final_score, explanation, tier
