import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models.candidate import Candidate
from app.models.job import Job

logger = logging.getLogger(__name__)

class GroqReranker:
    @staticmethod
    def evaluate_candidate(candidate: Candidate, job: Job, api_key: str) -> Tuple[float, str]:
        """
        Evaluates a candidate profile against a job description using Groq API.
        Returns a tuple: (score, reasoning) where score is 0-100.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TalentMindAI/1.0"
        }

        # Format candidate profile
        skills_str = ", ".join(candidate.skills or [])
        signals_str = json.dumps(candidate.redrob_signals or {}, indent=2)
        
        # Summarize career history descriptions
        career_summary = []
        for role in (candidate.career_history or []):
            role_title = role.get("title", "Unknown Role")
            role_company = role.get("company", "")
            role_desc = (role.get("description") or "")[:200]
            career_summary.append(f"- {role_title} at {role_company}: {role_desc}...")
        career_history_str = "\n".join(career_summary) if career_summary else "No career history details."

        resume_snippet = (candidate.resume_text or "")[:1000]

        prompt = (
            "You are an expert recruiter conducting a second-stage candidate evaluation for a critical technical role.\n"
            "Analyze the candidate profile against the Job Description and score their suitability.\n\n"
            "JOB DESCRIPTION:\n"
            f"Title: {job.title}\n"
            f"Description: {job.description[:1000]}...\n\n"
            "CANDIDATE PROFILE:\n"
            f"Candidate ID: {candidate.candidate_id}\n"
            f"Title: {candidate.title}\n"
            f"Skills: {skills_str}\n"
            f"Experience Years: {candidate.experience_years}\n"
            f"Career History:\n{career_history_str}\n"
            f"Behavioral & Cognitive Signals (Redrob):\n{signals_str}\n"
            f"Resume Text Snippet:\n{resume_snippet}\n\n"
            "CRITERIA TO EVALUATE:\n"
            "1. Skill Alignment: How well do the candidate's skills align with the required skills of the role?\n"
            "2. Experience Relevance: Is their background and seniority level suitable for the role?\n"
            "3. Retrieval/Search Expertise: Do they have hands-on experience with recommendation systems, vector search, RAG, hybrid search, ranking, or information retrieval?\n"
            "4. Behavioral Signals: Evaluate their cognitive/behavioral attributes (e.g., from Redrob signals, work stability/hopping, etc.).\n\n"
            "OUTPUT FORMAT:\n"
            "Return a JSON object with EXACTLY the following keys (do not include other markdown formatting or text):\n"
            "{\n"
            '  "score": 85.0,     // A float or integer from 0.0 to 100.0 representing suitability.\n'
            '  "reasoning": "Reason for score based on the four criteria." // Under 150 words.\n'
            "}"
        )

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional recruiting evaluator. Always output valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        import time
        max_retries = 5
        backoff = 2.0
        for attempt in range(max_retries):
            try:
                req_data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.getcode() != 200:
                        raise ValueError(f"HTTP response status code: {response.getcode()}")
                    
                    res_body = response.read().decode("utf-8")
                    data = json.loads(res_body)
                
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                score = float(parsed.get("score", 0.0))
                reasoning = str(parsed.get("reasoning", ""))
                return score, reasoning
                
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    sleep_time = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited (429) evaluating candidate {candidate.candidate_id}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Error evaluating candidate {candidate.candidate_id} (attempt {attempt+1}/{max_retries}): {e}")
                    raise e
            except Exception as e:
                logger.error(f"Error evaluating candidate {candidate.candidate_id} (attempt {attempt+1}/{max_retries}): {e}")
                raise e

    @classmethod
    def rerank_candidates(cls, candidate_results: List[Dict[str, Any]], job: Job) -> List[Dict[str, Any]]:
        """
        Reranks the top candidate results using parallelized Groq LLM evaluation.
        Inputs:
          candidate_results: list of dicts with {"candidate": Candidate, "score": float, "explanation": dict}
        Returns:
          A new list of results where the top 50 candidates are re-ranked using:
          final_score = 0.7 * original_score + 0.3 * GroqScore
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY env var not set. Skipping Groq recruiter reranking.")
            return candidate_results

        # Only evaluate the top 50 candidates
        top_n = 50
        to_rerank = candidate_results[:top_n]
        remaining = candidate_results[top_n:]

        print(f"Reranking top {len(to_rerank)} candidates using Groq Recruiter Rerank...")

        reranked_results = []
        
        # Parallelize the 50 API calls
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_cand = {
                executor.submit(cls.evaluate_candidate, r["candidate"], job, api_key): r 
                for r in to_rerank
            }
            
            for future in as_completed(future_to_cand):
                result_entry = future_to_cand[future]
                candidate = result_entry["candidate"]
                original_score = result_entry["score"]
                explanation = result_entry["explanation"]
                
                try:
                    groq_score, groq_reasoning = future.result()
                    # Combine scores: 0.7 * original + 0.3 * Groq
                    combined_score = 0.7 * original_score + 0.3 * groq_score
                    
                    # Update explanation with Groq details
                    updated_explanation = explanation.copy()
                    updated_explanation["groq_score"] = groq_score
                    updated_explanation["groq_reasoning"] = groq_reasoning
                    updated_explanation["original_heuristic_score"] = original_score
                    
                    reranked_results.append({
                        "candidate": candidate,
                        "score": combined_score,
                        "explanation": updated_explanation
                    })
                except Exception as e:
                    # Fallback to original score for this candidate on failure
                    logger.warning(f"Fallback for {candidate.candidate_id} due to evaluation error: {e}")
                    reranked_results.append(result_entry)

        # Sort the re-ranked top 50 by combined score descending
        reranked_results.sort(key=lambda x: x["score"], reverse=True)

        # Combine back with the remaining results
        final_results = reranked_results + remaining
        return final_results
