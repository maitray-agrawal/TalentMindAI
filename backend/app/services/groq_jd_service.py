import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class GroqJDService:
    @staticmethod
    def analyze_jd(text: str) -> Dict[str, Any]:
        """
        Parses a job description using Groq API via standard urllib.
        Returns a dictionary with:
          required_skills (list of strings)
          preferred_skills (list of strings)
          experience_required (float)
          education_requirements (list of strings)
          disqualifiers (list of strings)
        
        If the API is unavailable, fails, or GROQ_API_KEY is not set,
        falls back to JDAnalyzerService.analyze_detailed(text).
        """
        from app.services.jd_analyzer import JDAnalyzerService

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY env var not set. Falling back to heuristic JDAnalyzerService.")
            return GroqJDService._fallback(text)

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TalentMindAI/1.0"
        }
        
        prompt = (
            "You are an expert technical recruiter and AI assistant. Your task is to analyze the following job description "
            "and extract structural requirement fields in JSON format.\n\n"
            "Job Description:\n"
            f"{text}\n\n"
            "Return a JSON object with EXACTLY the following keys (do not include any other markdown formatting or text):\n"
            "{\n"
            '  "required_skills": ["skill1", "skill2", ...],  // Must be list of strings. Extract specific technical skills.\n'
            '  "preferred_skills": ["skill1", "skill2", ...], // Must be list of strings. Nice-to-have skills.\n'
            '  "experience_required": 5.0,                   // Must be a float representing the minimum years of experience required.\n'
            '  "education_requirements": ["req1", ...],        // Must be list of strings describing educational criteria.\n'
            '  "disqualifiers": ["disq1", ...]               // Must be list of strings describing disqualifying factors.\n'
            "}"
        )

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional recruiting analyzer that extracts structured details from job descriptions. Always output valid JSON."
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
        backoff = 3.0
        for attempt in range(max_retries):
            try:
                req_data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    status_code = response.getcode()
                    if status_code != 200:
                        raise ValueError(f"HTTP response status code: {status_code}")
                    
                    res_body = response.read().decode("utf-8")
                    data = json.loads(res_body)
                
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                # Extract and validate fields
                required_skills = parsed.get("required_skills", [])
                preferred_skills = parsed.get("preferred_skills", [])
                experience_required = parsed.get("experience_required", 0.0)
                education_requirements = parsed.get("education_requirements", [])
                disqualifiers = parsed.get("disqualifiers", [])
                
                # Type correction/coercion
                if not isinstance(required_skills, list):
                    required_skills = [str(required_skills)] if required_skills else []
                else:
                    required_skills = [str(s) for s in required_skills]
                    
                if not isinstance(preferred_skills, list):
                    preferred_skills = [str(preferred_skills)] if preferred_skills else []
                else:
                    preferred_skills = [str(s) for s in preferred_skills]
                    
                try:
                    experience_required = float(experience_required)
                except (ValueError, TypeError):
                    experience_required = 0.0
                    
                if not isinstance(education_requirements, list):
                    education_requirements = [str(education_requirements)] if education_requirements else []
                else:
                    education_requirements = [str(e) for e in education_requirements]
                    
                if not isinstance(disqualifiers, list):
                    disqualifiers = [str(disqualifiers)] if disqualifiers else []
                else:
                    disqualifiers = [str(d) for d in disqualifiers]
                    
                return {
                    "required_skills": required_skills,
                    "preferred_skills": preferred_skills,
                    "experience_required": experience_required,
                    "education_requirements": education_requirements,
                    "disqualifiers": disqualifiers
                }
                
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    sleep_time = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited (429) parsing JD. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Error calling Groq API (attempt {attempt+1}/{max_retries}): {e}. Falling back.")
                    if attempt == max_retries - 1:
                        return GroqJDService._fallback(text)
            except Exception as e:
                logger.error(f"Error calling Groq API (attempt {attempt+1}/{max_retries}): {e}. Falling back.")
                if attempt == max_retries - 1:
                    return GroqJDService._fallback(text)

    @staticmethod
    def _fallback(text: str) -> Dict[str, Any]:
        from app.services.jd_analyzer import JDAnalyzerService
        heuristic = JDAnalyzerService.analyze_detailed(text)
        return {
            "required_skills": heuristic.get("required_skills", []),
            "preferred_skills": heuristic.get("preferred_skills", []),
            "experience_required": float(heuristic.get("experience_required", 0.0) or 0.0),
            "education_requirements": heuristic.get("education_requirements", []),
            "disqualifiers": heuristic.get("disqualifiers", [])
        }
