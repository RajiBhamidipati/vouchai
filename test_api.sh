#!/bin/bash

# VouchAI API Test Script
# Tests both SSE and Jobs endpoints

echo "🧪 VouchAI API Test Script"
echo "=========================="
echo ""

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TEST_QUERY="What is quantum computing?"

echo "Testing API at: $API_URL"
echo "Query: $TEST_QUERY"
echo ""

# Test 1: Health Check
echo "📋 Test 1: Health Check"
echo "GET $API_URL/"
curl -s "$API_URL/" | jq '.'
echo ""
echo ""

# Test 2: Detailed Health Check
echo "📋 Test 2: Detailed Health Check"
echo "GET $API_URL/health-detailed"
curl -s "$API_URL/health-detailed" | jq '.'
echo ""
echo ""

# Test 3: SSE Streaming (if main_streaming.py is running)
echo "📋 Test 3: SSE Streaming Endpoint"
echo "POST $API_URL/research/stream"
echo "This will show real-time progress..."
echo ""
curl -N -X POST "$API_URL/research/stream" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$TEST_QUERY\"}" 2>&1 | head -n 20
echo ""
echo "... (truncated for brevity)"
echo ""
echo ""

# Test 4: Background Jobs (if main_jobs.py is running)
echo "📋 Test 4: Background Jobs Workflow"
echo "POST $API_URL/research/submit"

JOB_RESPONSE=$(curl -s -X POST "$API_URL/research/submit" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$TEST_QUERY\"}")

echo "$JOB_RESPONSE" | jq '.'

# Extract job ID if available
if command -v jq &> /dev/null; then
  JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id // empty')

  if [ ! -z "$JOB_ID" ]; then
    echo ""
    echo "✅ Job submitted: $JOB_ID"
    echo ""
    echo "Polling status every 5 seconds..."

    # Poll up to 30 times (2.5 minutes)
    for i in {1..30}; do
      echo "Poll #$i - GET $API_URL/research/status/$JOB_ID"

      STATUS_RESPONSE=$(curl -s "$API_URL/research/status/$JOB_ID")
      STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
      PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0')
      MESSAGE=$(echo "$STATUS_RESPONSE" | jq -r '.message')

      echo "Status: $STATUS | Progress: $PROGRESS% | $MESSAGE"

      # Check if completed or failed
      if [ "$STATUS" == "completed" ] || [ "$STATUS" == "failed" ]; then
        echo ""
        echo "Final response:"
        echo "$STATUS_RESPONSE" | jq '.'
        break
      fi

      sleep 5
    done
  else
    echo "⚠️ Jobs endpoint not available (might be using streaming version)"
  fi
else
  echo "⚠️ jq not installed - install with: brew install jq"
fi

echo ""
echo ""

# Test 5: Stats
echo "📋 Test 5: Statistics"
echo "GET $API_URL/stats"
curl -s "$API_URL/stats" | jq '.'
echo ""
echo ""

echo "✅ Tests complete!"
echo ""
echo "💡 Tips:"
echo "  - Test SSE: curl -N -X POST $API_URL/research/stream -H 'Content-Type: application/json' -d '{\"query\": \"test\"}'"
echo "  - Test Jobs: Check WORKFLOW_GUIDE.md for full workflow"
echo "  - View logs: Check server terminal for detailed logs"
echo "  - Frontend examples: See frontend_examples.md"
