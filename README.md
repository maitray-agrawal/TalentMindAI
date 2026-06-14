# TalentMind AI Recruitment Platform

TalentMind AI is an AI-powered talent intelligence and recruitment automation platform. It automates the candidate screening process, analyzes unstructured job descriptions, performs multi-criteria ranking, and maps upskilling pathways to bridge skill gaps between candidates and roles.

---

## Key Features

1. **Job Description Intelligence (Phase 3)**
   - Upload job description documents (`.docx`, `.txt`) using a drag-and-drop widget.
   - Heuristic extraction of crucial requirements: **Required Skills**, **Preferred Skills**, **Min Experience**, **Education Requirements**, **Location/Work Preferences**, **Culture Fit (Vibe Check)**, and **Disqualifiers**.
   - Interactive review and validation modal to verify parsed details before persisting the role.

2. **Match & Ranker Engine**
   - Ranks all stored candidates against active job descriptions.
   - Matches candidate skill profiles using a TF-IDF vectorizer and calculates custom cosine similarity.
   - Factors in years of experience, work location compatibility, and qualification tiers.

3. **Candidate Search & Stats**
   - Multi-criteria candidate search (by name, keyword, location, experience range, work mode preference, and skills).
   - Real-time platform candidate stats (distribution of experience levels, open-to-work percentage, top skills, and profile completeness).

4. **Skill Gap Analysis & Copilot Roadmaps**
   - Detail page mapping candidate skills against job requirements.
   - Automatically identifies missing technical skills and experience gaps.
   - Generates a step-by-step learning roadmap with recommended resources (e.g. DeepLearning.AI, Fast.ai) and hands-on projects to close gaps.

---

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy (ORM), SQLite (Database), Uvicorn (ASGI Server), Scikit-Learn (TF-IDF Vectorization & Similarity), Numpy, Pandas.
- **Frontend**: Vanilla HTML5, CSS3, Tailwind CSS (Glassmorphism layout theme), native JavaScript (asynchronous UI updates and API connectivity).

---

## Repository Structure

```text
TalentMindAI/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy DB schemas
│   │   ├── routes/       # FastAPI endpoints (jobs, candidates, ranking, copilot)
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
├── requirements.txt      # Python dependencies list
└── README.md             # Project documentation
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
