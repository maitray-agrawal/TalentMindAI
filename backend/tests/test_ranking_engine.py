import sys
import os
import time
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.database import Base, get_db
from app.models.candidate import Candidate

# Use a separate test database for these ranking tests
TEST_DB_URL = "sqlite:///./test_ranking_engine.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class RankingEngineTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()
        cls.seed_candidates()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
        if os.path.exists("./test_ranking_engine.db"):
            try:
                os.remove("./test_ranking_engine.db")
            except Exception:
                pass

    @classmethod
    def seed_candidates(cls):
        # 1. Candidate A: Top Match (Full match on skills, exp, tier 1 education, high behavioral signals)
        c1 = Candidate(
            name="Alice Top",
            email="alice@top.io",
            title="Senior Backend Engineer",
            location="Remote",
            work_preference="Remote",
            experience_years=8.0,
            skills=["Python", "FastAPI", "PostgreSQL"],
            resume_text="Senior Backend Engineer with 8 years of experience building Python FastAPI services.",
            education=[{
                "institution": "Stanford University",
                "degree": "M.S.",
                "field_of_study": "Computer Science",
                "tier": "tier_1"
            }],
            redrob_signals={
                "profile_completeness_score": 98.0,
                "open_to_work_flag": True,
                "github_activity_score": 90.0,
                "recruiter_response_rate": 0.95
            }
        )
        
        # 2. Candidate B: Strong Match (Good match, but tier 3 education, average behavioral signals)
        c2 = Candidate(
            name="Bob Mid",
            email="bob@mid.io",
            title="Backend Engineer",
            location="Remote",
            work_preference="Remote",
            experience_years=5.0,
            skills=["Python", "FastAPI"],
            resume_text="Backend Developer using Python and FastAPI.",
            education=[{
                "institution": "Local College",
                "degree": "B.S.",
                "field_of_study": "Information Technology",
                "tier": "tier_3"
            }],
            redrob_signals={
                "profile_completeness_score": 70.0,
                "open_to_work_flag": False,
                "github_activity_score": 40.0,
                "recruiter_response_rate": 0.60
            }
        )

        # 3. Candidate C: Poor Match (Weak skills, low experience, no signals)
        c3 = Candidate(
            name="Charlie Poor",
            email="charlie@poor.io",
            title="Junior Dev",
            location="Onsite",
            work_preference="Onsite",
            experience_years=1.0,
            skills=["HTML"],
            resume_text="Junior developer working on HTML.",
            education=[],
            redrob_signals={}
        )

        cls.db.add_all([c1, c2, c3])
        cls.db.commit()

    # --- 1. Automated Tests ---
    
    def test_ranking_suitability_and_order(self):
        # Request with raw JD
        jd_text = "Senior Backend Engineer. Requirements: Python, FastAPI, PostgreSQL. 7 years experience. Stanford University Computer Science degree required. Remote."
        response = self.client.post(
            "/api/ranking/generate",
            json={"job_description": jd_text}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we got at least 3 ranked candidates
        self.assertGreaterEqual(len(data), 3)
        
        # Locate the three seeded candidates in the results list to verify relative ranking order
        alice_idx = next(i for i, c in enumerate(data) if c["candidate_name"] == "Alice Top")
        bob_idx = next(i for i, c in enumerate(data) if c["candidate_name"] == "Bob Mid")
        charlie_idx = next(i for i, c in enumerate(data) if c["candidate_name"] == "Charlie Poor")
        
        # Verify that Alice ranked higher than Bob, who ranked higher than Charlie
        self.assertLess(alice_idx, bob_idx)
        self.assertLess(bob_idx, charlie_idx)
        
        # Verify score ordering relative to each other
        self.assertGreater(data[alice_idx]["score"], data[bob_idx]["score"])
        self.assertGreater(data[bob_idx]["score"], data[charlie_idx]["score"])
        
        # Verify ranks match their list indexes
        self.assertEqual(data[alice_idx]["rank"], alice_idx + 1)
        self.assertEqual(data[bob_idx]["rank"], bob_idx + 1)
        self.assertEqual(data[charlie_idx]["rank"], charlie_idx + 1)

    def test_ranking_limit_parameter(self):
        # Request with limit = 2
        jd_text = "Python Developer"
        response = self.client.post(
            "/api/ranking/generate",
            json={"job_description": jd_text, "limit": 2}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["rank"], 1)
        self.assertEqual(data[1]["rank"], 2)

    def test_ranking_pre_analyzed_input(self):
        # Request with structured pre-analyzed fields
        response = self.client.post(
            "/api/ranking/generate",
            json={
                "title": "Senior PyTorch Specialist",
                "required_skills": ["Python", "FastAPI"],
                "experience_required": 6.0,
                "education_requirements": ["tier_1"],
                "work_preference": "Remote"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 3)
        
        alice_data = next(c for c in data if c["candidate_name"] == "Alice Top")
        self.assertIn("Education Match: 100.0%", alice_data["reasoning"])
        self.assertIn("Behavioral Signals Score: 96.2%", alice_data["reasoning"])

    # --- 2. Validation Tests ---
    
    def test_validation_empty_request(self):
        # Neither raw description nor pre-analyzed fields provided
        response = self.client.post(
            "/api/ranking/generate",
            json={}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Must provide either a non-empty job_description or structured job", response.json()["detail"])

    def test_validation_edge_cases(self):
        # Space-only strings should fail validation
        response = self.client.post(
            "/api/ranking/generate",
            json={"job_description": "     "}
        )
        self.assertEqual(response.status_code, 400)

    # --- 3. Performance Tests ---
    
    def test_performance_100_candidates(self):
        # Seed 100 more candidates to simulate large scale ranking
        large_candidates = []
        for i in range(100):
            large_candidates.append(Candidate(
                name=f"Mock Candidate {i}",
                email=f"mock{i}@domain.com",
                title="Software Engineer",
                experience_years=float(i % 10),
                skills=["Python", "SQL"] if i % 2 == 0 else ["Java"],
                resume_text=f"This is resume text for mock candidate number {i} who is a software engineer.",
                education=[],
                redrob_signals={}
            ))
        self.db.add_all(large_candidates)
        self.db.commit()

        # Measure latency
        start_time = time.time()
        response = self.client.post(
            "/api/ranking/generate",
            json={
                "title": "Python Software Engineer",
                "required_skills": ["Python", "SQL"],
                "experience_required": 5.0
            }
        )
        end_time = time.time()
        latency = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we ranked all candidates (100 seeded + 3 initial)
        self.assertEqual(len(data), 103)
        
        # Performance assertion: Should generate rankings in under 2.0 seconds
        print(f"\n[PERFORMANCE] Ranked 103 candidates in {latency:.4f} seconds.")
        self.assertLess(latency, 2.0, f"Ranking generation took too long: {latency:.2f}s")

if __name__ == "__main__":
    unittest.main()
