# Groq-Powered Job Description Parsing

TalentMindAI supports optional LLM-powered Job Description (JD) parsing using the Groq API. This allows recruiters to utilize advanced language understanding to extract required skills, preferred skills, experience limits, education, and candidate disqualifiers.

---

## 1. Setup & API Key Configuration

To enable the Groq parser, set the `GROQ_API_KEY` environment variable in your environment:

### Windows (PowerShell)
```powershell
$env:GROQ_API_KEY="gsk_your_actual_groq_api_key"
```

### Linux/macOS
```bash
export GROQ_API_KEY="gsk_your_actual_groq_api_key"
```

---

## 2. Command Line Interface (CLI) usage

You can toggle between the default heuristic parser and the Groq LLM parser using the `--llm` CLI flag.

### Run with Groq LLM Parser
```bash
python backend/generate_submission.py --llm
```

### Run with Heuristic Parser (Default)
```bash
python backend/generate_submission.py
```

---

## 3. Extraction Schema

The Groq parser requests a JSON output adhering strictly to the following structure:

```json
{
  "required_skills": ["Python", "TensorFlow", "FAISS"],
  "preferred_skills": ["Kubernetes", "PyTorch"],
  "experience_required": 5.0,
  "education_requirements": ["B.Tech/M.Tech in Computer Science or related field"],
  "disqualifiers": ["Consulting-only backgrounds (TCS, Infosys, etc.)"]
}
```

---

## 4. Fallback Architecture

To ensure high availability and prevent workflow disruption, the Groq service employs a two-tier fallback architecture:

1. **API Key Absence Fallback:** If `GROQ_API_KEY` is not detected in the environment variables, the system logs a warning and automatically redirects parsing to the heuristic `JDAnalyzerService`.
2. **Runtime Error Fallback:** If the Groq API is down, returns an error (e.g. rate-limits, invalid key, timeout), or responds with invalid JSON, the service captures the exception and falls back to `JDAnalyzerService.analyze_detailed(text)`.
