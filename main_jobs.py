"""
VouchAI v1 - Background Jobs Version
Uses in-memory job queue for long-running research
Suitable for platforms with strict timeout limits
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from analyst_team import run_research, ResearchOutput


# Load environment variables
load_dotenv()

# Verify API keys
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found")


# Initialize FastAPI
app = FastAPI(
    title="VouchAI API v1 - Jobs",
    description="Production-ready multi-agent research with background job processing",
    version="1.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Job Status Enum
class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Models
class ResearchRequest(BaseModel):
    query: str


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    created_at: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[int] = None
    message: str
    data: Optional[ResearchOutput] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


# In-memory job storage (use Redis in production)
jobs_db: Dict[str, Dict[str, Any]] = {}

LOG_FILE = Path("universal_research_evals.jsonl")


def log_research_evaluation(query: str, output: ResearchOutput) -> None:
    """Log research evaluation"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "professor_score": output.professor_eval_score.score,
        "professor_feedback": output.professor_eval_score.feedback,
        "hallucination_check": output.professor_eval_score.hallucination_check,
        "recommendations": output.professor_eval_score.recommendations
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


async def process_research_job(job_id: str, query: str):
    """Background task to process research"""
    try:
        # Update status to processing
        jobs_db[job_id]["status"] = JobStatus.PROCESSING
        jobs_db[job_id]["message"] = "Research in progress..."
        jobs_db[job_id]["progress"] = 10

        # Run research
        result = await run_research(query)

        # Update job with result
        jobs_db[job_id]["status"] = JobStatus.COMPLETED
        jobs_db[job_id]["message"] = "Research completed successfully"
        jobs_db[job_id]["data"] = result
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()

        # Log evaluation
        log_research_evaluation(query, result)

    except Exception as e:
        # Update job with error
        jobs_db[job_id]["status"] = JobStatus.FAILED
        jobs_db[job_id]["message"] = "Research failed"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()

        # Log error
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "error": str(e),
            "status": "failed"
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_log) + "\n")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "VouchAI v1 - Research You Can Vouch For (Background Jobs)",
        "status": "running",
        "version": "1.2.0",
        "domain": "vouchai.app",
        "features": {
            "background_jobs": "Queue research, poll for results",
            "no_timeout": "Long-running queries supported"
        }
    }


@app.post("/research/submit", response_model=JobResponse)
async def submit_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """
    Submit a research query for background processing
    Returns immediately with job_id
    """
    # Validate query
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Create job ID
    job_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    # Initialize job in database
    jobs_db[job_id] = {
        "job_id": job_id,
        "query": request.query,
        "status": JobStatus.QUEUED,
        "message": "Research queued for processing",
        "progress": 0,
        "data": None,
        "error": None,
        "created_at": created_at,
        "completed_at": None
    }

    # Add background task
    background_tasks.add_task(process_research_job, job_id, request.query)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="Research job submitted successfully. Use /research/status/{job_id} to check progress.",
        created_at=created_at
    )


@app.get("/research/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Check the status of a research job
    Poll this endpoint to get updates
    """
    # Check if job exists
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        data=job["data"],
        error=job["error"],
        created_at=job["created_at"],
        completed_at=job["completed_at"]
    )


@app.get("/research/jobs")
async def list_jobs() -> Dict[str, Any]:
    """List all jobs (last 50)"""
    all_jobs = list(jobs_db.values())
    # Sort by created_at descending
    sorted_jobs = sorted(
        all_jobs,
        key=lambda x: x["created_at"],
        reverse=True
    )[:50]

    return {
        "total": len(jobs_db),
        "showing": len(sorted_jobs),
        "jobs": [
            {
                "job_id": job["job_id"],
                "status": job["status"],
                "query": job["query"][:100],  # First 100 chars
                "created_at": job["created_at"]
            }
            for job in sorted_jobs
        ]
    }


@app.get("/health-detailed")
async def health_detailed() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "operational",
        "message": "VouchAI v1 - 4-Agent Research Platform (Background Jobs)",
        "agents": ["Scout", "Adjudicator", "Synthesizer", "Professor"],
        "features": {
            "web_search": "Tavily API",
            "llm": "Google Gemini 2.0 Flash",
            "quality_scoring": "1-10 scale",
            "hallucination_detection": True,
            "eval_logging": "JSONL",
            "background_jobs": True,
            "no_timeout": True
        },
        "endpoints": {
            "POST /research/submit": "Submit research job (returns immediately)",
            "GET /research/status/{job_id}": "Check job status (poll this)",
            "GET /research/jobs": "List all jobs"
        },
        "usage": {
            "1": "POST /research/submit with {query: 'your question'}",
            "2": "Get job_id from response",
            "3": "Poll GET /research/status/{job_id} every 5 seconds",
            "4": "When status='completed', data will contain results"
        }
    }


@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get statistics from logged evaluations"""
    if not LOG_FILE.exists():
        return {
            "total_queries": 0,
            "average_score": 0,
            "message": "No logs available yet"
        }

    scores = []
    total = 0

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                total += 1
                if "professor_score" in entry:
                    scores.append(entry["professor_score"])
            except json.JSONDecodeError:
                continue

    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "total_queries": total,
        "successful_queries": len(scores),
        "average_score": round(avg_score, 2),
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "active_jobs": len([j for j in jobs_db.values() if j["status"] in [JobStatus.QUEUED, JobStatus.PROCESSING]])
    }


if __name__ == "__main__":
    uvicorn.run(
        "main_jobs:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
