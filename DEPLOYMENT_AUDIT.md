# TalentMindAI — Deployment Readiness Audit

**Date:** 2026-09-22  
**Target Architecture:** Frontend → Vercel | Backend/API → Render | LLM → Groq API  
**Auditor:** Senior DevOps Engineer  
**Status:** ⛔ NOT READY — 7 Blockers identified

---

## Table of Contents

- [E. BLOCKERS — Must resolve before any deploy](#e-blockers)
- [B. MUST FIX — Required for production](#b-must-fix)
- [C. SHOULD FIX — Strongly recommended](#c-should-fix)
- [D. OPTIONAL — Nice to have](#d-optional)
- [A. READY — No action needed](#a-ready)
- [Render Configuration](#render-configuration)
- [Vercel Configuration](#vercel-configuration)
- [Deployment Sequence](#deployment-sequence)

---

## E. BLOCKERS

> **⛔ CAUTION: These 7 issues will cause the deployment to fail outright. All must be resolved before deploying.**

### BLOCKER-1: Frontend hardcoded `API_BASE` pointing to `127.0.0.1`

| Property | Detail |
|---|---|
| **File** | `frontend_screens/integration.js` line 6 |
| **Code** | `const API_BASE = 'http://127.0.0.1:8000/api';` |
| **Impact** | Every single API call from the frontend will fail once deployed to Vercel. The browser will send requests to `127.0.0.1:8000` (the user's localhost), not the Render backend. |
| **Affects** | **Vercel** (fatal) |
| **Fix** | Replace with `const API_BASE = '/api';` combined with a Vercel rewrite that proxies `/api/*` to the Render backend URL. |

---

### BLOCKER-2: Hardcoded Windows filesystem path in import endpoint

| Property | Detail |
|---|---|
| **File** | `backend/app/routes/candidates.py` line 28 |
| **Code** | `file_path = "d:\\TalentMindAI\\dataset\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\candidates.jsonl"` |
| **Impact** | This path does not exist on Render (Linux). The `/api/candidates/import` endpoint will always return a `404 FileNotFoundError`. |
| **Affects** | **Render** (fatal) |
| **Fix** | Remove the hardcoded default. Either require `file_path` as mandatory, set a relative default using `BASE_DIR`, or remove the default entirely. |

---

### BLOCKER-3: Hardcoded Windows path in submission CSV writer

| Property | Detail |
|---|---|
| **File** | `backend/app/routes/submission.py` line 145 |
| **Code** | `workspace_csv_path = r"d:\TalentMindAI\submission.csv"` |
| **Impact** | Render runs on Linux. This `d:\` path does not exist and will throw an exception. While the code has a try/except making it non-blocking for the HTTP response, it still generates errors in logs and the file is never persisted. |
| **Affects** | **Render** (fatal functionality loss) |
| **Fix** | Use a relative path from `BASE_DIR`, write to `/tmp`, or remove the local-write entirely (the streaming response already returns the CSV). |

---

### BLOCKER-4: 648 MB SQLite database is not deployable to Render

| Property | Detail |
|---|---|
| **File** | `backend/data/talentmind.db` |
| **Size** | **648 MB** |
| **Impact** | This file is gitignored (`*.db` in `.gitignore`), so it will **not** be present on Render after deploy. The app starts, creates an empty DB via `Base.metadata.create_all()`, and all 100,001 candidate records are lost. The application will serve empty results for every query. |
| **Affects** | **Render** (fatal — no data) |
| **Fix** | **Recommended: Migrate to Render PostgreSQL.** Alternatives: persistent disk, cloud storage download on startup, or bundled JSONL with ingestion on first deploy. |

---

### BLOCKER-5: SQLite is ephemeral on Render — all writes are lost on redeploy

| Property | Detail |
|---|---|
| **File** | `backend/app/config.py` line 12 |
| **Code** | `DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/talentmind.db")` |
| **Impact** | Render's free and starter tiers use ephemeral filesystems. Every new deploy, restart, or auto-scale event wipes the filesystem. All candidate data, rankings, audit logs, and new jobs will be permanently lost. |
| **Affects** | **Render** (fatal — data loss) |
| **Fix** | Migrate to **Render PostgreSQL**. Change `DATABASE_URL` to the Render-provided PostgreSQL connection string. Add `psycopg2-binary` to requirements. |

---

### BLOCKER-6: `check_same_thread=False` is SQLite-only — will crash with PostgreSQL

| Property | Detail |
|---|---|
| **File** | `backend/app/database.py` line 8 |
| **Code** | `connect_args={"check_same_thread": False}` |
| **Impact** | If you switch `DATABASE_URL` to PostgreSQL without removing this, SQLAlchemy will throw `TypeError: Invalid argument 'check_same_thread'` and the app will crash on startup. |
| **Affects** | **Render** (fatal if migrating to PostgreSQL) |
| **Fix** | Conditionally apply: `connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}` |

---

### BLOCKER-7: No `load_dotenv()` call — env var documentation gap

| Property | Detail |
|---|---|
| **File** | `backend/app/config.py` |
| **Impact** | `python-dotenv` is listed in `requirements.txt` but `load_dotenv()` is **never called** anywhere in the codebase. No `.env.example` exists to document required env vars (`DATABASE_URL`, `GROQ_API_KEY`, `FRONTEND_URL`). |
| **Affects** | **Both** (development friction; production env var documentation gap) |
| **Fix** | Add `from dotenv import load_dotenv; load_dotenv()` in `config.py`. Create `.env.example`. |

---

## B. MUST FIX

> **🔴 WARNING: These issues will cause significant functionality failures or degraded service in production.**

### MF-1: CORS `allow_origins=["*"]` with `allow_credentials=True`

| Property | Detail |
|---|---|
| **File** | `backend/app/main.py` lines 17-24 |
| **Code** | `allow_origins=["*"], allow_credentials=True` |
| **Impact** | Per CORS spec, browsers **reject** responses with `Access-Control-Allow-Origin: *` when `Allow-Credentials: true` is also set. Also `"*"` is too permissive for production. |
| **Affects** | **Both** |
| **Fix** | Set `allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")]`. |

---

### MF-2: Ranking loads ALL 100k candidates into memory (OOM risk)

| Property | Detail |
|---|---|
| **File** | `backend/app/routes/ranking.py` line 27 |
| **Code** | `candidates = db.query(Candidate).all()` |
| **Impact** | Loads 100k candidate ORM objects (~300-500 MB) into memory + TF-IDF vectorization. On Render Free (512 MB RAM): OOM kill. |
| **Affects** | **Render** (OOM crash) |
| **Fix** | Use `.yield_per(1000)`, pre-compute rankings, or add SQL-side filtering. Use Render 2 GB+ plan. |

---

### MF-3: Generate ranking also loads ALL candidates

| Property | Detail |
|---|---|
| **File** | `backend/app/routes/ranking.py` line 169 |
| **Code** | `candidates = db.query(Candidate).all()` |
| **Impact** | Same OOM risk as MF-2. Called from frontend ranking page. |
| **Affects** | **Render** |

---

### MF-4: Submission generate loads all candidates if rankings empty

| Property | Detail |
|---|---|
| **File** | `backend/app/routes/submission.py` lines 38-56 |
| **Impact** | Same OOM risk — loads ALL candidates and computes rankings synchronously. |
| **Affects** | **Render** |

---

### MF-5: Groq reranker `time.sleep(4.0)` per candidate — request timeout

| Property | Detail |
|---|---|
| **File** | `backend/app/services/groq_reranker.py` line 87 |
| **Code** | `time.sleep(4.0)` — called for **each** candidate |
| **Impact** | For top_n=5: minimum 20-30 sec. Render HTTP timeout is 30 sec (free tier). Request terminated. |
| **Affects** | **Render** (timeout kill) |
| **Fix** | Move reranking to background task with status polling, or reduce sleep and use `Retry-After` headers. |

---

### MF-6: Groq API timeouts too short

| Property | Detail |
|---|---|
| **Files** | `groq_reranker.py` line 95 (`timeout=10`), `copilot_service.py` line 135 (`timeout=8`) |
| **Impact** | Under load, Groq LLM can take 10-15 seconds. Short timeouts cause frequent `TimeoutError` + compound retries. |
| **Affects** | **Render** |
| **Fix** | Increase to `timeout=30` (reranker) and `timeout=25` (copilot). |

---

### MF-7: `requirements.txt` missing production dependencies

| Property | Detail |
|---|---|
| **File** | `requirements.txt` |
| **Missing** | `psycopg2-binary` (required for PostgreSQL), `psutil` (optional monitoring) |
| **Affects** | **Render** |

---

## C. SHOULD FIX

> **🟡 IMPORTANT: These will cause degraded experience, security concerns, or maintainability issues.**

| # | Issue | File | Impact | Affects |
|---|---|---|---|---|
| SF-1 | No `.env.example` documenting required env vars | *(missing file)* | Deployment confusion | Both |
| SF-2 | `create_all()` at module import time | `main.py` L8 | DB errors block import | Render |
| SF-3 | Seed script only has 6 mockup candidates | `seed.py` | No production seed path | Render |
| SF-4 | Health check doesn't verify DB connectivity | `main.py` L42-44 | Render routes to broken instance | Render |
| SF-5 | No `render.yaml` | *(missing file)* | Manual config required | Render |
| SF-6 | No `vercel.json` | *(missing file)* | Auto-detect may fail | Vercel |
| SF-7 | Stats loads 10k skill arrays into Python | `candidates.py` L79 | Memory-intensive | Render |
| SF-8 | Search uses `ILIKE %text%` on `resume_text` | `candidates.py` L119-123 | Full table scan, 10-30s | Render |
| SF-9 | Copilot timeout too aggressive (8s) | `copilot_service.py` L135 | Intermittent failures | Render |
| SF-10 | `python-dotenv` in requirements but never loaded | `config.py` | Can't use `.env` locally | Both |

---

## D. OPTIONAL

| # | Issue | Impact | Affects |
|---|---|---|---|
| OPT-1 | Add JSON structured logging | Better log filtering on Render | Render |
| OPT-2 | Add `PORT` env var support | Render injects `PORT` automatically | Render |
| OPT-3 | Add rate limiting (`slowapi`) | Security hardening | Render |
| OPT-4 | Add `Cache-Control` headers for frontend | Performance improvement | Vercel |
| OPT-5 | Remove test `.db` files from filesystem | Filesystem cleanliness | Both |
| OPT-6 | Pin Python version via `runtime.txt` | Build reproducibility | Render |

---

## A. READY

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Backend entry point `app.main:app` | ✅ | Correct FastAPI app object |
| 2 | `requirements.txt` exists | ✅ | Core deps pinned |
| 3 | Gitignored database files (`*.db`) | ✅ | No DB files in git |
| 4 | Gitignored dataset (`dataset/`) | ✅ | 100k JSONL not committed |
| 5 | Gitignored `.env` | ✅ | API keys won't leak |
| 6 | Health check endpoint exists | ✅ | `GET /health` (needs enhancement) |
| 7 | Groq graceful fallback | ✅ | All 3 Groq services fall back when key missing |
| 8 | Groq 429 rate-limit handling | ✅ | Exponential backoff in all Groq services |
| 9 | Frontend is static HTML/CSS/JS | ✅ | Perfect for Vercel, zero build step |
| 10 | No uploaded file storage dependency | ✅ | JD upload processes in-memory |
| 11 | Submission CSV uses StreamingResponse | ✅ | Returns CSV as download |
| 12 | No background jobs / cron | ✅ | No BackgroundTasks or Celery |
| 13 | Swagger/OpenAPI auto-generated | ✅ | `/docs` works automatically |
| 14 | `venv/` gitignored | ✅ | Virtual environment excluded |

---

## Render Configuration

| Setting | Value |
|---|---|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r ../requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |
| **Required Env Vars** | `DATABASE_URL`, `GROQ_API_KEY`, `FRONTEND_URL` |
| **Minimum Plan** | Starter (2 GB RAM) — Free tier (512 MB) will OOM |

> **Note:** `requirements.txt` is at the repo root, not inside `backend/`. The build command must reference `../requirements.txt`.

---

## Vercel Configuration

| Setting | Value |
|---|---|
| **Root Directory** | `frontend_screens` |
| **Build Command** | *None* (static HTML, no build step) |
| **Output Directory** | `.` (serve from `frontend_screens/` root) |
| **Framework Preset** | Other (static) |
| **Frontend API Variable** | `API_BASE` in `integration.js` → change to `/api` |

**Recommended `vercel.json`:** Use rewrites to proxy `/api/*` to `https://talentmind-api.onrender.com/api/*`. This avoids CORS entirely.

---

## Environment Variables Summary

| Variable | Used In | Required | Platform |
|---|---|---|---|
| `DATABASE_URL` | `config.py` | Yes | Render |
| `GROQ_API_KEY` | `groq_reranker.py`, `copilot_service.py`, `groq_jd_service.py` | Yes | Render |
| `FRONTEND_URL` | `main.py` (CORS) | Yes | Render |
| `PORT` | Start command | Auto-injected | Render |

---

## Deployment Sequence

| # | Action | Details |
|---|---|---|
| **1** | **Resolve BLOCKERS** | Fix all 7 blocker issues in code |
| **2** | **Resolve MUST FIX** | Fix CORS, memory, timeouts, requirements |
| **3** | **Resolve SHOULD FIX** | Add `render.yaml`, `vercel.json`, `.env.example`, enhance health check |
| **4** | **Create Render PostgreSQL** | Dashboard → New → PostgreSQL. Copy internal `DATABASE_URL` |
| **5** | **Migrate schema** | Run one-time migration to create tables on PostgreSQL |
| **6** | **Seed production data** | Run ingestion of `candidates.jsonl` into PostgreSQL (100k records) |
| **7** | **Deploy backend to Render** | Connect repo → Set root dir `backend` → Set env vars → Deploy |
| **8** | **Verify backend** | Hit `/health` and `/docs`. Confirm 100k via `/api/candidates/stats` |
| **9** | **Configure frontend** | Update `API_BASE` to `/api`. Create `vercel.json` with rewrites |
| **10** | **Deploy frontend to Vercel** | Connect repo → Set root dir `frontend_screens` → Deploy |
| **11** | **Smoke test** | Test all 8 screens + Groq features (rerank, copilot, JD analysis) |
| **12** | **Custom domain** | Configure DNS for both Vercel and Render if needed |

---

## Final Verdict

| Category | Count |
|---|---|
| ⛔ BLOCKERS | 7 |
| 🔴 MUST FIX | 7 |
| 🟡 SHOULD FIX | 10 |
| 🔵 OPTIONAL | 6 |
| ✅ READY | 14 |

**The application is NOT deployment-ready.** The 7 blockers — particularly the 648 MB SQLite database issue, hardcoded Windows paths, and the hardcoded `127.0.0.1` API URL — must all be resolved before attempting any deployment to Render or Vercel.
