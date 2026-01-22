# VouchAI Workflow Solutions - Avoiding Timeouts

## The Problem

Your VouchAI app uses 4 sequential agents (Scout → Adjudicator → Synthesizer → Professor) that:
- Take 90-120 seconds to complete full research
- Make multiple Tavily API calls (slow)
- Use Gemini for analysis (takes time)

**Result:** HTTP requests timeout on most platforms (Railway, Vercel, Heroku = 30-60s limits)

---

## Solutions Overview

### ⭐ **Solution 1: Server-Sent Events (SSE) - RECOMMENDED**
**Files:** `main_streaming.py` + `analyst_team_streaming.py`

**How it works:**
- User submits query
- Server streams progress updates as each agent completes
- Connection stays alive, no timeout
- User sees real-time progress (🔍 Scout working... ✅ Complete!)

**Pros:**
- Best UX - users see immediate feedback
- No polling needed
- Works on all platforms
- Reduces perceived wait time

**Cons:**
- Slightly more complex frontend integration

**Use when:**
- Building user-facing web app
- Want professional polish
- Need to show progress

**Frontend code:**
```javascript
const response = await fetch('/research/stream', {
  method: 'POST',
  body: JSON.stringify({ query })
});

const reader = response.body.getReader();
// Read stream and update UI progressively
```

---

### ✅ **Solution 2: Background Jobs + Polling**
**File:** `main_jobs.py`

**How it works:**
1. POST `/research/submit` → Get `job_id` (returns immediately)
2. Poll GET `/research/status/{job_id}` every 5 seconds
3. When `status: "completed"` → Get results

**Pros:**
- Simple to implement
- Works everywhere
- Easy to scale with Redis/Celery
- Can build queue dashboard

**Cons:**
- Requires polling (frontend complexity)
- Slight delay in getting results
- Uses more HTTP requests

**Use when:**
- Need simplest backend solution
- Building API for mobile apps
- Want job history tracking

**Frontend code:**
```javascript
// Submit job
const { job_id } = await fetch('/research/submit', {
  method: 'POST',
  body: JSON.stringify({ query })
}).then(r => r.json());

// Poll every 5 seconds
const interval = setInterval(async () => {
  const status = await fetch(`/research/status/${job_id}`).then(r => r.json());
  if (status.status === 'completed') {
    clearInterval(interval);
    // Show results
  }
}, 5000);
```

---

### 🚀 **Solution 3: WebSockets (Not Implemented)**

**How it works:**
- Establish WebSocket connection
- Send query over WS
- Receive real-time updates
- Bidirectional communication

**Pros:**
- True real-time, bidirectional
- Can send updates from server anytime
- Best for chat-like interfaces

**Cons:**
- Most complex implementation
- Requires WS support on hosting
- Harder to scale behind load balancers

**Use when:**
- Building chat interface
- Need bidirectional communication
- Have WebSocket infrastructure

---

## Quick Decision Tree

```
Are you building a web app for end users?
├─ Yes → Use SSE Streaming (Solution 1) ⭐
│         Best UX, shows progress, professional
│
└─ No → Is this an API for other apps/mobile?
          ├─ Yes → Use Background Jobs (Solution 2)
          │         Simple, reliable, easy to integrate
          │
          └─ No → Building chat/real-time interface?
                    └─ Yes → Consider WebSockets (Solution 3)
```

---

## Implementation Steps

### For SSE Streaming (Recommended)

1. **Replace main.py**
   ```bash
   mv main.py main_original.py
   mv main_streaming.py main.py
   mv analyst_team_streaming.py analyst_team.py
   ```

2. **Test locally**
   ```bash
   uv run python main.py
   ```

3. **Test endpoint**
   ```bash
   curl -N -X POST http://localhost:8000/research/stream \
     -H "Content-Type: application/json" \
     -d '{"query": "What is quantum computing?"}'
   ```

4. **Update frontend** (see `frontend_examples.md`)

5. **Deploy to Railway/Render**

---

### For Background Jobs

1. **Use main_jobs.py**
   ```bash
   mv main.py main_original.py
   mv main_jobs.py main.py
   ```

2. **Optional: Add Redis for production**
   ```python
   # Replace in-memory dict with Redis
   import redis
   jobs_db = redis.Redis(host='localhost', port=6379, decode_responses=True)
   ```

3. **Test locally**
   ```bash
   uv run python main.py
   ```

4. **Test workflow**
   ```bash
   # Submit
   JOB_ID=$(curl -X POST http://localhost:8000/research/submit \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}' | jq -r '.job_id')

   # Check status
   curl http://localhost:8000/research/status/$JOB_ID
   ```

