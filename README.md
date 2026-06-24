# TalentMind AI 🧠💼

**TalentMind AI** is an intelligent talent discovery and recruitment automation platform. Designed for the modern talent acquisition landscape, it leverages **Explainable AI (XAI)**, semantic matching, and behavioral signal processing to bridge the gap between complex job descriptions and vast candidate pools.

---

## 🎯 Problem Statement

Modern recruitment is broken. Traditional Applicant Tracking Systems (ATS) rely on rigid keyword matching, which leads to massive false positives (e.g., a "Marketing Manager" matching an "AI Engineer" role because they stuffed their resume with tech buzzwords) and false negatives (missing great candidates who describe their experience differently). 

Recruiters need a system that understands **context, semantic skill overlap, behavioral engagement signals, and explicit job disqualifiers**—evaluating candidates the way a human engineering manager would.

---

## 🏗️ Architecture

TalentMind AI uses a decoupled, high-performance architecture:

*   **Client Layer:** A reactive Vanilla JS / HTML5 frontend utilizing Tailwind CSS for a premium "Glassmorphism" UI.
*   **API Gateway:** FastAPI acts as the lightning-fast ASGI gateway.
*   **Intelligence Layer:** 
    *   **JD Analyzer:** Parses `.docx` and unstructured text to extract hard requirements, preferred skills, education, and cultural vibe checks (supports heuristic & Groq LLM-based parsing).
    *   **Ranker Engine:** Computes a multi-variate compatibility score using TF-IDF (Term Frequency-Inverse Document Frequency) text similarity, semantic skill bucketing, experience curve matching, and behavioral signal processing.
    *   **Groq GenAI Services:** Extends the parser (`GroqJDService`) and ranker (`GroqReranker`) with qualitative LLM evaluations and automatic exponential backoff to handle rate limits.
*   **Data Persistence:** SQLAlchemy ORM backed by an efficient SQLite database.

---

## 📊 Dataset

The platform is built to ingest and process complex candidate profiles, supporting the **Redrob "India Runs Data and AI Challenge"** schema. 

**Key candidate data points include:**
*   **Profile & Career History:** Deep nested arrays detailing companies, titles, durations, and role descriptions.
*   **Education & Skills:** Tiered education histories and multi-level skill proficiency matrices.
*   **Redrob Behavioral Signals:** Real-world simulated engagement metrics such as `recruiter_response_rate`, `profile_completeness_score`, `open_to_work_flag`, and `github_activity_score`.

---

## 📈 Multi-Variate Scoring Methodology

The `RankerService` evaluates candidates against a job description using a hybrid of semantic similarity, heuristic rules, and behavioral signals to generate a final normalized score between `0` and `100`.

### 1. Six-Pillar Component Weights
*   **Skills (30%):** Evaluates candidate capabilities using a weighted blend of semantic categories (80%) and exact keyword matches (20%). Includes an absolute `+0.20` boost (capped at 1.0) if the candidate has proven search/retrieval experience.
*   **Experience (20%):** A linear ratio comparing total years of experience against the job's requirements.
*   **Semantic Overlap (15%):** Uses Scikit-learn's `TfidfVectorizer` (unigrams/bigrams) to calculate cosine similarity between the candidate's profile text and the job description, scaled by `1.5` to offset vocabulary baselines.
*   **Education (15%):** Analyzes listed degrees. Awards points based on degree levels (+0.20 for PhD, +0.10 for Masters), STEM majors (+0.20), and Tier-1 institution classification (+0.20).
*   **Behavioral Signals (10%):** Derived from Redrob platform indicators: Profile Completeness (40%), Open to Work (20%), GitHub Activity (20%), and Recruiter Response Rate (20%).
*   **Location Compatibility (10%):** Evaluates work preference (Remote, Onsite, Hybrid) and geographic alignment.

### 2. Role Fit Multipliers
Applied post-scoring to align candidates' titles with technical roles:
*   **Direct AI / Search engineering match:** `1.0x`
*   **Software Engineers (without retrieval exp) applying to AI jobs:** `0.95x`
*   **DevOps / QA applying to AI jobs:** `0.80x`
*   **Business Analysts:** `0.60x`
*   **Non-technical roles (HR, Marketing, Sales):** `0.15x`

### 3. Disqualifier Penalties
*   **Consulting-Only Background:** `-10%` penalty (`0.90x` multiplier) if career history consists entirely of IT consulting firms.
*   **Title-Chasers:** `-5%` penalty (`0.95x` multiplier) if average tenure is under 15 months.
*   **AI Wrapper-Only:** `-10%` penalty (`0.90x` multiplier) if listing wrapper tools (LangChain, OpenAI) but lacking core ML frameworks (PyTorch, TensorFlow, FAISS).

---

## ✨ Features

1.  **Job Description Intelligence:** Drag-and-drop unstructured `.docx` files to automatically extract required skills, experience thresholds, and explicit disqualifiers. Supports both heuristic and LLM-assisted parsing.
2.  **Explainable Match & Rank Engine:** Ranks candidate pools with comprehensive sub-scores and provides human-readable explanations.
3.  **Explainable AI Insights (XAI):** A dedicated endpoint fetches candidate-to-job matching explanations, categorizing "Why Matched", "Key Strengths", "Potential Risks/Weaknesses", and "Hiring Recommendations" inside the Candidate Details screen.
4.  **Skill Gap Analysis & Copilot Roadmaps:** Dynamically identifies missing skills and generates targeted learning roadmaps (courses, projects) to help candidates upskill.
5.  **Recruiter Copilot (GenAI):** A conversational AI assistant that drafts personalized outreach emails and summarizes candidate profiles.
6.  **Multi-Candidate Comparison Matrix:** Select multiple candidates from the search grid and compare their metrics side-by-side.

