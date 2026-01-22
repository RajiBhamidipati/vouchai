"""
VouchAI v1 - Universal Multi-Agent Research Platform
FastAPI server providing REST API for research queries with comprehensive evaluation logging
Domain: vouchai.app
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from analyst_team import run_research, ResearchOutput


# Load environment variables
load_dotenv()

# Verify API keys are present
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in environment variables")


# Initialize FastAPI app
app = FastAPI(
    title="VouchAI API v1",
    description="Production-ready multi-agent research platform with guardrails and evaluations",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vouchai.app",
        "https://www.vouchai.app",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "*"  # Allow all for initial deployment - restrict later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class ResearchRequest(BaseModel):
    query: str


# Response model wrapper
class ResearchResponse(BaseModel):
    success: bool
    data: ResearchOutput | None = None
    error: str | None = None


# Logging file path
LOG_FILE = Path("universal_research_evals.jsonl")


def log_research_evaluation(query: str, output: ResearchOutput) -> None:
    """
    Log research query and Professor's evaluation to JSONL file

    Args:
        query: The research query
        output: The research output containing evaluation
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "professor_score": output.professor_eval_score.score,
        "professor_feedback": output.professor_eval_score.feedback,
        "hallucination_check": output.professor_eval_score.hallucination_check,
        "recommendations": output.professor_eval_score.recommendations
    }

    # Append to JSONL file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint - API health check"""
    return {
        "message": "VouchAI v1 - Research You Can Vouch For",
        "status": "running",
        "version": "1.0.0",
        "domain": "vouchai.app"
    }


@app.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest) -> ResearchResponse:
    """
    Main research endpoint - processes queries through the analyst team

    Args:
        request: ResearchRequest containing the query

    Returns:
        ResearchResponse: Structured research output with evaluation
    """
    try:
        # Validate query
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )

        # Run the research analysis
        result = await run_research(request.query)

        # Log the evaluation
        log_research_evaluation(request.query, result)

        # Return successful response
        return ResearchResponse(
            success=True,
            data=result,
            error=None
        )

    except Exception as e:
        # Log error
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": request.query,
            "error": str(e),
            "status": "failed"
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_log) + "\n")

        # Return error response
        return ResearchResponse(
            success=False,
            data=None,
            error=str(e)
        )


@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """
    Get statistics from logged evaluations

    Returns:
        Statistics including average score, total queries, etc.
    """
    if not LOG_FILE.exists():
        return {
            "total_queries": 0,
            "average_score": 0,
            "message": "No logs available yet"
        }

    # Read and parse JSONL
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
        "lowest_score": min(scores) if scores else 0
    }


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
