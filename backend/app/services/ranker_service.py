import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
from app.models.candidate import Candidate
from app.models.job import Job
from app.config import settings

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

        # 5. Education Match
        edu_score = 1.0
        # Get education requirements if present
        edu_reqs = []
        if hasattr(job, 'education_requirements') and job.education_requirements:
            edu_reqs = job.education_requirements
        elif job.description:
            try:
                from app.services.jd_analyzer import JDAnalyzerService
                detailed = JDAnalyzerService.analyze_detailed(job.description)
                edu_reqs = detailed.get("education_requirements", [])
            except Exception:
                edu_reqs = []
                
        # If there are no specified education requirements, candidate gets full score
        if not edu_reqs or any("not specified" in r.lower() for r in edu_reqs):
            edu_score = 1.0
        else:
            cand_edu_list = candidate.education or []
            if not cand_edu_list:
                edu_score = 0.5  # No education listed but job requires it
            else:
                best_match = 0.5
                for edu in cand_edu_list:
                    inst = (edu.get("institution") or "").lower()
                    deg = (edu.get("degree") or "").lower()
                    field = (edu.get("field_of_study") or "").lower()
                    tier = (edu.get("tier") or "").lower()
                    
                    match_val = 0.6  # Base score for having some education
                    
                    # Check tier 1
                    if tier == "tier_1" or "tier-1" in tier or "stanford" in inst or "mit" in inst or "harvard" in inst:
                        match_val += 0.2
                        
                    # Check field match
                    job_title_lower = (job.title or "").lower()
                    if "computer science" in field or "cs" in field or "engineering" in field or "ai" in field or "ml" in field:
                        if any(kw in job_title_lower for kw in ["engineer", "developer", "scientist", "tech", "ai", "ml", "specialist", "programmer", "architect", "lead"]):
                            match_val += 0.2
                            
                    # Check degree level
                    if "ph.d" in deg or "phd" in deg or "doctor" in deg:
                        match_val += 0.2
                    elif "master" in deg or "m.s" in deg or "m.tech" in deg:
                        match_val += 0.1
                        
                    best_match = max(best_match, min(1.0, match_val))
                edu_score = best_match

        # 6. Behavioral Signals Match
        signals = candidate.redrob_signals or {}
        
        # Profile completeness (40% weight)
        completeness = float(signals.get("profile_completeness_score", 50.0)) / 100.0
        
        # Open to work flag (20% weight)
        open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.5
        
        # GitHub activity score (20% weight)
        github = float(signals.get("github_activity_score", 50.0)) / 100.0
        
        # Recruiter response rate (20% weight)
        response_rate = float(signals.get("recruiter_response_rate", 0.8))
        
        behavioral_score = (completeness * 0.4) + (open_to_work * 0.2) + (github * 0.2) + (response_rate * 0.2)
        behavioral_score = max(0.0, min(1.0, behavioral_score))

        # 7. Weighted Score Calculation
        final_score = (
            (skills_match_ratio * settings.WEIGHT_SKILLS) +
            (exp_score * settings.WEIGHT_EXPERIENCE) +
            (text_sim * settings.WEIGHT_SEMANTIC) +
            (edu_score * settings.WEIGHT_EDUCATION) +
            (behavioral_score * settings.WEIGHT_BEHAVIORAL) +
            (location_score * settings.WEIGHT_LOCATION)
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
            "education_score": round(edu_score * 100.0, 1),
            "behavioral_score": round(behavioral_score * 100.0, 1),
            "location_score": round(location_score * 100.0, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_difference_years": round(exp_diff, 1)
        }

        return final_score, explanation, tier
