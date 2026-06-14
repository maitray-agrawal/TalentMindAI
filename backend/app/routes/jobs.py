from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate, JobInDB
from app.services.jd_analyzer import JDAnalyzerService

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[JobInDB])
def read_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@router.get("/{job_id}", response_model=JobInDB)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/", response_model=JobInDB, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    # Auto-analyze the raw description if no title or no skills are provided
    data = job_in.model_dump()
    if data.get("description") and (not data.get("title") or not data.get("required_skills")):
        analysis = JDAnalyzerService.analyze(data["description"])
        
        # Merge analysis results if the client left them blank
        if not data.get("title") or data["title"] == "Untitled Role":
            data["title"] = analysis["title"]
        if not data.get("required_skills"):
            data["required_skills"] = analysis["required_skills"]
        if not data.get("experience_required") or data["experience_required"] == 0.0:
            data["experience_required"] = analysis["experience_required"]
        if not data.get("location"):
            data["location"] = analysis["location"]
        if not data.get("work_preference"):
            data["work_preference"] = analysis["work_preference"]
        if not data.get("department"):
            data["department"] = analysis["department"]
            
    new_job = Job(**data)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.put("/{job_id}", response_model=JobInDB)
def update_job(job_id: int, job_in: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    update_data = job_in.model_dump(exclude_unset=True)
    
    # Re-run analysis if the description is updated
    if "description" in update_data and update_data["description"]:
        analysis = JDAnalyzerService.analyze(update_data["description"])
        if "title" not in update_data:
            update_data["title"] = analysis["title"]
        if "required_skills" not in update_data:
            update_data["required_skills"] = analysis["required_skills"]
        if "experience_required" not in update_data:
            update_data["experience_required"] = analysis["experience_required"]
            
    for key, val in update_data.items():
        setattr(job, key, val)
        
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return None

@router.post("/analyze")
def analyze_job_description(file: UploadFile = File(...)):
    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        
    filename = file.filename
    text = ""
    
    if filename.endswith(".docx"):
        try:
            text = JDAnalyzerService.extract_text_from_docx(contents)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read docx file: {str(e)}")
    elif filename.endswith(".txt"):
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = contents.decode("latin-1")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decode text file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .docx or .txt file.")
        
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="The uploaded file contains no text content.")
        
    analysis = JDAnalyzerService.analyze_detailed(text)
    return analysis
