from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.ranking import Ranking
from app.models.job import Job


class ComparisonService:
    @staticmethod
    def compare_candidates(
        candidate_ids: List[int],
        job_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple candidates and return detailed comparison metrics
        """
        if not candidate_ids or len(candidate_ids) < 2:
            raise ValueError("At least 2 candidate IDs are required for comparison")

        candidates = []
        for cand_id in candidate_ids:
            cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
            if not cand:
                raise ValueError(f"Candidate with ID {cand_id} not found")
            candidates.append(cand)

        # Build comparison data
        comparison = {
            "candidates": [],
            "summary": {}
        }

        for candidate in candidates:
            cand_data = ComparisonService._extract_candidate_data(candidate, job_id, db)
            comparison["candidates"].append(cand_data)

        # Calculate summary metrics
        comparison["summary"] = ComparisonService._calculate_summary(comparison["candidates"])

        return comparison

    @staticmethod
    def _extract_candidate_data(
        candidate: Candidate,
        job_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Extract comprehensive candidate data for comparison"""
        
        # Get ranking score if job_id provided
        ranking_score = 0.0
        ranking_tier = "N/A"
        ranking_explanation = {}
        
        if job_id:
            ranking = db.query(Ranking).filter(
                Ranking.candidate_id == candidate.id,
                Ranking.job_id == job_id
            ).first()
            if ranking:
                ranking_score = ranking.match_score
                ranking_tier = ranking.tier
                ranking_explanation = ranking.explanation or {}

        # Extract skills with proficiency levels
        skills_data = []
        if candidate.skills:
            for skill in candidate.skills:
                # Try to get proficiency from career history or resume
                proficiency = ComparisonService._estimate_skill_proficiency(skill, candidate)
                skills_data.append({
                    "name": skill,
                    "proficiency": proficiency,
                    "endorsements": 0  # Can be enhanced from redrob signals
                })

        # Extract education details
        education_data = []
        if candidate.education:
            for edu in candidate.education:
                education_data.append({
                    "institution": edu.get("institution") if isinstance(edu, dict) else getattr(edu, "institution", None),
                    "degree": edu.get("degree") if isinstance(edu, dict) else getattr(edu, "degree", None),
                    "field_of_study": edu.get("field_of_study") if isinstance(edu, dict) else getattr(edu, "field_of_study", None),
                    "tier": edu.get("tier", "unknown") if isinstance(edu, dict) else getattr(edu, "tier", "unknown")
                })

        # Extract experience details
        experience_data = []
        total_years = candidate.experience_years or 0.0
        
        if candidate.career_history:
            for job_hist in candidate.career_history:
                if isinstance(job_hist, dict):
                    experience_data.append({
                        "company": job_hist.get("company"),
                        "title": job_hist.get("title"),
                        "duration_months": job_hist.get("duration_months"),
                        "is_current": job_hist.get("is_current", False),
                        "industry": job_hist.get("industry")
                    })
                else:
                    experience_data.append({
                        "company": getattr(job_hist, "company", None),
                        "title": getattr(job_hist, "title", None),
                        "duration_months": getattr(job_hist, "duration_months", None),
                        "is_current": getattr(job_hist, "is_current", False),
                        "industry": getattr(job_hist, "industry", None)
                    })

        # Extract behavioral signals
        behavioral_signals = ComparisonService._extract_behavioral_signals(candidate)

        # Generate hiring recommendation
        recommendation = ComparisonService._generate_hiring_recommendation(
            candidate,
            ranking_score,
            ranking_tier,
            behavioral_signals
        )

        return {
            "id": candidate.id,
            "name": candidate.name,
            "title": candidate.title,
            "email": candidate.email,
            "location": candidate.location,
            "work_preference": candidate.work_preference,
            "status": candidate.status,
            "avatar_url": candidate.avatar_url,
            "experience": {
                "years": total_years,
                "history": experience_data,
                "level": ComparisonService._classify_experience_level(total_years)
            },
            "skills": skills_data,
            "education": education_data,
            "behavioral_signals": behavioral_signals,
            "ranking": {
                "score": ranking_score,
                "tier": ranking_tier,
                "explanation": ranking_explanation
            },
            "recommendation": recommendation,
            "salary_expectation": candidate.salary_expectation
        }

    @staticmethod
    def _estimate_skill_proficiency(skill: str, candidate: Candidate) -> str:
        """Estimate skill proficiency level based on resume and career history"""
        skill_lower = skill.lower()
        
        # Check resume for skill mentions
        resume_text = (candidate.resume_text or "").lower()
        career_desc = ""
        
        if candidate.career_history:
            for job_hist in candidate.career_history:
                if isinstance(job_hist, dict):
                    career_desc += (job_hist.get("description") or "").lower()
                else:
                    career_desc += (getattr(job_hist, "description", "") or "").lower()
        
        combined_text = f"{resume_text} {career_desc}"
        
        # Keywords for proficiency levels
        expert_keywords = ["expert", "lead", "architect", "specialist", "principal", "senior"]
        intermediate_keywords = ["proficient", "experienced", "working", "knowledge", "familiar"]
        
        count = combined_text.count(skill_lower)
        expert_count = sum(1 for kw in expert_keywords if f"{kw}" in combined_text and skill_lower in combined_text)
        
        if expert_count > 0 or count > 5:
            return "Expert"
        elif count > 2:
            return "Intermediate"
        elif count > 0:
            return "Beginner"
        else:
            return "Listed"

    @staticmethod
    def _classify_experience_level(years: float) -> str:
        """Classify experience level based on years"""
        if years < 2:
            return "Entry Level"
        elif years < 5:
            return "Mid Level"
        elif years < 10:
            return "Senior"
        else:
            return "Principal"

    @staticmethod
    def _extract_behavioral_signals(candidate: Candidate) -> Dict[str, Any]:
        """Extract behavioral signals from redrob_signals"""
        signals = candidate.redrob_signals or {}
        
        return {
            "profile_completeness": signals.get("profile_completeness_score", 0),
            "open_to_work": signals.get("open_to_work_flag", False),
            "profile_views_30d": signals.get("profile_views_received_30d", 0),
            "applications_submitted_30d": signals.get("applications_submitted_30d", 0),
            "recruiter_response_rate": signals.get("recruiter_response_rate", 0),
            "avg_response_time_hours": signals.get("avg_response_time_hours", None),
            "connection_count": signals.get("connection_count", 0),
            "endorsements_received": signals.get("endorsements_received", 0),
            "notice_period_days": signals.get("notice_period_days", None),
            "willing_to_relocate": signals.get("willing_to_relocate", False),
            "github_activity_score": signals.get("github_activity_score", 0),
            "interview_completion_rate": signals.get("interview_completion_rate", 0),
            "offer_acceptance_rate": signals.get("offer_acceptance_rate", 0),
            "verified_credentials": {
                "email": signals.get("verified_email", False),
                "phone": signals.get("verified_phone", False),
                "linkedin": signals.get("linkedin_connected", False)
            }
        }

    @staticmethod
    def _generate_hiring_recommendation(
        candidate: Candidate,
        ranking_score: float,
        ranking_tier: str,
        behavioral_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate hiring recommendation based on multiple factors"""
        
        score_weight = ranking_score / 100.0 if ranking_score > 0 else 0
        
        # Calculate behavioral score (0-1)
        behavioral_score = 0.0
        if behavioral_signals["open_to_work"]:
            behavioral_score += 0.2
        if behavioral_signals["profile_completeness"] > 70:
            behavioral_score += 0.2
        if behavioral_signals["recruiter_response_rate"] and behavioral_signals["recruiter_response_rate"] > 0.7:
            behavioral_score += 0.2
        if behavioral_signals["offer_acceptance_rate"] and behavioral_signals["offer_acceptance_rate"] > 0.5:
            behavioral_score += 0.2
        if behavioral_signals["interview_completion_rate"] and behavioral_signals["interview_completion_rate"] > 0.5:
            behavioral_score += 0.2
        
        behavioral_score = min(behavioral_score, 1.0)
        
        # Combined score (70% ranking, 30% behavioral)
        combined_score = (score_weight * 0.7) + (behavioral_score * 0.3)
        
        # Determine recommendation level
        if combined_score >= 0.8 or ranking_tier == "Top Match":
            recommendation_level = "Strong Hire"
            confidence = 0.95 if combined_score >= 0.85 else 0.8
        elif combined_score >= 0.6 or ranking_tier == "Strong Match":
            recommendation_level = "Consider"
            confidence = 0.75 if combined_score >= 0.7 else 0.6
        elif combined_score >= 0.4 or ranking_tier == "Good Match":
            recommendation_level = "Maybe"
            confidence = 0.5
        else:
            recommendation_level = "Pass"
            confidence = 0.3
        
        # Build recommendation text
        recommendation_text = ComparisonService._build_recommendation_text(
            candidate, ranking_tier, behavioral_signals
        )
        
        return {
            "level": recommendation_level,
            "confidence": confidence,
            "score": combined_score,
            "reasoning": recommendation_text,
            "key_strengths": ComparisonService._identify_strengths(candidate, behavioral_signals),
            "key_concerns": ComparisonService._identify_concerns(candidate, behavioral_signals)
        }

    @staticmethod
    def _build_recommendation_text(
        candidate: Candidate,
        ranking_tier: str,
        behavioral_signals: Dict[str, Any]
    ) -> str:
        """Build human-readable recommendation text"""
        text_parts = []
        
        if ranking_tier == "Top Match":
            text_parts.append("Excellent skill and experience alignment with the role.")
        elif ranking_tier == "Strong Match":
            text_parts.append("Good skill and experience match with the role.")
        elif ranking_tier == "Good Match":
            text_parts.append("Moderate skill match; may need some upskilling.")
        else:
            text_parts.append("Skills and experience don't closely match role requirements.")
        
        if behavioral_signals["open_to_work"]:
            text_parts.append("Candidate is actively open to new opportunities.")
        
        if behavioral_signals["profile_completeness"] > 80:
            text_parts.append("Complete and well-maintained professional profile.")
        
        if behavioral_signals["interview_completion_rate"] and behavioral_signals["interview_completion_rate"] > 0.7:
            text_parts.append("Strong interview engagement history.")
        
        return " ".join(text_parts)

    @staticmethod
    def _identify_strengths(candidate: Candidate, behavioral_signals: Dict[str, Any]) -> List[str]:
        """Identify key strengths of the candidate"""
        strengths = []
        
        if candidate.experience_years and candidate.experience_years > 5:
            strengths.append("Extensive professional experience")
        
        if candidate.skills and len(candidate.skills) > 10:
            strengths.append("Diverse skill set")
        
        if candidate.education and len(candidate.education) > 1:
            strengths.append("Strong educational background")
        
        if behavioral_signals["open_to_work"]:
            strengths.append("Actively seeking opportunities")
        
        if behavioral_signals["profile_completeness"] > 80:
            strengths.append("Well-maintained professional presence")
        
        if behavioral_signals["github_activity_score"] and behavioral_signals["github_activity_score"] > 0.5:
            strengths.append("Active open-source contributor")
        
        if behavioral_signals["connection_count"] and behavioral_signals["connection_count"] > 200:
            strengths.append("Strong professional network")
        
        return strengths[:4]  # Return top 4 strengths

    @staticmethod
    def _identify_concerns(candidate: Candidate, behavioral_signals: Dict[str, Any]) -> List[str]:
        """Identify key concerns about the candidate"""
        concerns = []
        
        if not behavioral_signals["open_to_work"]:
            concerns.append("Not actively open to new opportunities")
        
        if behavioral_signals["profile_completeness"] < 50:
            concerns.append("Incomplete professional profile")
        
        if candidate.experience_years and candidate.experience_years < 1:
            concerns.append("Very junior; requires substantial mentoring")
        
        if behavioral_signals["interview_completion_rate"] and behavioral_signals["interview_completion_rate"] < 0.3:
            concerns.append("Poor interview follow-through history")
        
        if behavioral_signals["offer_acceptance_rate"] and behavioral_signals["offer_acceptance_rate"] < 0.3:
            concerns.append("Low offer acceptance rate")
        
        if behavioral_signals["notice_period_days"] and behavioral_signals["notice_period_days"] > 60:
            concerns.append(f"Requires {behavioral_signals['notice_period_days']} days notice")
        
        return concerns[:3]  # Return top 3 concerns

    @staticmethod
    def _calculate_summary(candidates_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary comparison metrics"""
        if not candidates_data:
            return {}

        summary = {
            "total_candidates": len(candidates_data),
            "highest_ranked": max(candidates_data, key=lambda x: x["ranking"]["score"]),
            "average_experience_years": sum(c["experience"]["years"] for c in candidates_data) / len(candidates_data),
            "average_ranking_score": sum(c["ranking"]["score"] for c in candidates_data) / len(candidates_data),
            "average_salary_expectation": 0,
            "recommendation_distribution": {}
        }

        # Calculate average salary
        salaries = [c.get("salary_expectation", 0) for c in candidates_data if c.get("salary_expectation")]
        if salaries:
            summary["average_salary_expectation"] = sum(salaries) / len(salaries)

        # Count recommendations
        for candidate in candidates_data:
            rec_level = candidate["recommendation"]["level"]
            summary["recommendation_distribution"][rec_level] = \
                summary["recommendation_distribution"].get(rec_level, 0) + 1

        # Identify best candidate for different criteria
        summary["best_experience"] = max(candidates_data, key=lambda x: x["experience"]["years"])
        summary["best_ranking"] = max(candidates_data, key=lambda x: x["ranking"]["score"])
        summary["most_engaged"] = max(
            candidates_data,
            key=lambda x: x["behavioral_signals"]["profile_completeness"]
        )

        return summary
