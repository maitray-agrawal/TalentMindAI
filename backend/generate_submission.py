import csv
import argparse
from pathlib import Path

from app.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.jd_analyzer import JDAnalyzerService
from app.services.ranker_service import RankerService

def main(use_llm=False, groq_rerank=False):
    db = SessionLocal()
    try:
        # 2. Open /backend/extracted_jd.txt with plain open() and read the text
        jd_path = Path(__file__).parent / "extracted_jd.txt"
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        # 3. Call parser depending on use_llm flag
        if use_llm:
            from app.services.groq_jd_service import GroqJDService
            print("Using Groq LLM to parse Job Description...")
            analysis = JDAnalyzerService.analyze_detailed(jd_text)
            groq_analysis = GroqJDService.analyze_jd(jd_text)
            analysis.update(groq_analysis)
        else:
            print("Using heuristic parser to parse Job Description...")
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
        
        synthetic_keywords = ["AUDIT", "TEST", "DEMO", "SAMPLE"]
        valid_candidates = [
            c for c in candidates 
            if not (c.candidate_id and any(kw in c.candidate_id.upper() for kw in synthetic_keywords))
        ]
        
        results = []
        # 6. For each candidate call calculate_match
        for candidate in valid_candidates:
            score, explanation, tier = RankerService.calculate_match(candidate, job)
            results.append({
                "candidate": candidate,
                "score": score,
                "explanation": explanation
            })

        # 7. Sort results by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        if groq_rerank:
            from app.services.groq_reranker import GroqReranker
            results = GroqReranker.rerank_candidates(results, job)

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
                
                groq_note = explanation.get("groq_reasoning", "")
                reasoning = (
                    f"{title} | {exp_years}yrs | "
                    f"Matched: {matched_str} | "
                    f"Key gaps: {missing_str} | "
                    f"Profile: {completeness}% complete, response rate: {response_rate}"
                )
                if groq_note:
                    reasoning += f" | Rerank Note: {groq_note}"
                
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
    parser = argparse.ArgumentParser(description="Generate candidate ranking submission.")
    parser.add_argument("--llm", action="store_true", help="Use Groq LLM for Job Description parsing instead of the heuristic parser.")
    parser.add_argument("--groq-rerank", action="store_true", help="Enable Groq LLM recruiter re-ranking on the top 50 candidates.")
    args = parser.parse_args()
    main(use_llm=args.llm, groq_rerank=args.groq_rerank)
