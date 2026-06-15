import csv
from pathlib import Path

from app.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.jd_analyzer import JDAnalyzerService
from app.services.ranker_service import RankerService

def main():
    db = SessionLocal()
    try:
        # 2. Open /backend/extracted_jd.txt with plain open() and read the text
        jd_path = Path(__file__).parent / "extracted_jd.txt"
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        # 3. Call JDAnalyzerService.analyze_detailed(jd_text) → store as analysis
        analysis = JDAnalyzerService.analyze_detailed(jd_text)

        # 4. Build a temporary Job object
        job = Job(
            title=analysis.get("title"),
            description=jd_text,
            required_skills=analysis.get("required_skills", []),
            experience_required=float(analysis.get("experience_required", 0.0) or 0.0),
            work_preference=analysis.get("work_preference", "Remote"),
            location=analysis.get("location", "Remote")
        )
        job.education_requirements = analysis.get("education_requirements", [])

        # 5. Open DB session, query all Candidate records
        candidates = db.query(Candidate).all()
        
        results = []
        # 6. For each candidate call calculate_match
        for candidate in candidates:
            score, explanation, tier = RankerService.calculate_match(candidate, job)
            results.append({
                "candidate": candidate,
                "score": score,
                "explanation": explanation
            })

        # 7. Sort results by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        # 8. Write to /submission.csv (project root)
        output_path = Path(__file__).parent.parent / "submission.csv"
        
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            
            for rank, result in enumerate(results, start=1):
                candidate = result["candidate"]
                score = result["score"]
                explanation = result["explanation"]
                
                candidate_id = candidate.candidate_id
                normalized_score = round(score / 100, 4)
                
                signals = candidate.redrob_signals or {}
                matched = explanation.get("matched_skills", [])
                missing = explanation.get("missing_skills", [])[:3]
                
                completeness = round(float(signals.get("profile_completeness_score", 0)), 1)
                response_rate = round(float(signals.get("recruiter_response_rate", 0)), 2)
                
                title = candidate.title or 'Unknown'
                exp_years = candidate.experience_years
                matched_str = ', '.join(matched) if matched else 'None'
                missing_str = ', '.join(missing) if missing else 'None'
                
                reasoning = (
                    f"{title} | {exp_years}yrs | "
                    f"Matched: {matched_str} | "
                    f"Key gaps: {missing_str} | "
                    f"Profile: {completeness}% complete, response rate: {response_rate}"
                )
                
                writer.writerow([candidate_id, rank, normalized_score, reasoning])
                
        # 9. Print: total candidates ranked + top 5 names and scores
        print(f"Total candidates ranked: {len(results)}")
        print("Top 5 candidates:")
        for result in results[:5]:
            c = result["candidate"]
            name = getattr(c, 'name', getattr(c, 'first_name', c.candidate_id))
            print(f"- {name}: {result['score']}")

    finally:
        # 10. Close DB in a finally block
        db.close()

if __name__ == "__main__":
    main()
