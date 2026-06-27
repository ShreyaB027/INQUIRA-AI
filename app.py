"""
app.py – FastAPI entry point for Inquira AI.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Must happen before importing pipeline (which imports agents)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from pipeline import run_research_pipeline
from pdf_generator import generate_pdf


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Inquira AI – Multi-Agent Research Assistant",
    version="1.0.0",
    description="Automated research pipeline: search → read → write → critique",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    topic: str

class PDFRequest(BaseModel):
    topic: str
    report: str
    sources: list[dict] = []


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Inquira AI"}


@app.post("/research")
def research(req: ResearchRequest):
    """Run the full research pipeline and return all stage outputs."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    if len(topic) > 300:
        raise HTTPException(status_code=400, detail="Topic is too long (max 300 chars).")

    try:
        result = run_research_pipeline(topic)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse(content={
        "topic":          result.get("topic", topic),
        "search_results": result.get("search_results", ""),
        "scraped_content":result.get("scraped_content", ""),
        "report":         result.get("report", ""),
        "feedback":       result.get("feedback", {}),
        "sources":        result.get("sources", []),
        "timings":        result.get("timings", {}),
    })


@app.post("/download-pdf")
def download_pdf(req: PDFRequest):
    """Generate and return a PDF for the given report."""
    topic = req.topic.strip()
    report = req.report.strip()

    if not topic or not report:
        raise HTTPException(status_code=400, detail="topic and report are required.")

    try:
        pdf_bytes = generate_pdf(topic, report, req.sources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    safe_topic = "".join(c if c.isalnum() or c in "- " else "_" for c in topic)[:60]
    filename = f"Inquira_Report_{safe_topic.replace(' ', '_')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
