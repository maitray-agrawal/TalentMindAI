# Final Submission Report: 100k Candidate Dataset

This report documents the final pipeline run, processing time, candidate validation results, and top candidates.

## 1. Run Summary
- **Dataset Size:** 100,000 candidates + 1 audit candidate (100,001 total records in SQLite database).
- **Synthetic Candidates Filtered:** 1 candidate (`CAND_0000000_AUDIT` or containing synthetic keywords) was automatically excluded.
- **Total Candidates Ranked:** 100,000 candidates.
- **Pipeline Components Used:**
  - **Job Description Parsing:** `GroqJDService` (LLM-based parsing)
  - **Candidate Reranking:** `GroqReranker` (LLM-based evaluation on top 50 candidates, blended with 0.7 heuristic + 0.3 LLM weights)
- **Output File:** `submission.csv` (100 rows, containing columns `candidate_id`, `rank`, `score`, `reasoning`).

---

## 2. Execution Performance
- **Heuristic Phase Duration:** ~4.6 minutes.
- **Groq Reranking Phase Duration:** ~27.2 minutes (including exponential backoff retries for rate-limiting).
- **Total Pipeline Runtime:** ~31.8 minutes.

---

## 3. Top 20 Candidates

The table below lists the top 20 candidates generated in the final submission.

| Rank | Candidate ID | Name | Job Title | Match Score | Reasoning (Rerank Note / Highlights) |
| :---: | :---: | :--- | :--- | :---: | :--- |
| 1 | CAND_0002025 | Ira Dalal | Senior AI Engineer | 84.72% | 5.9 YOE. Strong skills in NLP and Dense Retrieval. |
| 2 | CAND_0061265 | Tanya Chopra | Recommendation Systems Engineer | 82.48% | 6.6 YOE. Strong Recommendation and Applied AI experience. |
| 3 | CAND_0079387 | Sneha Arora | AI Engineer | 82.41% | 6.9 YOE. Strong skills in ML pipelines. |
| 4 | CAND_0052328 | Vikram Banerjee | Recommendation Systems Engineer | 82.13% | 6.5 YOE. Experienced in search/retrieval. |
| 5 | CAND_0088025 | Amit Arora | Staff Machine Learning Engineer | 81.84% | 8.6 YOE. Relevant Staff-level MLE expertise. |
| 6 | CAND_0027691 | Ayaan Goyal | NLP Engineer | 81.68% | 6.5 YOE. |
| 7 | CAND_0070398 | Riya Saxena | Machine Learning Engineer | 81.63% | 7.2 YOE. |
| 8 | CAND_0083307 | Neha Patel | Search Engineer | 81.15% | 7.8 YOE. |
| 9 | CAND_0065195 | Kiara Mukherjee | Search Engineer | 80.86% | 5.1 YOE. |
| 10 | CAND_0071974 | Sai Verma | Senior AI Engineer | 80.81% | 7.8 YOE. |
| 11 | CAND_0018499 | Aarav Trivedi | Senior Machine Learning Engineer | 80.38% | 7.2 YOE. |
| 12 | CAND_0039754 | Mira Banerjee | Senior Applied Scientist | 80.38% | 16.2 YOE. |
| 13 | CAND_0040178 | Anika Bhatia | ML Engineer | 80.31% | 5.0 YOE. |
| 14 | CAND_0093193 | Aarohi Bose | Senior Machine Learning Engineer | 80.30% | 7.9 YOE. |
| 15 | CAND_0036121 | Atharv Bansal | ML Engineer | 80.16% | 5.2 YOE. |
| 16 | CAND_0032179 | Om Hegde | Computer Vision Engineer | 79.89% | 6.4 YOE. |
| 17 | CAND_0086022 | Dhruv Naidu | Senior Applied Scientist | 79.81% | 5.3 YOE. |
| 18 | CAND_0050876 | Vivaan Shah | Applied ML Engineer | 79.60% | 6.0 YOE. |
| 19 | CAND_0080766 | Kiara Mittal | Staff Machine Learning Engineer | 79.46% | 8.8 YOE. |
| 20 | CAND_0030784 | Ved Mukherjee | Data Scientist | 79.21% | 4.4 YOE. |

---

## 4. Validation Results

We ran both backend validation tests and the official Hack2Skill dataset validator on `submission.csv`:

### Local Validator:
```bash
$ python backend/validate_submission.py
PASS (100 rows checked)
```

### Challenge Validator:
```bash
$ python "dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" submission.csv
Submission is valid.
```

The output file meets all requirements:
1. Contains exactly 100 candidate data rows (excluding the header).
2. Rank values are sequential and strictly unique (1 to 100).
3. Candidate IDs follow the `CAND_XXXXXXX` format.
4. Score values are non-increasing and fall strictly in the range `[0.0, 1.0]`.
5. Reasoning field is populated with candidate summaries and Groq evaluation notes.
