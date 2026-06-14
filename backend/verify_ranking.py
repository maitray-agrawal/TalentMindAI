import os
import sys
import time
from pathlib import Path
from sqlalchemy.orm import Session

# Add absolute backend path
sys.path.append("d:/TalentMindAI/backend")

from app.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.jd_analyzer import JDAnalyzerService
from app.services.ranker_service import RankerService

def verify_ranking():
    jd_path = Path("d:/TalentMindAI/dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/job_description.docx")
    if not jd_path.exists():
        print(f"Error: Job description file not found at {jd_path}")
        return
        
    print("Reading job description...")
    with open(jd_path, "rb") as f:
        file_bytes = f.read()
        
    docx_text = JDAnalyzerService.extract_text_from_docx(file_bytes)
    
    analysis = JDAnalyzerService.analyze_detailed(docx_text)
    print("Parsed Job requirements:")
    print(f"Title: {analysis.get('title')}")
    print(f"Required Skills: {analysis.get('required_skills')}")
    print(f"Preferred Skills: {analysis.get('preferred_skills')}")
    print(f"Exp Required: {analysis.get('experience_required')}")
    print(f"Education Requirements: {analysis.get('education_requirements')}")
    
    temp_job = Job(
        title=analysis.get("title") or "Search/Retrieval Engineer",
        description=docx_text,
        required_skills=analysis.get("required_skills") or [],
        experience_required=float(analysis.get("experience_required") or 0.0),
        work_preference=analysis.get("work_preference") or "Remote",
        location=analysis.get("location") or "Remote"
    )
    temp_job.education_requirements = analysis.get("education_requirements") or []
    
    db = SessionLocal()
    candidates = db.query(Candidate).all()
    candidate_count = len(candidates)
    print(f"\nTotal candidates in DB: {candidate_count}")
    if candidate_count == 0:
        print("Error: No candidates found in database!")
        db.close()
        return

    print("Ranking candidates...")
    start_time = time.time()
    ranked_list = []
    for candidate in candidates:
        score, explanation, tier = RankerService.calculate_match(candidate, temp_job)
        ranked_list.append((candidate, score, explanation, tier))
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"Ranking completed in {duration:.4f} seconds.")
    
    # Sort descending by score
    ranked_list.sort(key=lambda x: x[1], reverse=True)
    
    # Generate Markdown Report
    report_lines = []
    report_lines.append("# Candidate Ranking Verification Report")
    report_lines.append(f"\n- **Job Title**: {temp_job.title}")
    report_lines.append(f"- **Experience Required**: {temp_job.experience_required} years")
    report_lines.append(f"- **Required Skills**: {', '.join(temp_job.required_skills)}")
    report_lines.append(f"- **Education Required**: {', '.join(temp_job.education_requirements)}")
    report_lines.append(f"- **Total Candidates Processed**: {candidate_count}")
    report_lines.append(f"- **Ranking Generation Time**: {duration:.4f} seconds")
    
    report_lines.append("\n## Top 20 Candidates and Score Breakdown")
    report_lines.append("\n| Rank | Candidate Name | ID | Overall Score | Skills Match | Experience Match | Semantic Sim | Education Match | Behavioral Signals | Location Match |")
    report_lines.append("|---|---|---|---|---|---|---|---|---|---|")
    
    for idx, (cand, score, explanation, tier) in enumerate(ranked_list[:20]):
        report_lines.append(
            f"| {idx+1} | {cand.name} | {cand.candidate_id} | {score}% ({tier}) | "
            f"{explanation.get('skills_score')}% | {explanation.get('experience_score')}% | "
            f"{explanation.get('text_similarity_score')}% | {explanation.get('education_score')}% | "
            f"{explanation.get('behavioral_score')}% | {explanation.get('location_score')}% |"
        )
        
    report_lines.append("\n## Detailed Analysis of Top 5 Candidates")
    for idx, (cand, score, explanation, tier) in enumerate(ranked_list[:5]):
        report_lines.append(f"\n### {idx+1}. {cand.name} ({cand.candidate_id})")
        report_lines.append(f"- **Overall Fit**: **{score}%** ({tier})")
        report_lines.append(f"- **Experience**: {cand.experience_years} years (Job requirement: {temp_job.experience_required} years)")
        report_lines.append(f"- **Skills**: Match ratio {len(explanation.get('matched_skills', []))}/{len(explanation.get('matched_skills', [])) + len(explanation.get('missing_skills', []))}")
        report_lines.append(f"  - *Matched*: `{', '.join(explanation.get('matched_skills', [])) or 'None'}`")
        report_lines.append(f"  - *Missing*: `{', '.join(explanation.get('missing_skills', [])) or 'None'}`")
        report_lines.append(f"- **Education Detail**: `{cand.education}` (Score: {explanation.get('education_score')}%)")
        report_lines.append(f"- **Behavioral Detail (Redrob)**: Completeness: {cand.redrob_signals.get('profile_completeness_score', 0)}%, Recruiter Response: {cand.redrob_signals.get('recruiter_response_rate', 0)}, Github Activity: {cand.redrob_signals.get('github_activity_score', 0)}")
        
    report_path = Path("d:/TalentMindAI/ranking_report.md")
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report_lines))
        
    print(f"Report successfully generated at {report_path}")
    db.close()

if __name__ == "__main__":
    verify_ranking()
