from sqlalchemy import Column, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    work_preference = Column(String, default="Remote") # Remote, Hybrid, Onsite
    description = Column(Text, nullable=True)
    required_skills = Column(JSON, default=list) # List of skills extracted/required
    experience_required = Column(Float, default=0.0) # years of experience required
    status = Column(String, default="Active") # Active, Paused, Closed
    priority = Column(String, default="Medium") # High, Medium, Low

    # Relationships
    rankings = relationship("Ranking", back_populates="job", cascade="all, delete-orphan")
