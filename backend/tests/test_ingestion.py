import sys
import os
import json
import tempfile
import unittest
from pathlib import Path

# Add backend to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.candidate import Candidate
from app.services.ingestion import IngestionService
from app.routes.candidates import get_candidate_stats, search_candidates

# Set up test database
TEST_DATABASE_URL = "sqlite:///./test_ingestion_talentmind.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MOCK_CANDIDATES = [
    {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Candidate One",
            "headline": "Lead AI Research Scientist",
            "summary": "Deep learning researcher with 8 years of experience.",
            "location": "San Francisco, CA",
            "country": "United States",
            "years_of_experience": 8.0,
            "current_title": "AI Scientist",
            "current_company": "NeuroLink",
            "current_company_size": "51-200",
            "current_industry": "Artificial Intelligence"
        },
        "career_history": [
            {
                "company": "NeuroLink",
                "title": "AI Scientist",
                "start_date": "2022-01-01",
                "end_date": None,
                "duration_months": 24,
                "is_current": True,
                "industry": "Artificial Intelligence",
                "company_size": "51-200",
                "description": "Led LLM projects."
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "Ph.D.",
                "field_of_study": "Computer Science",
                "start_year": 2014,
                "end_year": 2018,
                "grade": "4.0",
                "tier": "tier_1"
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 45, "duration_months": 96},
            {"name": "PyTorch", "proficiency": "expert", "endorsements": 30, "duration_months": 60}
        ],
        "certifications": [
            {"name": "AWS Machine Learning", "issuer": "Amazon", "year": 2020}
        ],
        "languages": [
            {"language": "English", "proficiency": "native"}
        ],
        "redrob_signals": {
            "profile_completeness_score": 95.0,
            "signup_date": "2021-06-01",
            "last_active_date": "2023-12-01",
            "open_to_work_flag": True,
            "profile_views_received_30d": 120,
            "applications_submitted_30d": 5,
            "recruiter_response_rate": 0.9,
            "avg_response_time_hours": 2.5,
            "skill_assessment_scores": {"Python": 98.0, "PyTorch": 92.0},
            "connection_count": 450,
            "endorsements_received": 75,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 45.0, "max": 65.0},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "github_activity_score": 88.0,
            "search_appearance_30d": 200,
            "saved_by_recruiters_30d": 15,
            "interview_completion_rate": 1.0,
            "offer_acceptance_rate": 0.8,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True
        }
    },
    {
        "candidate_id": "CAND_0000002",
        "profile": {
            "anonymized_name": "Candidate Two",
            "headline": "Senior Frontend Developer",
            "summary": "Experienced react developer.",
            "location": "London, UK",
            "country": "United Kingdom",
            "years_of_experience": 5.5,
            "current_title": "Frontend Engineer",
            "current_company": "WebTech",
            "current_company_size": "11-50",
            "current_industry": "Tech Services"
        },
        "career_history": [
            {
                "company": "WebTech",
                "title": "Frontend Engineer",
                "start_date": "2021-06-01",
                "end_date": None,
                "duration_months": 30,
                "is_current": True,
                "industry": "Tech Services",
                "company_size": "11-50",
                "description": "Figma to React translation."
            }
        ],
        "education": [
            {
                "institution": "University College London",
                "degree": "B.Sc.",
                "field_of_study": "Software Engineering",
                "start_year": 2016,
                "end_year": 2019,
                "grade": "First Class",
                "tier": "tier_1"
            }
        ],
        "skills": [
            {"name": "React", "proficiency": "advanced", "endorsements": 25, "duration_months": 48},
            {"name": "TypeScript", "proficiency": "advanced", "endorsements": 18, "duration_months": 36}
        ],
        "certifications": [],
        "languages": [
            {"language": "English", "proficiency": "native"}
        ],
        "redrob_signals": {
            "profile_completeness_score": 85.0,
            "signup_date": "2020-03-01",
            "last_active_date": "2023-11-28",
            "open_to_work_flag": False,
            "profile_views_received_30d": 45,
            "applications_submitted_30d": 1,
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 12.0,
            "skill_assessment_scores": {"React": 85.0},
            "connection_count": 120,
            "endorsements_received": 12,
            "notice_period_days": 60,
            "expected_salary_range_inr_lpa": {"min": 25.0, "max": 35.0},
            "preferred_work_mode": "remote",
            "willing_to_relocate": False,
            "github_activity_score": 45.0,
            "search_appearance_30d": 75,
            "saved_by_recruiters_30d": 3,
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.7,
            "verified_email": True,
            "verified_phone": False,
            "linkedin_connected": True
        }
    }
]

class IngestionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()
        
        # Write mock data to a temp file
        cls.temp_jsonl = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.jsonl', encoding='utf-8')
        for cand in MOCK_CANDIDATES:
            cls.temp_jsonl.write(json.dumps(cand) + "\n")
        cls.temp_jsonl.close()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists(cls.temp_jsonl.name):
            os.remove(cls.temp_jsonl.name)
        if os.path.exists("./test_ingestion_talentmind.db"):
            try:
                os.remove("./test_ingestion_talentmind.db")
            except Exception:
                pass

    def test_1_ingestion_service(self):
        # Ingest mock candidates
        result = IngestionService.ingest_candidates(
            db=self.db,
            file_path=self.temp_jsonl.name,
            limit=None,
            batch_size=10
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_processed"], 2)
        self.assertEqual(result["inserted"], 2)
        self.assertEqual(result["updated"], 0)

        # Verify in DB
        c1 = self.db.query(Candidate).filter(Candidate.candidate_id == "CAND_0000001").first()
        self.assertIsNotNone(c1)
        self.assertEqual(c1.name, "Candidate One")
        self.assertEqual(c1.experience_years, 8.0)
        self.assertEqual(c1.work_preference, "Hybrid")
        self.assertIn("Python", c1.skills)
        self.assertIn("PyTorch", c1.skills)
        self.assertEqual(c1.salary_expectation, 65)
        self.assertEqual(c1.profile["current_company"], "NeuroLink")
        self.assertEqual(c1.redrob_signals["profile_completeness_score"], 95.0)

        # Verify idempotency (should update 2)
        result_retry = IngestionService.ingest_candidates(
            db=self.db,
            file_path=self.temp_jsonl.name,
            limit=None,
            batch_size=10
        )
        self.assertEqual(result_retry["records_processed"], 2)
        self.assertEqual(result_retry["inserted"], 0)
        self.assertEqual(result_retry["updated"], 2)

    def test_2_search_candidates_route(self):
        # Search by Q
        res_q = search_candidates(q="Candidate One", limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_q), 1)
        self.assertEqual(res_q[0].candidate_id, "CAND_0000001")

        # Search by location
        res_loc = search_candidates(location="London", limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_loc), 1)
        self.assertEqual(res_loc[0].candidate_id, "CAND_0000002")

        # Search by experience range
        res_exp = search_candidates(min_experience=6.0, limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_exp), 1)
        self.assertEqual(res_exp[0].candidate_id, "CAND_0000001")

        # Search by work preference
        res_pref = search_candidates(work_preference="remote", limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_pref), 1)
        self.assertEqual(res_pref[0].candidate_id, "CAND_0000002")

        # Search by skill
        res_skill = search_candidates(skill="React", limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_skill), 1)
        self.assertEqual(res_skill[0].candidate_id, "CAND_0000002")

        # Search by open_to_work
        res_open = search_candidates(open_to_work=True, limit=50, offset=0, db=self.db)
        self.assertEqual(len(res_open), 1)
        self.assertEqual(res_open[0].candidate_id, "CAND_0000001")

    def test_3_stats_route(self):
        stats = get_candidate_stats(db=self.db)
        self.assertEqual(stats["total_candidates"], 2)
        self.assertEqual(stats["average_experience"], 6.75) # (8.0 + 5.5) / 2
        self.assertEqual(stats["experience_distribution"]["Mid (3-7 Yrs)"], 1)
        self.assertEqual(stats["experience_distribution"]["Senior (7-12 Yrs)"], 1)
        self.assertEqual(stats["open_to_work_count"], 1)
        self.assertEqual(stats["open_to_work_percentage"], 50.0)
        self.assertEqual(stats["average_profile_completeness"], 90.0) # (95 + 85) / 2
        
        # Verify skills sorted
        self.assertGreaterEqual(len(stats["top_skills"]), 2)
        self.assertEqual(stats["top_skills"][0]["count"], 1)

if __name__ == "__main__":
    unittest.main()
