# TalentMind AI Hack2Skill Demo Script

This script outlines the screen-by-screen visual flow of the video demonstration. The Playwright automation drives these actions sequentially, allowing the presenter to sync narration.

---

## Part 1: Architecture, Scale & Documentation (0:00 - 0:45)
*   **Visual Focus:** IDE/GitHub repository structure, documentation files under `docs/`, and backend setup.
*   **Action Flow:**
    1.  Show repository structure: `backend/`, `frontend_screens/`, `docs/`.
    2.  Open `docs/architecture.md` and show the Decoupled System Architecture diagram.
    3.  Open `docs/dataset_scale_validation.md` to demonstrate ingestion of the 100,001 candidates.
    4.  Briefly show the FastAPI terminal or code entry point `backend/app/main.py`.

---

## Part 2: The Command Center — Dashboard & Scale (0:45 - 1:30)
*   **Visual Focus:** `dashboard.html`
*   **Action Flow:**
    1.  Open the dashboard. Highlight the "Total Candidates" metric: **100,001 Ingested Candidates**.
    2.  Show the live database status indicator (green badge "API Online").
    3.  Show "Recent Job Openings" table containing seeded roles (e.g. AI Engineer, frontend, backend).
    4.  Hover over the "Job Description Intelligence" upload area. Programmatically simulate dropping a Job Description file or choosing a pre-parsed job to show real-time extraction of key skills, experience thresholds, and disqualifiers.

---

## Part 3: Search & Discovery at 100k Scale (1:30 - 2:00)
*   **Visual Focus:** `candidate_search.html`
*   **Action Flow:**
    1.  Navigate to "Candidate Search" via the sidebar.
    2.  Filter by Skill (e.g., "React.js" or "PyTorch"), Experience (>5 years), and Location (Remote).
    3.  Click "Apply Filters" and watch the platform query the 100,001 candidate SQLite database in milliseconds using indexed columns.
    4.  Select a few matching candidates for a visual "Comparison" later.

---

## Part 4: Hybrid Match & Rank Engine (2:00 - 2:45)
*   **Visual Focus:** `candidate_ranking.html`
*   **Action Flow:**
    1.  Navigate to "Ranking" via the sidebar.
    2.  Select the **AI/Search Engineer** job role.
    3.  Click "Generate Rankings" to execute the multi-variate ranker. The progress bar completes, showing a ranked table of top candidates.
    4.  Show the component scores: Skills (30%), Experience (20%), Semantic Overlap (15%), Education (15%), Behavioral Signals (10%), Location Compatibility (10%).
    5.  Hover over the "Fit Score" to show the tooltips and explicit disqualifiers (e.g., title-chasers, consulting-only backgrounds, AI wrapper penalty).

---

## Part 5: Groq AI Recruiter Reranking & XAI (2:45 - 3:30)
*   **Visual Focus:** `candidate_ranking.html` & `candidate_details.html`
*   **Action Flow:**
    1.  On the ranking screen, click "Trigger Groq Reranking".
    2.  Watch the AI refine the rankings with qualitative LLM reasoning. Show the updated order and the "Groq Badge" next to reranked scores.
    3.  Click "View Profile" on the top candidate (Alexander Vance or Elena Rodriguez).
    4.  Navigate to Candidate Details. Show the "AI Insights" panel highlighting:
        *   **Key Strengths:** Scalability Mindset, Lead Experience.
        *   **Potential Risks:** Retention Probability (74% risk of counter-offer), Role Overqualification.
        *   **Hiring Recommendation:** Offer package generation.
    5.  Observe the "Skills Spectrum" radar chart illustrating technical fit.

---

## Part 6: Candidate Comparison & Skill Gap Analysis (3:30 - 4:00)
*   **Visual Focus:** `candidate_comparison.html` & `skill_gap_analysis.html`
*   **Action Flow:**
    1.  Select "Comparison" in the sidebar. Show the side-by-side comparison of 3 candidates (e.g. Elena, Alexander, and another).
    2.  Highlight the color-coded skill grids and behavioral signals compared visually.
    3.  Navigate to "Skill Gap" to show the automatically generated upskilling roadmaps for candidates who fell slightly short of required skills, demonstrating the platform's applicant-centric value.

---

## Part 7: Recruiter Copilot & Submission Verification (4:00 - 4:30)
*   **Visual Focus:** `recruiter_copilot.html` & FastAPI `/docs` (Swagger UI)
*   **Action Flow:**
    1.  Navigate to "Recruiter Copilot".
    2.  See the conversational interface. The script types: *"Let's go with the outreach email. Mention her blog post on micro-frontends."* and generates a beautiful, ready-to-send outreach message in real-time using Groq.
    3.  Transition to the FastAPI Swagger UI (`http://127.0.0.1:8000/docs`).
    4.  Scroll through the clean, documented endpoints showing the robust backend structure.
    5.  Show the `/api/submission/generate` and show that validation passes with a clean `submission.csv` conforming to the challenge requirements.
