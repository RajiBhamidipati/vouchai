#!/bin/bash
# Railway startup script for VouchAI

# Use Railway's PORT environment variable, default to 8000 if not set
PORT=${PORT:-8000}

# Start uvicorn with the dynamic port
uvicorn main:app --host 0.0.0.0 --port $PORT
