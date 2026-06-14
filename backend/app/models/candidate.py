from sqlalchemy import Column, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, nullable=True)
    location = Column(String, nullable=True)
    work_preference = Column(String, default="Remote") # Remote, Hybrid, Onsite
    experience_years = Column(Float, default=0.0)
    skills = Column(JSON, default=list) # List of skills like ["Python", "TensorFlow"]
    resume_text = Column(Text, nullable=True)
    status = Column(String, default="Sourcing") # Sourcing, Screening, Interview, Offer, Hired
    salary_expectation = Column(Integer, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Redrob dataset fields
    candidate_id = Column(String, unique=True, index=True, nullable=True)
    profile = Column(JSON, default=dict)
    career_history = Column(JSON, default=list)
    education = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    redrob_signals = Column(JSON, default=dict)

    # Relationships
    rankings = relationship("Ranking", back_populates="candidate", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="candidate", cascade="all, delete-orphan")
