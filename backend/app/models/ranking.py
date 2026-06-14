from sqlalchemy import Column, Integer, ForeignKey, Float, JSON, String
from sqlalchemy.orm import relationship
from app.database import Base

class Ranking(Base):
    __tablename__ = "rankings"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, default=0.0) # 0.0 to 100.0
    explanation = Column(JSON, default=dict) # breakdown of skills matched, skill gaps, exp gap, etc.
    tier = Column(String, default="Standard") # Top Match, Strong Match, Good Match, Potentially Unsuitable

    # Relationships
    candidate = relationship("Candidate", back_populates="rankings")
    job = relationship("Job", back_populates="rankings")
