# INQUIRA-AI

Inquira AI – Multi-Agent Research Assistant
Overview

Inquira AI is an AI-powered Multi-Agent Research Assistant that automates the entire research workflow using specialized AI agents.

The system searches the web, extracts relevant information, generates a professional research report, and performs a critical review of the generated report.

The project demonstrates Agentic AI concepts using LangChain, Mistral AI, FastAPI, and a custom web interface.

Features
Search Agent
Finds recent and reliable information from the web
Collects relevant sources related to the research topic
Retrieves search snippets and URLs
Reader Agent
Selects the most relevant source
Scrapes detailed content from webpages
Extracts meaningful information for analysis
Writer Chain
Generates structured research reports
Creates:
Executive Summary
Key Findings
Detailed Analysis
Conclusion
Sources
Critic Chain
Reviews the generated report
Provides:
Research quality score
Strengths
Areas for improvement
Final verdict
Research Dashboard
Real-time pipeline visualization
Progress tracking
Recent research history
Report statistics
PDF export support
Architecture

Research Topic

↓

Search Agent

↓

Reader Agent

↓

Writer Chain

↓

Critic Chain

↓

Final Report + Review

Tech Stack
AI & LLM
Mistral AI
LangChain
Backend
FastAPI
Python
Frontend
HTML
CSS
JavaScript
Utilities
BeautifulSoup
Requests
Python Regex
PDF Export


# 🔭 Inquira AI – Multi-Agent Research Assistant

A production-quality full-stack research pipeline powered by **Mistral AI**, **LangChain**, **Tavily**, and **FastAPI** with a dark glassmorphism frontend.

---

## Architecture

```
User → Frontend (HTML/CSS/JS)
         ↓ POST /research
      FastAPI (app.py)
         ↓
      pipeline.py
       ├─ Search Agent  (Tavily + LangGraph ReAct)
       ├─ Reader Agent  (BeautifulSoup scraper)
       ├─ Writer Chain  (Mistral AI)
       └─ Critic Chain  (Mistral AI, JSON output)
         ↓ POST /download-pdf
      pdf_generator.py (ReportLab whitepaper)
```

---

## Project Structure

```
inquira/
├── backend/
│   ├── app.py            # FastAPI entry point
│   ├── pipeline.py       # Pipeline orchestrator
│   ├── agents.py         # Search/Reader agents, Writer/Critic chains
│   ├── my_tools.py       # Tavily search + BeautifulSoup scraper tools
│   ├── pdf_generator.py  # ReportLab PDF generation
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Copy and fill in your API keys
cp .env.example .env
# Edit .env:  MISTRAL_API_KEY=... TAVILY_API_KEY=...

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Backend is live at `http://localhost:8000`

### 2. Frontend

Open `frontend/index.html` directly in your browser, **or** serve it:

```bash
cd frontend
python -m http.server 3000
# then visit http://localhost:3000
```

The frontend will call `http://localhost:8000` by default.

---

## Environment Variables

| Variable          | Required | Description                        |
|-------------------|----------|------------------------------------|
| `MISTRAL_API_KEY` | ✅        | [Mistral AI](https://console.mistral.ai) API key |
| `TAVILY_API_KEY`  | ✅        | [Tavily](https://app.tavily.com) search API key  |

---

## API Reference

### `POST /research`

```json
// Request
{ "topic": "Quantum Computing" }

// Response
{
  "topic": "Quantum Computing",
  "search_results": "...",
  "scraped_content": "...",
  "report": "...",     // Markdown
  "feedback": {
    "score": 8,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "suggestions": ["..."]
  },
  "sources": [
    { "title": "...", "url": "https://..." }
  ],
  "timings": {
    "search": 4.2,
    "reader": 3.1,
    "writer": 6.8,
    "critic": 2.4
  }
}
```

### `POST /download-pdf`

```json
// Request
{
  "topic": "Quantum Computing",
  "report": "# Markdown report...",
  "sources": [{ "title": "...", "url": "..." }]
}
// Response: application/pdf (binary download)
```

---

## Deployment

### Backend → Render

1. Push `backend/` to a Git repo.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `MISTRAL_API_KEY`, `TAVILY_API_KEY`
6. Copy your Render URL (e.g. `https://inquira-api.onrender.com`).

### Frontend → Vercel

1. Push `frontend/` to a Git repo.
2. Import on [vercel.com](https://vercel.com) as a **Static Site**.
3. Add an environment variable or edit `app.js`:
   ```js
   // top of app.js
   const API_BASE_URL = "https://inquira-api.onrender.com";
   ```
   Or inject it at build time:
   ```html
   <!-- in index.html, before app.js -->
   <script>window.ENV_API_BASE_URL = "https://inquira-api.onrender.com";</script>
   ```
4. Deploy.

---

## Features

- **4-stage pipeline** with real-time progress visualization
- **Glassmorphism dark UI** – responsive on desktop and mobile
- **Research history** – last 10 topics stored in localStorage, clickable to re-run
- **Professional PDF** – whitepaper-style with clickable sources (ReportLab)
- **Critic scoring** – structured JSON feedback (score/strengths/weaknesses/suggestions)
- **Error handling** – API failures, timeouts, missing keys all displayed gracefully
- **Copy to clipboard** – one-click report copy
