import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
from app.models.candidate import Candidate
from app.models.job import Job
from app.config import settings

class RankerService:
    _vectorizer_cache = {}

    @classmethod
    def get_job_vectorizer(cls, job: Job):
        job_id = getattr(job, "id", None) or f"{job.title}_{'-'.join(job.required_skills or [])}"
        if job_id not in cls._vectorizer_cache:
            job_skills_str = " ".join(job.required_skills or [])
            job_corpus = f"{job.title or ''} {job_skills_str}"
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
            job_tfidf = vectorizer.fit_transform([job_corpus])
            cls._vectorizer_cache[job_id] = (vectorizer, job_tfidf)
        return cls._vectorizer_cache[job_id]

    @staticmethod
    def calculate_match(candidate: Candidate, job: Job) -> Tuple[float, Dict[str, Any], str]:
        # Clean inputs
        job_title_lower = (job.title or "").lower()
        cand_title_lower = (candidate.title or "").lower()
        cand_resume_lower = (candidate.resume_text or "").lower()
        
        # 1. Text Similarity using TF-IDF and Cosine Similarity
        # Combine candidate data into a single corpus string
        cand_skills_str = " ".join(candidate.skills or [])
        cand_corpus = f"{candidate.title or ''} {cand_skills_str}"
        
        # Check for retrieval keywords in candidate's resume/history
        retrieval_keywords = [
            "ranking", "recommendation", "recommender", "search engine", "information retrieval",
            "retrieval system", "matching engine", "hybrid search", "semantic search", "vector search",
            "dense retrieval", "learning to rank", "ltr", "embeddings-based", "vector database",
            "faiss", "pinecone", "milvus", "qdrant", "weaviate", "elasticsearch", "opensearch", "bm25"
        ]
        
        # Check in career history descriptions specifically, and fallback to resume text
        has_retrieval_experience = False
        career_desc_text = ""
        if candidate.career_history:
            for job_history in candidate.career_history:
                career_desc_text += " " + (job_history.get("description") or "").lower()
                
        # Define non-technical keywords for early filtering
        non_tech_kws = ["marketing", "hr", "operations", "graphic", "designer", "artist", "illustrator", "creative", "accountant", "customer support", "support", "writer", "mechanical", "civil", "chemical"]
        
        if any(kw in career_desc_text for kw in retrieval_keywords) or any(kw in cand_resume_lower for kw in retrieval_keywords):
            # To avoid false positives on non-technical candidates (e.g. Graphic Designer with RAG side projects),
            # we only set has_retrieval_experience if they are in a technical software/data/AI role
            if not any(nt in cand_title_lower for nt in non_tech_kws):
                has_retrieval_experience = True
                
        # TF-IDF calculation using cached job vectorizer
        try:
            vectorizer, job_tfidf = RankerService.get_job_vectorizer(job)
            cand_tfidf = vectorizer.transform([cand_corpus])
            raw_text_sim = float(cosine_similarity(cand_tfidf, job_tfidf)[0][0])
            # Calibration: scale up TF-IDF cosine similarity as it rarely reaches 1.0 natively
            text_sim = min(1.0, raw_text_sim * 1.5)
        except Exception:
            text_sim = 0.0
            
        # Boost text similarity if they have proven retrieval experience
        if has_retrieval_experience:
            text_sim = min(1.0, text_sim + 0.15)

        # 2. Skills Match (Synonym & Category mapping + Exact check)
        cand_skills_set = {s.lower().strip() for s in (candidate.skills or [])}
        job_skills_set = {s.lower().strip() for s in (job.required_skills or [])}
        
        matched_skills = []
        missing_skills = []
        
        for skill in job.required_skills or []:
            if skill.lower().strip() in cand_skills_set:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        # Define semantic skill categories
        categories = {
            "vector_dbs": ["pinecone", "milvus", "qdrant", "weaviate", "faiss", "vector databases", "vector search", "dense retrieval"],
            "search_retrieval": ["elasticsearch", "opensearch", "hybrid search", "embeddings-based retrieval", "information retrieval", "search", "retrieval"],
            "ranking_recommendation": ["ranking systems", "ranking", "matching", "recommendation systems", "recommendation", "learning-to-rank", "learning to rank", "ltr", "xgboost", "lightgbm"],
            "evaluation": ["evaluation frameworks", "ab test", "a/b test", "ndcg", "mrr", "map", "evaluation"],
            "embeddings_llms": ["openai embeddings", "bge", "e5", "sentence-transformers", "sentence transformers", "embeddings", "hugging face transformers", "transformers", "llm", "peft", "lora", "qlora"],
            "programming": ["python", "programming", "software development", "go", "rust", "c++", "java"]
        }
        
        # Check which categories are matched
        matched_categories_count = 0
        for cat_name, cat_skills in categories.items():
            # Check if candidate has any skill in this category
            if any(s in cand_skills_set or any(s in cs.lower() for cs in candidate.skills or []) for s in cat_skills):
                matched_categories_count += 1
                
        category_match_ratio = matched_categories_count / len(categories)
        
        # Exact match ratio
        exact_match_ratio = len(matched_skills) / len(job_skills_set) if len(job_skills_set) > 0 else 1.0
        
        # Combine category match and exact match (80% category, 20% exact match to reward exact fits)
        skills_match_ratio = (category_match_ratio * 0.8) + (exact_match_ratio * 0.2)
        
        # Boost skills score if they have proven retrieval experience in career history
        if has_retrieval_experience:
            skills_match_ratio = min(1.0, skills_match_ratio + 0.20)
            
        skills_match_ratio = max(0.0, min(1.0, skills_match_ratio))

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
            cand_loc = (candidate.location or "").lower()
            job_loc = (job.location or "").lower()
            if cand_loc == job_loc or cand_loc in job_loc or job_loc in cand_loc:
                location_score = 1.0
            elif candidate.work_preference and candidate.work_preference.lower() == "remote":
                location_score = 0.2
            elif candidate.work_preference and candidate.work_preference.lower() in ["flexible", "hybrid", "onsite"]:
                location_score = 0.8  # Relocation / flex candidate
            else:
                location_score = 0.5
        else:
            if candidate.work_preference and candidate.work_preference.lower() == "remote":
                location_score = 1.0
            else:
                location_score = 0.9

        # 5. Education Match
        edu_score = 1.0
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
                
        if not edu_reqs or any("not specified" in r.lower() for r in edu_reqs):
            edu_score = 1.0
        else:
            cand_edu_list = candidate.education or []
            if not cand_edu_list:
                edu_score = 0.5
            else:
                best_match = 0.5
                for edu in cand_edu_list:
                    inst = (edu.get("institution") or "").lower()
                    deg = (edu.get("degree") or "").lower()
                    field = (edu.get("field_of_study") or "").lower()
                    tier = (edu.get("tier") or "").lower()
                    
                    match_val = 0.6
                    
                    # Check tier 1
                    if tier == "tier_1" or "tier-1" in tier or "stanford" in inst or "mit" in inst or "harvard" in inst or "iit" in inst or "bits" in inst:
                        match_val += 0.2
                        
                    # Check field match
                    if "computer science" in field or "cs" in field or "engineering" in field or "ai" in field or "ml" in field or "information technology" in field or "data" in field:
                        if any(kw in job_title_lower for kw in ["engineer", "developer", "scientist", "tech", "ai", "ml", "specialist", "programmer", "architect", "lead"]):
                            match_val += 0.2
                            
                    # Check degree level
                    if "ph.d" in deg or "phd" in deg or "doctor" in deg:
                        match_val += 0.2
                    elif "master" in deg or "m.s" in deg or "m.tech" in deg or "mca" in deg:
                        match_val += 0.1
                        
                    best_match = max(best_match, min(1.0, match_val))
                edu_score = best_match

        # 6. Behavioral Signals Match
        signals = candidate.redrob_signals or {}
        completeness = float(signals.get("profile_completeness_score", 50.0)) / 100.0
        open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.5
        github = float(signals.get("github_activity_score", 50.0)) / 100.0
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
        
        # 8. Role Fit Multiplier Calculation (when job is technical)
        role_fit_multiplier = 1.0
        is_job_technical = any(kw in job_title_lower for kw in ["engineer", "developer", "scientist", "architect", "programmer", "tech lead", "systems", "analyst", "ai", "ml"])
        
        if is_job_technical:
            # Check for non-technical fields
            non_tech_keywords = [
                "marketing", "hr", "human resources", "recruiter", "operations", 
                "accountant", "accounting", "finance", "mechanical", "civil", 
                "chemical", "industrial", "customer support", "support", 
                "writer", "content", "sales", "business development",
                "designer", "graphic", "artist", "illustrator", "creative"
            ]
            
            # Determine if the job itself is AI/Search/Retrieval/Recommendation
            is_job_search_or_ai = any(kw in job_title_lower for kw in ["ai", "ml", "machine learning", "deep learning", "nlp", "search", "retrieval", "ranking", "recommendation"])
            
            # Check for specific role classes
            if any(nt in cand_title_lower for nt in non_tech_keywords) or "operations manager" in cand_title_lower or "project manager" in cand_title_lower or "scrum master" in cand_title_lower or "product owner" in cand_title_lower or "product manager" in cand_title_lower:
                role_fit_multiplier = 0.15  # Heavy penalty for completely non-technical roles
            elif any(ai_kw in cand_title_lower for ai_kw in ["ai", "ml", "machine learning", "deep learning", "nlp", "computer vision", "recommendation", "search", "retrieval", "ranking", "lead scientist"]):
                role_fit_multiplier = 1.0  # Perfect direct match
            elif any(swe_kw in cand_title_lower for swe_kw in ["software engineer", "developer", "programmer", "architect", "tech lead", "systems engineer", "backend", "frontend", "full stack"]):
                # If it's a search/AI job and they lack retrieval/ranking experience, apply a slight penalty
                if is_job_search_or_ai and not has_retrieval_experience:
                    role_fit_multiplier = 0.95
                else:
                    role_fit_multiplier = 1.0
            elif any(ops_kw in cand_title_lower for ops_kw in ["devops", "qa", "quality assurance", "test", "cloud"]):
                if is_job_search_or_ai and not has_retrieval_experience:
                    role_fit_multiplier = 0.80
                else:
                    role_fit_multiplier = 0.95
            elif "business analyst" in cand_title_lower:
                role_fit_multiplier = 0.60
                
        # Apply role fit multiplier
        final_score = final_score * role_fit_multiplier

        # 9. Disqualifier Penalties
        # A. Consulting-only backgrounds (TCS, Infosys, Wipro, etc.)
        consulting_companies = {"tcs", "infosys", "wipro", "hcl", "cognizant", "accenture", "capgemini", "tech mahindra", "mindtree", "tata consultancy services", "cts"}
        if candidate.career_history:
            companies = {job_history.get("company", "").lower().strip() for job_history in candidate.career_history}
            # Clean up company names (e.g. "tcs limited" -> "tcs")
            cleaned_companies = set()
            for c in companies:
                c_clean = re.sub(r"\b(ltd|limited|inc|corp|services|technologies)\b", "", c).strip()
                cleaned_companies.add(c_clean)
            
            # If they have worked and ALL their companies are in consulting
            if cleaned_companies and cleaned_companies.issubset(consulting_companies):
                final_score = final_score * 0.90  # 10% penalty

        # B. Title-chasers (changing companies every 1.5 years or less)
        # Average tenure under 15 months
        if candidate.career_history and len(candidate.career_history) >= 2:
            total_months = sum(job_history.get("duration_months") or 0 for job_history in candidate.career_history)
            if total_months > 0:
                avg_tenure_months = total_months / len(candidate.career_history)
                if avg_tenure_months < 15.0:
                    final_score = final_score * 0.95  # 5% penalty

        # C. LangChain/OpenAI wrapper only (no core ML/Search foundations)
        has_wrapper_skills = any(s in cand_skills_set for s in ["langchain", "openai", "openai embeddings"])
        has_core_foundations = any(s in cand_skills_set or any(s in cs.lower() for cs in candidate.skills or []) for s in [
            "pytorch", "tensorflow", "scikit-learn", "xgboost", "lightgbm", "search", "retrieval", 
            "ranking", "recommendation", "vector databases", "faiss", "pinecone", "milvus", "qdrant", "weaviate"
        ])
        if has_wrapper_skills and not has_core_foundations:
            final_score = final_score * 0.90  # 10% penalty

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
            "experience_difference_years": round(exp_diff, 1),
            "role_fit_multiplier": round(role_fit_multiplier, 2),
            "has_retrieval_experience": has_retrieval_experience
        }

        return final_score, explanation, tier
