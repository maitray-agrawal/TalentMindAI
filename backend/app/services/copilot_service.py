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
        prompt_lower = prompt.lower()
        response_text = ""
        suggested_actions = []
        
        # 1. Fetch Candidate/Job context
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first() if candidate_id else None
        job = db.query(Job).filter(Job.id == job_id).first() if job_id else None

        # 2. Match intent: Outreach email drafting
        if "draft" in prompt_lower or "email" in prompt_lower or "outreach" in prompt_lower:
            if candidate and job:
                email = cls.generate_outreach_email(candidate, job)
                response_text = f"I've successfully generated a custom outreach email for **{candidate.name}** for the **{job.title}** role. You can edit the template below:"
                suggested_actions = [
                    {"label": "Send Email", "action": "send_email", "payload": {"candidate_id": candidate.id, "email": email}},
                    {"label": "Regenerate Email", "action": "chat", "payload": {"prompt": "Regenerate email with a more casual tone"}}
                ]
                return {
                    "response": response_text,
                    "email_draft": email,
                    "suggested_actions": suggested_actions
                }
            elif candidate:
                response_text = f"I can draft an email for **{candidate.name}**, but please select a job role context first so I can align the pitch."
                return {"response": response_text, "suggested_actions": []}
            else:
                response_text = "Who would you like me to draft an outreach email for? Please select a candidate profile first."
                return {"response": response_text, "suggested_actions": []}

        # 3. Match intent: Upskilling Roadmap
        elif "roadmap" in prompt_lower or "upskill" in prompt_lower or "gap" in prompt_lower:
            if candidate and job:
                roadmap = cls.generate_roadmap(candidate, job)
                response_text = f"Here is the strategic upskilling roadmap for **{candidate.name}** to bridge their gaps for the **{job.title}** role. This focuses on learning key missing skills: {', '.join([r['skill'] for r in roadmap])}."
                suggested_actions = [
                    {"label": "Export Roadmap", "action": "export_roadmap", "payload": {"candidate_id": candidate.id, "roadmap": roadmap}},
                    {"label": "Share with Candidate", "action": "share_roadmap", "payload": {"candidate_id": candidate.id}}
                ]
                return {
                    "response": response_text,
                    "roadmap": roadmap,
                    "suggested_actions": suggested_actions
                }
            elif candidate:
                response_text = f"I can build an upskilling roadmap for **{candidate.name}**, but please specify which Job Description you are matching them against."
                return {"response": response_text, "suggested_actions": []}
            else:
                response_text = "Please select a candidate to generate their customized upskilling roadmap."
                return {"response": response_text, "suggested_actions": []}

        # 4. Contextual Q&A
        elif "hello" in prompt_lower or "hi" in prompt_lower:
            response_text = "Hello! I am your TalentMind Recruiter Copilot. I can assist you with candidate matching, drafting outreach emails, analyzing skill gaps, and generating upskilling roadmaps. How can I help you today?"
            suggested_actions = [
                {"label": "Rank Candidates", "action": "rank_candidates", "payload": {}},
                {"label": "Analyze Skill Gaps", "action": "skill_gap", "payload": {}}
            ]
        elif candidate:
            response_text = (
                f"Checking files for candidate **{candidate.name}** ({candidate.title}). "
                f"They currently possess {len(candidate.skills)} skills, including {', '.join(candidate.skills[:4])}. "
                f"Their status is currently set to **{candidate.status}**. "
                f"How would you like me to assist with this candidate?"
            )
            suggested_actions = [
                {"label": "Draft Outreach Email", "action": "chat", "payload": {"prompt": f"Draft outreach email for {candidate.name}"}},
                {"label": "Skill Gap Analysis", "action": "skill_gap", "payload": {"candidate_id": candidate.id}}
            ]
        else:
            response_text = "I'm ready. Select a candidate or a job role from your dashboard, and I can generate candidate summaries, compare candidates, or draft outreach templates."
            suggested_actions = [
                {"label": "Show Top Ranked", "action": "show_rankings", "payload": {}}
            ]

        return {
            "response": response_text,
            "suggested_actions": suggested_actions
        }
