# TalentMindAI Scoring Methodology

This document outlines the evaluation algorithms and weighting used by the `RankerService` to match candidates to job requirements. The engine uses a hybrid of semantic similarity, heuristic rules, and behavioral signals to generate a final normalized score between 0 and 100.

## 1. Skills Scoring (Weight: 30%)
The skills score evaluates candidate capabilities using a weighted blend of semantic categories and exact matches:
*   **Semantic Category Match (80%):** Predefined technology clusters (e.g., Vector DBs, Ranking/Recommendation, LLMs). If a candidate possesses any skill in a cluster required by the job, they receive credit for the entire category.
*   **Exact Keyword Match (20%):** Simple intersection ratio (`Matched Skills / Total Required Skills`).
*   **Retrieval Boost:** Candidates flagged with `has_retrieval_experience` receive an absolute `+0.20` boost to this component (capped at 1.0).

## 2. Experience Scoring (Weight: 20%)
A simple linear ratio comparing the candidate's total years of experience against the job's requirement:
*   If `candidate.experience >= job.experience`: Score is `1.0`.
*   If `candidate.experience < job.experience`: Score is `candidate.experience / job.experience`.
*   *Note: If the job specifies no experience requirement, the score defaults to `1.0`.*

## 3. Semantic Scoring (Weight: 15%)
Evaluates unstructured text alignment between the candidate and the job using TF-IDF (Term Frequency-Inverse Document Frequency).
*   **Corpus:** Candidate's (`Title` + `Skills`) vs. Job's (`Title` + `Required Skills`).
*   **Algorithm:** Scikit-learn `TfidfVectorizer` (unigrams & bigrams) calculating Cosine Similarity.
*   **Calibration:** The raw cosine output is scaled by `1.5` (clipping at `1.0`) to compensate for naturally low mathematical baseline scores across differing vocabularies.
*   **Retrieval Boost:** Candidates with `has_retrieval_experience` receive a `+0.15` boost to this component.

## 4. Education Scoring (Weight: 15%)
Iterates through all degrees listed by the candidate and evaluates the strongest match (starting from a base score of `0.6` per degree):
*   **Institution Tier:** `+0.20` for Tier-1 institutions (e.g., IIT, BITS, Stanford, MIT, Harvard).
*   **Field of Study:** `+0.20` if the field is CS/Engineering/Data/AI *and* the target job is a technical role.
*   **Degree Level:** `+0.20` for a Ph.D./Doctorate; `+0.10` for a Master's/MCA.
*   *Note: Capped at `1.0`. Defaults to `0.5` if education is missing but required, and `1.0` if the job specifies no requirements.*

## 5. Behavioral Scoring (Weight: 10%)
An aggregated score derived from Redrob dataset signals:
*   **Profile Completeness (40%):** Score (`0.0 - 1.0`).
*   **Open To Work (20%):** `1.0` if true, `0.5` if false.
*   **GitHub Activity (20%):** Score (`0.0 - 1.0`).
*   **Recruiter Response Rate (20%):** Ratio (`0.0 - 1.0`).

## 6. Location Scoring (Weight: 10%)
Evaluates work preference and geographical alignment:
*   **Job is Remote:** `1.0` if candidate prefers remote, `0.9` otherwise.
*   **Job is On-site/Hybrid:** 
    *   `1.0` for exact/substring location match.
    *   `0.8` if candidate is willing to relocate or prefers "hybrid/onsite".
    *   `0.2` if candidate strictly prefers "remote".
    *   `0.5` for all other mismatches.

## 7. Role Fit Multipliers
Applied *after* the base weighted score is calculated. If the target job is technical (Engineer/Scientist/ML), penalties are applied based on the candidate's title history:
*   **Direct AI/Search match:** `1.0` multiplier.
*   **Software Engineers (without retrieval exp) applying to AI jobs:** `0.95` multiplier.
*   **DevOps/QA (without retrieval exp) applying to AI jobs:** `0.80` multiplier (`0.95` for non-AI tech jobs).
*   **Business Analysts:** `0.60` multiplier.
*   **Non-technical roles (HR, Marketing, Sales, etc.):** `0.15` multiplier.

## 8. Disqualifier Penalties
Compounding percentage deductions applied to the final score for heuristic red flags:
*   **Consulting-Only Background:** `-10%` penalty (multiplier `0.90`) if 100% of the candidate's career history consists of IT service/consulting firms (TCS, Infosys, Wipro, etc.).
*   **Title-Chasers:** `-5%` penalty (multiplier `0.95`) if the average tenure across all roles is under 15 months.
*   **AI Wrapper-Only:** `-10%` penalty (multiplier `0.90`) if the candidate lists wrapper skills (LangChain, OpenAI) but lacks foundational frameworks (PyTorch, TensorFlow, XGBoost, FAISS).

## 9. Final Score Calculation
The engine resolves the evaluation in the following order:
1. Calculates the weighted base score across the 6 dimensions (Totaling 100%).
2. Multiplies by the `Role Fit Multiplier`.
3. Sequentially multiplies by any triggered `Disqualifier Penalties`.
4. Bounds the output using `max(0.0, min(100.0, final_score))`.
5. Rounds to one decimal place.

## 10. Tier Assignment Logic
Candidates are bucketed into categorical tiers based on the absolute final score:
*   **Top Match:** `Score >= 85.0`
*   **Strong Match:** `Score >= 70.0`
*   **Good Match:** `Score >= 50.0`
*   **Potentially Unsuitable:** `Score < 50.0`
