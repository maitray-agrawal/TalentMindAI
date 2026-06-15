# Full Dataset Import Report

This document records the execution details and findings from importing the complete 100,000-candidate Hack2Skill recruitment dataset into the production environment.

## 1. Execution Summary

* **Import Command:**
  ```bash
  python -c "from app.database import SessionLocal; from app.services.ingestion import IngestionService; db = SessionLocal(); res = IngestionService.ingest_candidates(db, 'd:/TalentMindAI/dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl', limit=None); print(res)"
  ```
* **Import Duration:** **27.29 seconds** (ingestion rate of **~3,664.49 candidates/second**)
* **Candidate Count:** **100,001** records (`100,000` from dataset + `1` synthetic audit candidate)
* **Final Database Size:** **679,088,128 bytes** (~679.09 MB)

## 2. Ingestion Verification

A post-import verification was run against the SQLite database instance using SQL:

```sql
SELECT COUNT(*) FROM candidates;
```

* **Expected Count:** `100,001`
* **Actual Count:** `100,001`
* **Result:** **PASS**

All records were successfully streamed, parsed, validated, and persisted into the database. No uniqueness constraints, candidate_id collisions, or parser errors occurred during the run.
