# TalentMind AI Hack2Skill Demo Runbook

This runbook describes the steps required to execute, record, and verify the automated TalentMind AI video demonstration.

---

## 🏗️ 1. Prerequisites & Environment Setup

Ensure your local development environment has all the dependencies configured.

### Python Environment
Ensure the python virtual environment is activated and dependencies are installed:
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install playwright fastapi uvicorn pydantic sqlalchemy jinja2 python-docx scikit-learn pandas groq httpx
playwright install chromium
```

### Groq API Key Setup
The parser and reranker rely on Groq. Set your `GROQ_API_KEY` before starting the server:
```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
```

### Database Verification
Ensure the SQLite database exists and has candidates populated:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('backend/talentmind.db'); print('Candidate Count:', conn.execute('SELECT COUNT(*) FROM candidates').fetchone()[0])"
```
*Expected Output: `Candidate Count: 100001`*

---

## 🚀 2. Starting the Backend Server

Start the FastAPI backend server on port 8000:
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```
Verify the server is running by opening `http://127.0.0.1:8000/` or checking `/docs` in your browser.

---

## 🎥 3. OBS Studio Configuration

Configure OBS Studio to record the automated browser window seamlessly.

1.  **Scene Setup:**
    *   Create a new scene called **TalentMind AI Demo**.
2.  **Sources:**
    *   Add a **Window Capture** source targeting the Chromium browser launched by the Playwright script.
    *   Alternatively, add a **Display Capture** source if you want to capture the VS Code environment transition.
3.  **Audio Configuration:**
    *   Select your primary microphone as the input device.
    *   Ensure **Desktop Audio** is muted or kept at low levels to prevent feedback.
4.  **Video Settings:**
    *   Base canvas resolution: `1920x1080`.
    *   Output resolution: `1920x1080`.
    *   Frame rate: `30 FPS` or `60 FPS`.
5.  **Hotkeys:**
    *   Set `F9` for **Start Recording** and `F10` for **Stop Recording**. This makes it easy to control OBS without showing the OBS interface in the video.

---

## 🏃‍♂️ 4. Running the Demo Automation

1.  Start your backend server.
2.  Launch OBS Studio.
3.  Run the Playwright script from the project root:
    ```powershell
    python scratch/run_demo.py
    ```
4.  The script will launch Chromium in headed mode and pause at the starting screen.
5.  Press `F9` to start OBS Recording.
6.  Press `Enter` in the terminal/console to trigger the automation path.
7.  Read the `demo_narration.md` script aloud, matching your voice to the browser's actions. The automation includes built-in delays to give you enough time to narrate.
8.  Once the script finishes (it will close the browser), press `F10` to stop OBS Recording.

---

## 🛠️ 5. Troubleshooting & FAQ

#### Port 8000 is already in use
If uvicorn fails with `[Errno 10048] error while attempting to bind on address`, check for running uvicorn processes and terminate them:
```powershell
Stop-Process -Name "python" -Force
```

#### Groq API Rate Limiting / Timeout
The ranker has automatic exponential backoff configured. If it times out or encounters API limits, the Playwright script is built to fall back gracefully to pre-calculated rankings, ensuring your live recording never crashes.

#### Playwright fails to find chromium
Run:
```powershell
playwright install chromium
```
