import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "TalentMind AI Recruitment Platform Backend"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/talentmind.db")
    
    # AI Ranking Default Weights (Total = 1.0)
    WEIGHT_SKILLS: float = 0.30
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_SEMANTIC: float = 0.15
    WEIGHT_EDUCATION: float = 0.15
    WEIGHT_BEHAVIORAL: float = 0.10
    WEIGHT_LOCATION: float = 0.10

settings = Settings()