5. **Update frontend** (see `frontend_examples.md`)

---

## Platform-Specific Configs

### Railway (SSE or Jobs)
```yaml
# railway.json
{
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300
  }
}
```

### Render (SSE or Jobs)
```yaml
# render.yaml
services:
  - type: web
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /
```

### Vercel (Jobs only - SSE has issues)
```json
{
  "builds": [
    { "src": "main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "main.py" }
  ]
}
```

---

## Providing User Value During Wait

### 1. Show Progress (SSE)
```
🔍 Scout: Searching for primary sources...
✅ Scout: Sources gathered
⚖️ Adjudicator: Categorizing facts vs opinions...
✅ Adjudicator: Claims categorized
📝 Synthesizer: Creating report...
✅ Synthesizer: Report generated
🎓 Professor: Auditing quality...
✅ Professor: Quality score 8/10
```

### 2. Show Intermediate Results
Return partial results as agents complete:
- After Scout → Show sources found (10-15s)
- After Adjudicator → Show facts table (30-40s)
- After Synthesizer → Show summary (60-70s)
- After Professor → Show final score (90s)

### 3. Set Expectations
```javascript
// Before starting
"This research will take about 90 seconds. We're running 4 specialized
agents to ensure quality: Scout, Adjudicator, Synthesizer, and Professor."

// Show progress bar
Progress: [████████░░░░░░] 60% - Synthesizer working...
```

### 4. Educational Loading States
```
Did you know? VouchAI uses 4 specialized agents:
- Scout finds primary sources
- Adjudicator separates facts from opinions
- Synthesizer creates structured reports
- Professor audits quality (scores 1-10)
```

---

## Testing Checklist

- [ ] Submit research query
- [ ] See progress updates within 5 seconds
- [ ] Query completes without timeout (even 120s+)
- [ ] Results properly formatted
- [ ] Error handling works
- [ ] Multiple concurrent queries work
- [ ] Mobile browser compatible
- [ ] Works behind load balancer/CDN

---

## Production Recommendations

### For SSE Streaming:
1. **Add nginx config** to prevent buffering:
   ```nginx
   proxy_buffering off;
   proxy_cache off;
   proxy_set_header Connection '';
   proxy_http_version 1.1;
   chunked_transfer_encoding off;
   ```

2. **Set CORS headers** properly for streaming
3. **Add reconnection logic** in frontend
4. **Monitor connection timeouts** (some proxies kill after 60s)

### For Background Jobs:
1. **Use Redis** instead of in-memory dict:
   ```bash
   # Railway
   railway add redis

   # Render
   # Add Redis service in dashboard
   ```

2. **Add job cleanup** (delete old jobs after 24h)
3. **Add rate limiting** (max 5 concurrent jobs per user)
4. **Add job expiration** (auto-fail after 10 minutes)

---

## Migration Path

**Current:** `main.py` (times out after 60s)

**Phase 1:** Switch to SSE Streaming
- Swap files, test locally
- Deploy to staging
- Update frontend to use `/research/stream`
- Test thoroughly
- Deploy to production

**Phase 2:** Optimize (optional)
- Add caching layer for repeated queries
- Parallelize independent agent tasks
- Reduce Tavily search depth for faster results
- Add "quick mode" vs "thorough mode"

---

## FAQ

**Q: Which solution is fastest?**
A: Neither - both solutions take the same time to complete research. SSE just provides better UX by showing progress.

**Q: Can I run agents in parallel?**
A: Not easily - they depend on each other's output (Scout → Adjudicator → Synthesizer → Professor)

**Q: Will this work on Vercel?**
A: Jobs - yes. SSE - limited (Vercel has issues with streaming responses)

**Q: Do I need a database?**
A: For SSE - no. For Jobs - in-memory is fine for low traffic, use Redis for production.

**Q: How do I handle errors?**
A: Both solutions catch errors and return error events/responses. Monitor logs for debugging.

---

## Next Steps

1. **Choose solution:** SSE Streaming (recommended) or Background Jobs
2. **Review:** `frontend_examples.md` for integration code
3. **Test locally:** Run new main.py and test endpoints
4. **Update frontend:** Implement streaming or polling
5. **Deploy:** Push to Railway/Render
6. **Monitor:** Check logs for errors, timeouts

---

**Recommendation for vouchai.app:**

Use **SSE Streaming** (`main_streaming.py`). Deploy to Railway. Update frontend to show animated progress with agent emojis. This provides the best user experience and showcases your multi-agent architecture beautifully.

Users will appreciate seeing the research happen in real-time vs. staring at a loading spinner for 90 seconds!
