# Groq Recruiter Re-Ranking

TalentMindAI implements a multi-stage candidate screening pipeline. For high-accuracy recruiting, a secondary LLM-based re-ranking stage can be enabled.

---

## 1. Re-Ranking Pipeline Workflow

The ranking pipeline executes the following workflow:

1. **Phase 1 (Heuristic Screening):** Rank all candidates (e.g. 100,000 profiles) using the heuristic rules of `RankerService`.
2. **Phase 2 (Top 50 Extraction):** Extract the Top 50 candidates from the heuristic ranking results.
3. **Phase 3 (Parallelized Groq Evaluation):** Evaluate each of the top 50 candidates in parallel using the Groq API (`llama-3.1-8b-instant`).
4. **Phase 4 (Recalculate & Re-Sort):** Combine the scores and re-sort the Top 50 to form the final Top 20 short-list.

---

## 2. Score Combination Formula

The final candidate suitability score is computed as:

$$\text{final\_score} = 0.7 \times \text{RankerService Score} + 0.3 \times \text{Groq Score}$$

- **RankerService Score:** Normalized heuristic score (0-100 scale).
- **Groq Score:** LLM suitability score (0-100 scale).

---

## 3. Evaluation Criteria

The Groq prompt instructs the LLM to score each candidate on a 0-100 scale based on the following four dimensions:

1. **Skill Alignment:** Matching of candidate's technical skills with the job description.
2. **Experience Relevance:** Seniority, history length, and applicability of career accomplishments.
3. **Retrieval/Search Expertise:** Experience with vector search databases (FAISS, Milvus), information retrieval, hybrid search, recommendation engines, ranking, or RAG systems.
4. **Behavioral Signals:** Job-hopping frequency, professional stability, and cognitive/behavioral attributes from Redrob signals.

---

## 4. Usage

To run the pipeline with Groq Recruiter Re-ranking, use the `--groq-rerank` flag:

```bash
python backend/generate_submission.py --groq-rerank
```

You can also combine both LLM flags to parse the Job Description using the LLM AND re-rank candidates:

```bash
python backend/generate_submission.py --llm --groq-rerank
```

---

## 5. High Availability & Fallbacks

- **No API Key:** If the `GROQ_API_KEY` environment variable is not set, the pipeline skips the re-ranking step and preserves the heuristic sorting.
- **API Failures:** If an individual API call fails (rate-limit, timeout, network error), the service catches the exception and falls back to the candidate's original RankerService score, ensuring the pipeline completes successfully.
