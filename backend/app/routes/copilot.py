from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.audit import AuditLog
from app.services.copilot_service import CopilotService
from pydantic import BaseModel

router = APIRouter(prefix="/copilot", tags=["Recruiter Copilot"])

class ChatRequest(BaseModel):
    prompt: str
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None

@router.post("/chat")
def chat_with_copilot(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
    result = CopilotService.chat(
        prompt=payload.prompt,
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        db=db
    )
    
    # Write to audit log
    log_details = f"Prompt: {payload.prompt}\nResponse: {result.get('response')}"
    if "email_draft" in result:
        log_details += f"\nEmail Draft: {result['email_draft']}"
        
    audit_entry = AuditLog(
        candidate_id=payload.candidate_id,
        action="Copilot Interaction",
        details=log_details
    )
    db.add(audit_entry)
    db.commit()
    
    return result
