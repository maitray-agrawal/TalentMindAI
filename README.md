# TalentMind AI 🧠💼

**TalentMind AI** is an intelligent talent discovery and recruitment automation platform. Designed for the modern talent acquisition landscape, it leverages Explainable AI (XAI), semantic matching, and behavioral signal processing to bridge the gap between complex job descriptions and vast candidate pools.

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
    *   **JD Analyzer:** Parses `.docx` and unstructured text to extract hard requirements, preferred skills, education, and cultural vibe checks.
    *   **Ranker Engine:** Computes a multi-variate compatibility score using TF-IDF (Term Frequency-Inverse Document Frequency) text similarity, semantic skill bucketing, experience curve matching, and behavioral signal processing.
*   **Data Persistence:** SQLAlchemy ORM backed by an efficient SQLite database.

---

## 📊 Dataset

The platform is built to ingest and process complex candidate profiles, supporting the **Redrob "India Runs Data and AI Challenge"** schema. 

**Key candidate data points include:**
*   **Profile & Career History:** Deep nested arrays detailing companies, titles, durations, and role descriptions.
*   **Education & Skills:** Tiered education histories and multi-level skill proficiency matrices.
*   **Redrob Behavioral Signals:** Real-world simulated engagement metrics such as `recruiter_response_rate`, `profile_completeness_score`, `open_to_work_flag`, and `github_activity_score`.

---

## ✨ Features

1.  **Job Description Intelligence:** Drag-and-drop unstructured `.docx` files to automatically extract required skills, experience thresholds, and explicit disqualifiers.
2.  **Explainable Match & Rank Engine:** Ranks candidate pools from 1 to 100 with comprehensive sub-scores (Skills, Experience, Semantic, Education, Behavioral) and generates human-readable reasoning for every recommendation (e.g., "Strong Hire", "Consider", "Pass").
3.  **Skill Gap Analysis & Copilot Roadmaps:** Dynamically identifies missing skills and generates targeted learning roadmaps (courses, projects) to help candidates upskill.
4.  **Recruiter Copilot (GenAI):** A conversational AI assistant that drafts personalized outreach emails and summarizes candidate strengths/weaknesses.
5.  **Multi-Candidate Comparison Matrix:** Select up to 10 candidates from the search grid and compare their metrics side-by-side.

---

## 🔌 Core APIs

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/candidates/import` | `POST` | Bulk streams and ingests `.jsonl` candidate datasets. |
| `/candidates/search` | `GET` | Multi-criteria search by skills, experience, and location. |
| `/ranking/rank/{job_id}` | `POST` | Triggers the AI pipeline to rank all candidates against a specific role. |
| `/candidates/{id}/explanation` | `GET` | Returns human-readable XAI justifications for a candidate's rank. |
| `/candidates/compare` | `POST` | Generates a detailed comparison matrix across multiple candidate IDs. |
| `/copilot/chat` | `POST` | AI assistant for drafting emails and building upskilling roadmaps. |

---

## 🖼️ Screenshots

*(Screenshots available as interactive HTML in `/frontend_screens/`)*

*   !Dashboard *Recruiter Dashboard & KPIs*
*   !Ranking *Explainable AI Ranking View*
*   !Comparison *Candidate Comparison Matrix*
*   !Skill Gap *Automated Skill Gap Analysis*

---

## 📂 Repository Structure

```text
TalentMindAI/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy DB schemas
│   │   ├── routes/       # FastAPI endpoints
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── services/     # Core logic (JD Analyzer, Ingestion, Ranker, Copilot)
│   │   ├── database.py   # Connection session setup
│   │   ├── main.py       # FastAPI app initialization
│   │   └── seed.py       # Mock database seeder
│   └── tests/            # Pytest unit & integration tests
├── frontend_screens/     # HTML / CSS / JS UI elements
│   ├── dashboard.html    # Core Recruiter Dashboard
│   ├── integration.js    # Client-side API orchestration
│   └── ...               # Additional interface views (rankings, comparison, skill gap)
├── evaluate_ranking.py   # IR evaluation metrics (Precision/Recall) script
└── requirements.txt      # Python dependencies
```

---

## Getting Started

### 1. Backend Setup & Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the dependencies listed in the root `requirements.txt`:
   ```bash
   pip install -r ../requirements.txt
   ```

4. Seed the SQLite database with mockup candidates and roles:
   ```bash
   python -m app.seed
   ```

5. Run the FastAPI dev server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   The backend API will run at `http://127.0.0.1:8000` (docs available at `/docs`).

### 3. Generate Submission Output
```bash
    cd backend
    python generate_submission.py
```
    This regenerates `submission.csv` in the project root with the 
    correct AI-ranked candidate output.

### 2. Frontend Launch

Open `frontend_screens/dashboard.html` directly in any web browser (`file:///` protocol) or serve it locally. 
- Ensure the backend server is running on port `8000` so client-side API requests from `integration.js` succeed.
- Check the top-right header indicator to verify that the status displays **API: CONNECTED**.

---

## Testing & Validation

To run the unit tests for the ingestion pipeline, candidate matching, and service layers, run the following from the `backend/` directory:

```bash
python -m unittest tests/test_ingestion.py
python -m unittest tests/test_backend.py
```
