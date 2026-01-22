"""
VouchAI v1 - Streaming Version with Server-Sent Events
Provides real-time progress updates to prevent timeouts
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, AsyncGenerator
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from analyst_team_streaming import run_research_streaming, ResearchOutput


# Load environment variables
load_dotenv()

# Verify API keys
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in environment variables")


# Initialize FastAPI app
app = FastAPI(
    title="VouchAI API v1 - Streaming",
    description="Production-ready multi-agent research platform with real-time streaming",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Log research query and evaluation to JSONL file"""
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


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint - API health check"""
    return {
        "message": "VouchAI v1 - Research You Can Vouch For (Streaming)",
        "status": "running",
        "version": "1.1.0",
        "domain": "vouchai.app",
        "features": {
            "streaming": "Server-Sent Events for real-time progress",
            "no_timeout": "Long-running queries supported"
        }
    }


@app.post("/research/stream")
async def research_stream_endpoint(request: ResearchRequest):
    """
    Streaming research endpoint - provides real-time updates
    Returns Server-Sent Events (SSE) stream
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Validate query
            if not request.query or len(request.query.strip()) == 0:
                yield f"data: {json.dumps({'error': 'Query cannot be empty'})}\n\n"
                return

            # Send initial message
            yield f"data: {json.dumps({'status': 'started', 'message': 'Research started', 'agent': 'system'})}\n\n"

            # Run research with streaming updates
            async for event in run_research_streaming(request.query):
                # Convert Pydantic models to dict for JSON serialization
                serializable_event = event.copy()
                if 'data' in serializable_event and hasattr(serializable_event['data'], 'model_dump'):
                    # Convert ResearchOutput Pydantic model to dict
                    serializable_event['data'] = serializable_event['data'].model_dump()

                # Send progress update
                yield f"data: {json.dumps(serializable_event)}\n\n"

                # If this is the final result
                if event.get('status') == 'completed':
                    result = event.get('data')
                    if result:
                        # Log the evaluation
                        log_research_evaluation(request.query, result)

            # Send completion message
            yield f"data: {json.dumps({'status': 'done'})}\n\n"

        except Exception as e:
            # Send error
            error_event = {
                'status': 'error',
                'message': str(e),
                'agent': 'system'
            }
            yield f"data: {json.dumps(error_event)}\n\n"

            # Log error
            error_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": request.query,
                "error": str(e),
                "status": "failed"
            }
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_log) + "\n")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@app.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest) -> ResearchResponse:
    """
    Traditional endpoint - waits for full completion
    NOTE: May timeout on platforms with <120s limits
    """
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Collect all events until completion
        result = None
        async for event in run_research_streaming(request.query):
            if event.get('status') == 'completed':
                result = event.get('data')
                break

        if result:
            log_research_evaluation(request.query, result)
            return ResearchResponse(success=True, data=result, error=None)
        else:
            raise Exception("Research failed to complete")

    except Exception as e:
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": request.query,
            "error": str(e),
            "status": "failed"
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_log) + "\n")

        return ResearchResponse(success=False, data=None, error=str(e))


@app.get("/health-detailed")
async def health_detailed() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "operational",
        "message": "VouchAI v1 - 3-Agent Research Platform (Streaming)",
        "agents": ["Scout", "Adjudicator", "Professor"],
        "features": {
            "web_search": "Tavily API",
            "llm": "Google Gemini 2.0 Flash",
            "quality_scoring": "1-10 scale",
            "hallucination_detection": True,
            "eval_logging": "JSONL",
            "streaming": "Server-Sent Events",
            "no_timeout": True
        },
        "endpoints": {
            "/research/stream": "SSE streaming (recommended for long queries)",
            "/research": "Traditional (may timeout >60s)"
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
        "lowest_score": min(scores) if scores else 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "main_streaming:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
