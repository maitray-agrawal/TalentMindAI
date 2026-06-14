import sys
import os
from pathlib import Path
import unittest

# Add backend to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.schemas.job import JobCreate
from app.routes.candidates import create_candidate, read_candidates, read_candidate, update_candidate, delete_candidate
from app.routes.jobs import create_job, read_jobs, read_job
from app.routes.ranking import calculate_job_rankings, get_job_rankings, get_candidate_skill_gap
from app.routes.copilot import chat_with_copilot, ChatRequest
from app.services.jd_analyzer import JDAnalyzerService
from app.services.ranker_service import RankerService

# Set up test database
TEST_DATABASE_URL = "sqlite:///./test_talentmind.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DirectBackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_talentmind.db"):
            try:
                os.remove("./test_talentmind.db")
            except Exception:
                pass

    def test_1_jd_analyzer_service(self):
        desc = "Lead AI Scientist\nLocation: London\nWork preference: Hybrid\nRequirements: Python, PyTorch, Deep Learning\n6+ years experience"
        result = JDAnalyzerService.analyze(desc)
        self.assertEqual(result["title"], "Lead AI Scientist")
        self.assertEqual(result["location"], "London")
        self.assertEqual(result["work_preference"], "Hybrid")
        self.assertIn("Python", result["required_skills"])
        self.assertIn("PyTorch", result["required_skills"])
        self.assertEqual(result["experience_required"], 6.0)

    def test_2_candidate_crud_routes(self):
        # Create candidate
        cand_in = CandidateCreate(
            name="Test User",
            email="testuser@talentmind.io",
            title="DevOps Specialist",
            location="Remote",
            work_preference="Remote",
            experience_years=4.0,
            skills=["Docker", "AWS"],
            resume_text="Experienced devops guy.",
            status="Sourcing",
            salary_expectation=90000
        )
        cand = create_candidate(candidate_in=cand_in, db=self.db)
        self.assertEqual(cand.name, "Test User")
        self.assertEqual(cand.email, "testuser@talentmind.io")
        self.cand_id = cand.id

        # Read candidate
        fetched = read_candidate(candidate_id=self.cand_id, db=self.db)
        self.assertEqual(fetched.name, "Test User")

        # Update candidate
        cand_up = CandidateUpdate(status="Interview")
        updated = update_candidate(candidate_id=self.cand_id, candidate_in=cand_up, db=self.db)
        self.assertEqual(updated.status, "Interview")

        # List candidates
        candidates = read_candidates(db=self.db)
        self.assertGreaterEqual(len(candidates), 1)

    def test_3_job_crud_routes(self):
        # Create job
        job_in = JobCreate(
            title="DevOps Engineer",
            description="Docker, AWS, Kubernetes, 5 years experience. London.",
            experience_required=0.0, # Will trigger auto-analyzer
            required_skills=[]
        )
        job = create_job(job_in=job_in, db=self.db)
        self.assertEqual(job.title, "DevOps Engineer")
        self.assertIn("Docker", job.required_skills)
        self.assertEqual(job.experience_required, 5.0)
        self.job_id = job.id

    def test_4_ranking_and_skill_gap_routes(self):
        # Set up a candidate and a job for ranking test
        c1 = Candidate(
            name="Elena Rodriguez",
            email="elena.r@obsidian.network",
            title="Senior Frontend Engineer",
            location="London",
            work_preference="Hybrid",
            experience_years=6.0,
            skills=["React", "TypeScript", "Next.js", "CSS", "Git"],
            resume_text="Elena is a passionate Frontend Engineer with 6 years of experience."
        )
        j1 = Job(
            title="Senior Frontend Engineer",
            department="Engineering",
            location="London",
            work_preference="Hybrid",
            description="Looking for Frontend Engineer with React, TypeScript. London.",
            required_skills=["React", "TypeScript", "Next.js"],
            experience_required=5.0
        )
        self.db.add(c1)
        self.db.add(j1)
        self.db.commit()

        # Execute ranking
        rankings = calculate_job_rankings(job_id=j1.id, db=self.db)
        self.assertGreaterEqual(len(rankings), 1)
        self.assertGreater(rankings[0].match_score, 50.0)

        # Get rankings list
        list_rankings = get_job_rankings(job_id=j1.id, db=self.db)
        self.assertEqual(len(list_rankings), len(rankings))

        # Get skill gap analysis
        gap = get_candidate_skill_gap(candidate_id=c1.id, job_id=j1.id, db=self.db)
        self.assertEqual(gap.candidate_name, "Elena Rodriguez")
        self.assertGreaterEqual(len(gap.upskilling_roadmap), 1)

    def test_5_copilot_chat_route(self):
        # We need a candidate and job in the database
        cand = self.db.query(Candidate).filter(Candidate.name == "Elena Rodriguez").first()
        job = self.db.query(Job).filter(Job.title == "Senior Frontend Engineer").first()
        
        request = ChatRequest(
            prompt="Draft an outreach email to Elena Rodriguez for the Senior Frontend Engineer role",
            candidate_id=cand.id,
            job_id=job.id
        )
        
        result = chat_with_copilot(payload=request, db=self.db)
        self.assertIn("response", result)
        self.assertIn("email_draft", result)
        self.assertIn("Elena", result["email_draft"])

if __name__ == "__main__":
    unittest.main()
