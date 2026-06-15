# TalentMindAI System Architecture

## 1. Project Overview
TalentMindAI is an offline-capable, AI-driven recruitment intelligence platform. The frontend relies on **Vanilla HTML and JavaScript** without a reactive framework, integrating with a FastAPI backend. The system automates the parsing of unstructured job descriptions, persisting of candidate profiles, and heuristic/semantic evaluation of candidates against structured job requirements to produce calibrated ranking pipelines and submission datasets.

## 2. System Architecture

```text
+-------------------------+
|  Frontend UI            |
|  (Vanilla HTML/JS)      |
|  frontend_screens/*.html|
+-----------+-------------+
            | HTTP/REST
            v
+-------------------------+
|  FastAPI Backend        |
|  (app/main.py)          |
+-----+-------------+-----+
      |             |
[API Routers]   [Services]
 (app/routes/)  (app/services/)
      |             |
+-----+-------------+-----+
|  SQLAlchemy ORM         |
|  (app/models/)          |
+-----------+-------------+
            |
+-----------+-------------+
|  SQLite Database        |
|  (data/talentmind.db)   |
+-------------------------+

+-----------------------------------------+
| Offline Batch Pipeline                  |
| (generate_submission.py)                |
| -> JDAnalyzerService -> RankerService   |
| -> submission.csv                       |
+-----------------------------------------+
```

## 3. Backend Components
*   **FastAPI Application (`app/main.py`)**: The main application entry point that initializes the app, configures CORS middleware, and mounts API routers.
*   **SQLAlchemy ORM (`app/database.py`)**: Manages the connection pool (`SessionLocal`) and declarative base for mapping Python objects to database tables.
*   **SQLite Database**: A local `talentmind.db` file operating as the primary data store, ensuring offline capabilities.
*   **`JDAnalyzerService` (`app/services/jd_analyzer.py`)**: A text-parsing engine that processes unstructured job descriptions using predefined heuristic markers to extract required/preferred skills, experience, and educational constraints.
*   **`RankerService` (`app/services/ranker_service.py`)**: The core evaluation engine that calculates a 0-100 match score between a candidate and a job using a hybrid of TF-IDF text similarity, exact skill matching, and heuristic penalties.
*   **`generate_submission.py`**: A standalone script that orchestrates the entire offline evaluation pipeline, processing a text job description against all candidates in the database and exporting the results to a CSV file.
*   **`evaluate_ranking.py`**: An offline validation script used to test the precision and recall of the ranking engine against a ground-truth relevance function.

## 4. API Layer
The FastAPI endpoints are modularized in `app/routes/`:
*   `candidates.py`: Handles fetching, filtering, and aggregating candidate profile data.
*   `jobs.py`: Handles creating, listing, and retrieving job requirements.
*   `ranking.py`: Triggers manual or ad-hoc candidate evaluations for specific jobs.
*   `submission.py`: Orchestrates generating the final pipeline output and API representations of submission datasets.
*   `copilot.py`: Manages the interactive/LLM-like responses or AI-assisted review endpoints.

## 5. Database Layer
The data schema is mapped using SQLAlchemy in `app/models/`:
*   `candidate.py` (`Candidate`): Represents applicant profiles, including embedded arrays for skills, education, career history, and `redrob_signals` (behavioral metrics).
*   `job.py` (`Job`): Represents structured job definitions (title, required experience, extracted required skills).
*   `ranking.py` (`Ranking`): A junction table storing historical or persistent evaluation scores connecting a `Candidate` to a `Job`.
*   `audit.py` (`AuditLog`): Tracks system-level events and metadata changes.

## 6. Candidate Ranking Flow
The evaluation process operates sequentially as follows:
1.  **JD Input**: Unstructured text from a job description file or API input.
2.  **JD Analysis**: `JDAnalyzerService` splits the text by sections (Requirements, Preferred, Disqualifiers) using keyword markers.
3.  **Job Object**: The structured dictionaries are used to instantiate an ephemeral or persistent `Job` model.
4.  **Candidate Retrieval**: Active `Candidate` records are queried from the database.
5.  **Ranking Engine**: `RankerService.calculate_match(candidate, job)` is invoked for each pairing.
6.  **Scoring**: The engine computes a 0-100 base score (combining TF-IDF cosine similarity, skill subsets, and behavioral signals), applies role-fit multipliers, applies heuristic disqualifier penalties, and clips the score.
7.  **submission.csv**: Sorted output is written to a CSV file.

## 7. Submission Generation Flow
The exact execution path defined in `generate_submission.py`:
1.  **Read JD**: Opens `extracted_jd.txt` at the root/backend path.
2.  **Analyze**: Passes text to `JDAnalyzerService.analyze_detailed()`.
3.  **Mock Job**: Builds a temporary `Job` object in memory without persisting it to SQLite.
4.  **Fetch Candidates**: Executes `db.query(Candidate).all()`.
5.  **Filter Synthetics**: Explicitly filters out candidates containing `AUDIT`, `TEST`, `DEMO`, or `SAMPLE` in their `candidate_id`.
6.  **Evaluate**: Maps each valid candidate through `RankerService.calculate_match()`.
7.  **Write Results**: Creates `submission.csv` at the project root, writing `candidate_id`, `rank` (1-N), `score` (normalized to 0-1), and a structured `reasoning` string detailing profile completeness, response rate, matched skills, and gaps.

## 8. Current Limitations
*   **TF-IDF Semantic Bottleneck**: The semantic similarity module uses Scikit-learn's `TfidfVectorizer`, which relies heavily on exact keyword/n-gram overlap. It does not understand synonyms or dense contextual embeddings, artificially suppressing scores for differently phrased resumes.
*   **Rigid Heuristic Penalties**: The ranking engine applies hard-coded multipliers (e.g., `-10%` for consulting-only history, `-10%` for wrapper-only AI skills) which can be brittle if candidate data formatting varies.
*   **Offline/Text Dependency**: `generate_submission.py` strictly depends on the presence of `extracted_jd.txt` existing in the file system to run the offline batch pipeline.
