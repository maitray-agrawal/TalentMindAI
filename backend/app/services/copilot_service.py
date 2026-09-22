from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.job import Job

class CopilotService:
    @staticmethod
    def generate_outreach_email(candidate: Candidate, job: Job) -> str:
        return f"""Subject: Exciting Opportunity: {job.title} at Obsidian Network - Let's Connect!

Hi {candidate.name},

I hope this email finds you well. 

I came across your profile on our TalentMind platform and was incredibly impressed by your background. Specifically, your expertise in {", ".join((candidate.skills or [])[:3])} is a strong match for a critical role we are hiring for: {job.title} in our {job.department or "Engineering"} department.

At Obsidian Network, we are pioneering the next generation of intelligent tools, and we believe your {candidate.experience_years or 0.0} years of experience—especially your work as a {candidate.title or "specialist"}—would make you a stellar fit. 

This role is a {job.work_preference} position based out of {job.location}, offering you the chance to work alongside world-class engineers.

Would you be open to a brief 15-minute chat this week to discuss how your goals align with this opportunity? Let me know your availability or feel free to book a slot directly on my calendar.

Best regards,

Alex Chen
Senior Recruiter, Obsidian Network
alex.chen@obsidian.network
"""

    @staticmethod
    def generate_roadmap(candidate: Candidate, job: Job) -> List[Dict[str, Any]]:
        # Identify missing skills
        cand_skills = {s.lower().strip() for s in (candidate.skills or [])}
        missing_skills = [
            skill for skill in (job.required_skills or [])
            if skill.lower().strip() not in cand_skills
        ]

        if not missing_skills:
            # Add some advanced standard skills if there are no gaps
            missing_skills = ["Advanced MLOps Infrastructure", "Distributed Systems Scaling"]

        roadmap = []
        for i, skill in enumerate(missing_skills):
            phase = f"Phase {i+1}: {skill} Mastery"
            
            # Simple resources based on skill category
            if skill.lower() in ["docker", "kubernetes", "aws", "azure", "gcp", "devops"]:
                resources = ["AWS Certified DevOps Engineer Professional", "Kubernetes Academy - Hands-on GitOps"]
                project = f"Containerize & deploy a microservices pipeline to {skill} with automatic failover."
            elif skill.lower() in ["python", "tensorflow", "pytorch", "keras", "machine learning", "deep learning", "llm"]:
                resources = ["DeepLearning.AI: Generative AI with LLMs", "Fast.ai: Practical Deep Learning for Coders"]
                project = f"Build and fine-tune an open-source LLM for domain-specific text classification."
            else:
                resources = [f"Advanced {skill} Course on Coursera", f"Enterprise {skill} Design Patterns Cookbook"]
                project = f"Develop a production-ready repository demonstrating best practices in {skill}."

            roadmap.append({
                "phase": phase,
                "skill": skill,
                "estimated_duration": "4-6 weeks",
                "recommended_resources": resources,
                "hands_on_project": project
            })
        return roadmap

    @classmethod
    def chat(cls, prompt: str, candidate_id: Optional[int], job_id: Optional[int], db: Session) -> Dict[str, Any]:
        import os, json, urllib.request, urllib.error, logging, time
        logger = logging.getLogger(__name__)
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first() if candidate_id else None
        job = db.query(Job).filter(Job.id == job_id).first() if job_id else None

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set. Using Copilot fallback.")
            return cls._fallback_chat(prompt, candidate, job)

        # Build Context
        cand_context = "No candidate selected."
        if candidate:
            skills = ", ".join(candidate.skills or [])
            history = ""
            for role in (candidate.career_history or [])[:3]:
                history += f"- {role.get('title')} at {role.get('company')}\n"
            cand_context = f"Candidate Name: {candidate.name}\nTitle: {candidate.title}\nExperience: {candidate.experience_years} years\nLocation: {candidate.location}\nSkills: {skills}\nCareer History:\n{history}"

        job_context = "No job role selected."
        if job:
            reqs = ", ".join(job.required_skills or [])
            job_context = f"Job Title: {job.title}\nDepartment: {job.department}\nLocation: {job.location}\nRequired Skills: {reqs}\nDescription: {job.description[:500]}..."

        system_prompt = (
            "You are an expert technical recruiter and AI assistant (TalentMind Recruiter Copilot). "
            "Your task is to assist recruiters with outreach, summaries, interview questions, and gap analysis. "
            "Respond based on the provided Candidate and Job context. Output must be structured JSON.\n\n"
            f"--- CANDIDATE CONTEXT ---\n{cand_context}\n\n"
            f"--- JOB CONTEXT ---\n{job_context}\n\n"
            "INSTRUCTIONS:\n"
            "If the user asks for an outreach email, draft it and include it in 'email_draft'.\n"
            "If the user asks for an upskilling roadmap or gap analysis, structure a 2-3 step roadmap in 'roadmap'.\n"
            "Otherwise, respond conversationally in 'response' using Markdown.\n"
            "Always include 2-3 'suggested_actions' for the user to take next.\n\n"
            "JSON SCHEMA:\n"
            "{\n"
            '  "response": "Markdown formatted conversational response",\n'
            '  "email_draft": "Optional string containing the email draft, or empty string",\n'
            '  "roadmap": [ {"phase": "Phase 1", "skill": "Skill name", "estimated_duration": "2 weeks", "recommended_resources": ["link"], "hands_on_project": "project desc"} ],\n'
            '  "suggested_actions": [ {"label": "Button text", "action": "chat", "payload": {"prompt": "Quick prompt"}} ]\n'
            "}"
        )

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                req_data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=25) as response:
                    res_body = response.read().decode("utf-8")
                    data = json.loads(res_body)
                    
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                return {
                    "response": parsed.get("response", "I have processed your request."),
                    "email_draft": parsed.get("email_draft", ""),
                    "roadmap": parsed.get("roadmap", []),
                    "suggested_actions": parsed.get("suggested_actions", [])
                }
            except Exception as e:
                logger.error(f"Groq Copilot API error (attempt {attempt+1}): {e}")
                if attempt == max_retries - 1:
                    return cls._fallback_chat(prompt, candidate, job)
                time.sleep(1.5)

        return cls._fallback_chat(prompt, candidate, job)

    @classmethod
    def _fallback_chat(cls, prompt: str, candidate: Optional[Candidate], job: Optional[Job]) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        response_text = ""
        suggested_actions = []
        email = ""
        roadmap = []

        if "draft" in prompt_lower or "email" in prompt_lower:
            if candidate and job:
                email = cls.generate_outreach_email(candidate, job)
                response_text = f"I've generated a custom outreach email for **{candidate.name}** for the **{job.title}** role."
                suggested_actions = [{"label": "Send Email", "action": "send_email", "payload": {"candidate_id": candidate.id, "email": email}}]
            elif candidate:
                response_text = "Please select a job role context first so I can align the pitch."
            else:
                response_text = "Who would you like me to draft an outreach email for? Please select a candidate."
        elif "roadmap" in prompt_lower or "gap" in prompt_lower:
            if candidate and job:
                roadmap = cls.generate_roadmap(candidate, job)
                response_text = f"Here is the upskilling roadmap for **{candidate.name}** to match the **{job.title}** role."
            else:
                response_text = "Please select a candidate and job to generate a roadmap."
        else:
            response_text = "Hello! I am your Recruiter Copilot (Fallback Mode). How can I help you today?"
            
        return {
            "response": response_text,
            "email_draft": email,
            "roadmap": roadmap,
            "suggested_actions": suggested_actions
        }
