from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.services.ranker_service import RankerService

def seed_db():
    # Recreate tables just to be sure
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Candidate).first() is not None:
        print("Database already seeded.")
        db.close()
        return

    print("Seeding database with TalentMind mockup candidates and roles...")

    # 1. Add Jobs
    jobs = [
        Job(
            id=1,
            title="Lead AI Research Scientist",
            department="Engineering",
            location="London",
            work_preference="Hybrid",
            description="We are seeking an outstanding Lead AI Research Scientist to join our London Engineering team. You will lead research in large language models, reinforcement learning, and advanced AI systems. Required skills: Python, PyTorch, Deep Learning, NLP, LLM. Required experience: 6+ years.",
            required_skills=["Python", "PyTorch", "Deep Learning", "NLP", "LLM"],
            experience_required=6.0,
            status="Active",
            priority="High"
        ),
        Job(
            id=2,
            title="Product Designer (UX)",
            department="Creative",
            location="Remote",
            work_preference="Remote",
            description="Looking for a Product Designer (UX) to craft premium dark mode user interfaces, glassmorphism aesthetics, and responsive micro-interactions. Experience with Figma, React, CSS, UX, and UI Design is highly preferred. Required experience: 3+ years.",
            required_skills=["React", "CSS", "HTML", "UX", "UI Design"],
            experience_required=3.0,
            status="Active",
            priority="Medium"
        ),
        Job(
            id=3,
            title="Senior Frontend Engineer",
            department="Engineering",
            location="Remote",
            work_preference="Remote",
            description="Join our team building the Obsidian Intelligence Platform. We need a Senior Frontend Engineer with deep experience in TypeScript, React, Next.js, and CSS layout engines. Required experience: 5+ years.",
            required_skills=["React", "TypeScript", "Next.js", "CSS", "Git"],
            experience_required=5.0,
            status="Active",
            priority="High"
        ),
        Job(
            id=4,
            title="Sr. DevOps Engineer",
            department="Engineering",
            location="London",
            work_preference="Hybrid",
            description="Seeking a Senior DevOps Engineer to manage and scale our Kubernetes infrastructure on AWS. Strong experience with CI/CD pipelines and Terraform. Required experience: 5+ years.",
            required_skills=["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"],
            experience_required=5.0,
            status="Active",
            priority="Medium"
        )
    ]

    for j in jobs:
        db.add(j)
    db.commit()

    # 2. Add Candidates
    candidates = [
        Candidate(
            id=1,
            name="Elena Rodriguez",
            email="elena.r@obsidian.network",
            title="Senior Frontend Engineer",
            location="London",
            work_preference="Hybrid",
            experience_years=6.0,
            skills=["React", "TypeScript", "Next.js", "CSS", "Git", "JavaScript", "HTML"],
            resume_text="Elena is a passionate Frontend Engineer with 6 years of experience building high-scale React applications. Expert in TypeScript and custom design systems. Willing to work hybrid in London.",
            status="Screening",
            salary_expectation=120000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        ),
        Candidate(
            id=2,
            name="Alexander Vance",
            email="a.vance@systems.io",
            title="Director of Engineering",
            location="London",
            work_preference="Hybrid",
            experience_years=12.0,
            skills=["Python", "PyTorch", "Docker", "Kubernetes", "AWS", "Deep Learning", "NLP"],
            resume_text="Alexander Vance is an industry-veteran Systems Architect and former Director of Engineering. Over 12 years of experience leading engineering teams, deploying complex MLOps frameworks, and writing high-performance backend systems in Python.",
            status="Interview",
            salary_expectation=190000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        ),
        Candidate(
            id=3,
            name="Sarah J.",
            email="sarah.jones@cloudtech.com",
            title="Frontend Developer",
            location="Remote",
            work_preference="Remote",
            experience_years=3.0,
            skills=["React", "JavaScript", "HTML", "CSS"],
            resume_text="Sarah is a mid-level Frontend Developer focusing on clean UI code, web design basics, and React applications. Looking to grow into TypeScript and Next.js.",
            status="Sourcing",
            salary_expectation=85000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        ),
        Candidate(
            id=4,
            name="Marcus Holloway",
            email="marcus.h@techcorp.com",
            title="Senior Frontend Architect",
            location="Remote",
            work_preference="Remote",
            experience_years=8.0,
            skills=["React", "TypeScript", "Next.js", "Git", "Docker"],
            resume_text="Marcus has 8 years of engineering experience with a deep focus on React architecture, Next.js setups, and containerization. Excellent team player.",
            status="Screening",
            salary_expectation=140000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        ),
        Candidate(
            id=5,
            name="David Chen",
            email="david.chen@ai-labs.org",
            title="Lead AI Scientist",
            location="London",
            work_preference="Hybrid",
            experience_years=7.0,
            skills=["Python", "PyTorch", "Deep Learning", "NLP", "LLM", "Docker"],
            resume_text="David is a senior AI research scientist specializing in natural language processing and transformer models. Deep understanding of model deployment.",
            status="Interview",
            salary_expectation=160000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        ),
        Candidate(
            id=6,
            name="Lila Ames",
            email="lila.ames@creativemind.co",
            title="Lead UX/UI Designer",
            location="Remote",
            work_preference="Remote",
            experience_years=5.0,
            skills=["React", "CSS", "HTML", "UX", "UI Design"],
            resume_text="Lila is an expert digital product designer with a history of shipping high-end web and mobile products. Expert in CSS, UI layouts, Figma, and React.",
            status="Offer",
            salary_expectation=105000,
            avatar_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI"
        )
    ]

    for c in candidates:
        db.add(c)
    db.commit()

    # 3. Precalculate Rankings
    print("Precalculating rankings for seeded data...")
    db_jobs = db.query(Job).all()
    db_candidates = db.query(Candidate).all()
    for job in db_jobs:
        for candidate in db_candidates:
            score, explanation, tier = RankerService.calculate_match(candidate, job)
            ranking = Ranking(
                candidate_id=candidate.id,
                job_id=job.id,
                match_score=score,
                explanation=explanation,
                tier=tier
            )
            db.add(ranking)
            
    db.commit()
    print("Database seeding completed successfully.")
    db.close()

if __name__ == "__main__":
    seed_db()
