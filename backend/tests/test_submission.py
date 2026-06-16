import sys
import os
import io
import csv
from pathlib import Path
import unittest

# Add backend to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking

# Set up test database
TEST_DATABASE_URL = "sqlite:///./test_submission.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SubmissionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

        # Seed data for testing
        cls.job = Job(
            id=5,
            title="Senior AI Engineer",
            description="Deep Learning, PyTorch, Python, 5 years experience.",
            experience_required=5.0,
            required_skills=["Deep Learning", "PyTorch", "Python"]
        )
        cls.db.add(cls.job)

        cls.cand1 = Candidate(
            id=1,
            name="Alice Candidate",
            email="alice@talentmind.io",
            title="Senior AI Engineer",
            experience_years=6.0,
            skills=["Deep Learning", "PyTorch", "Python"],
            candidate_id="CAND_0000001",
            redrob_signals={"recruiter_response_rate": 0.95}
        )
        cls.cand2 = Candidate(
            id=2,
            name="Bob Candidate",
            email="bob@talentmind.io",
            title="Junior Developer",
            experience_years=2.0,
            skills=["Python"],
            candidate_id="CAND_0000002",
            redrob_signals={"recruiter_response_rate": 0.50}
        )
        cls.db.add(cls.cand1)
        cls.db.add(cls.cand2)
        cls.db.commit()

        # Override dependency get_db
        def override_get_db():
            try:
                yield cls.db
            finally:
                pass
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_submission.db"):
            try:
                os.remove("./test_submission.db")
            except Exception:
                pass
        # Remove dependency override
        app.dependency_overrides.pop(get_db, None)

    def test_submission_generation(self):
        # 1. Trigger rankings generation (ranking should run automatically or be created first)
        response = self.client.post("/api/submission/generate?job_id=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=submission.csv", response.headers["content-disposition"])

        csv_text = response.text
        self.assertTrue(len(csv_text) > 0)

        # 2. Parse CSV and perform validation
        f = io.StringIO(csv_text)
        reader = csv.DictReader(f)
        
        # Verify columns match sample_submission.csv
        expected_columns = ["candidate_id", "rank", "score", "reasoning"]
        self.assertEqual(reader.fieldnames, expected_columns)

        rows = list(reader)
        self.assertEqual(len(rows), 2)  # Should have 2 candidates

        seen_ranks = set()
        prev_score = float('inf')

        for idx, row in enumerate(rows):
            # Verify candidate ID format
            self.assertTrue(row["candidate_id"].startswith("CAND_"))

            # Verify unique rank
            rank = int(row["rank"])
            self.assertEqual(rank, idx + 1)
            self.assertNotIn(rank, seen_ranks)
            seen_ranks.add(rank)

            # Verify score format and descending order
            score = float(row["score"])
            # Format score check (e.g. 0.9630 is 6 characters string)
            self.assertEqual(len(row["score"].split(".")[1]), 4)
            self.assertLessEqual(score, prev_score)
            prev_score = score

            # Verify reasoning is populated and structured
            reasoning = row["reasoning"]
            self.assertTrue(len(reasoning) > 0)
            self.assertIn("yrs", reasoning)
            self.assertIn("Matched", reasoning)
            self.assertIn("response rate", reasoning)

if __name__ == "__main__":
    unittest.main()