---

## 🔌 Core APIs

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/candidates/import` | `POST` | Bulk streams and ingests `.jsonl` candidate datasets. |
| `/api/candidates/search` | `GET` | Multi-criteria search by skills, experience, and location. |
| `/api/ranking/rank/{job_id}` | `POST` | Triggers the AI pipeline to rank all candidates against a specific role. |
| `/api/candidates/{id}/explanation` | `GET` | Returns human-readable XAI justifications for a candidate's rank. |
| `/api/candidates/compare` | `POST` | Generates a detailed comparison matrix across multiple candidate IDs. |
| `/api/copilot/chat` | `POST` | AI assistant for drafting emails and building upskilling roadmaps. |
| `/api/submission/generate` | `POST` | Compiles and validates the candidate rankings to export `submission.csv`. |

---

## 📂 Repository Structure

```text
TalentMindAI/
├── backend/
│   ├── app/
│   │   ├── models/           # SQLAlchemy DB models (candidate, job, ranking, audit)
│   │   ├── routes/           # FastAPI routers (candidates, jobs, ranking, copilot, submission)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Core logic (JD Analyzer, Ingestion, Ranker, Copilot, Groq services)
│   │   ├── database.py       # Connection session setup
│   │   ├── main.py           # FastAPI app initialization
│   │   └── seed.py           # Mock database seeder
│   ├── tests/                # Pytest unit & integration tests
│   ├── evaluate_ranking.py   # IR evaluation script (Precision@K, Recall@K)
│   ├── generate_submission.py# Challenge submission CSV compiler (supporting heuristic & LLM blending)
│   ├── validate_submission.py# Local validation compliance script
│   └── verify_ranking.py     # Core ranking validation & profiling
├── docs/                     # Comprehensive architecture, scoring, and benchmarking reports
├── frontend_screens/         # HTML / CSS / JS UI elements
│   ├── dashboard.html        # Recruiter Dashboard
│   ├── candidate_details.html# Candidate Details & XAI Insights view
│   └── integration.js        # Client-side API orchestration
├── requirements.txt          # Python dependencies
└── submission.csv            # Final generated CSV submission
```

---

## Getting Started

### 1. Backend Setup & Installation

1. From the project root directory, create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Groq API Key (required for AI Reranking and Copilot):
   ```bash
   # On Windows PowerShell:
   $env:GROQ_API_KEY="your-groq-api-key"
   # On macOS/Linux:
   export GROQ_API_KEY="your-groq-api-key"
   ```

4. Navigate to the backend directory and start the FastAPI server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
   *The backend API will now run at `http://127.0.0.1:8000` (interactive docs available at `/docs`).*

### 2. Frontend Setup

The frontend is built with vanilla HTML/JS and TailwindCSS. It does not require a build step.
1. Simply open `frontend_screens/dashboard.html` in your web browser.
2. Alternatively, use a tool like VS Code Live Server to serve the `frontend_screens` directory.

### 2. Generate Submission Output
To compile, sort, and export the top 100 candidates based on the parsed job description in `extracted_jd.txt`:
```bash command
cd backend
# Run heuristic ranking:
python generate_submission.py

# Run with LLM Job Description parsing and Groq reranking:
python generate_submission.py --llm --groq-rerank
```
This generates `submission.csv` in the project root.

### 3. Run Submission Validator
To verify that the generated `submission.csv` complies with the challenge parameters (exactly 100 non-duplicated rows, correct format, sorted order):
```bash
cd backend
python validate_submission.py
```

### 4. Frontend Launch

Open `frontend_screens/dashboard.html` directly in any web browser (`file:///` protocol) or serve it locally. 
- Ensure the backend server is running on port `8000` so client-side API requests from `integration.js` succeed.
- Check the top-right header indicator to verify that the status displays **API: CONNECTED**.

---

## Testing & Evaluation

### 1. Automated Tests
To run unit and integration tests for the ingestion pipeline, candidate matching, and service layers, execute the following from the `backend/` directory:
```bash
python -m unittest tests/test_ingestion.py
python -m unittest tests/test_backend.py
```

### 2. IR Evaluation
To run the Information Retrieval (IR) evaluation metrics comparing ranked output against ground-truth parameters:
```bash
cd backend
python evaluate_ranking.py
```
This generates a detailed evaluation report at `evaluation_report.md` detailing **Precision@10**, **Precision@20**, and **Recall@20**.

---

## ⚡ Scale Validation & Benchmarking

TalentMindAI has been benchmarked and validated on the complete Hack2Skill recruitment dataset.

*   **Total Candidates Processed:** 100,000 candidates
*   **Heuristic Processing Speed:** **361.51 candidates/second**
*   **Heuristic Phase Runtime:** 276.62 seconds (4.61 minutes)
*   **Peak Memory Usage:** **2.93 GB**
*   **Database Ingestion Validation:** 100,001 total database entries (100k + 1 synthetic check candidate)

**Result:** The pipeline achieves 100% dataset coverage, running smoothly without socket timeouts or memory leaks.