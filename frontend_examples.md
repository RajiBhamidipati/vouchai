# Frontend Integration Examples for VouchAI

This guide shows how to integrate VouchAI's different backend solutions into your frontend.

---

## Option 1: Server-Sent Events (SSE) - RECOMMENDED ⭐

**Best for:** Real-time progress updates, best UX
**Backend:** `main_streaming.py`

### React Example with SSE

```tsx
import { useState } from 'react';

interface AgentProgress {
  status: string;
  agent: string;
  message: string;
  progress: number;
}

export function ResearchSSE() {
  const [query, setQuery] = useState('');
  const [progress, setProgress] = useState<AgentProgress[]>([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const startResearch = async () => {
    setIsLoading(true);
    setProgress([]);
    setResult(null);

    try {
      const response = await fetch('https://api.vouchai.app/research/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        // Decode the chunk
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            // Update progress
            setProgress(prev => [...prev, data]);

            // Check if completed
            if (data.status === 'completed') {
              setResult(data.data);
              setIsLoading(false);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">VouchAI Research</h1>

      {/* Input */}
      <div className="mb-6">
        <textarea
          className="w-full p-4 border rounded-lg"
          rows={3}
          placeholder="What do you want to research?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="mt-3 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          onClick={startResearch}
          disabled={isLoading || !query}
        >
          {isLoading ? 'Researching...' : 'Start Research'}
        </button>
      </div>

      {/* Progress Display */}
      {progress.length > 0 && (
        <div className="mb-6 space-y-2">
          <h2 className="text-xl font-semibold">Progress</h2>
          <div className="bg-gray-100 rounded-lg p-4 space-y-2">
            {progress.map((item, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <span className="font-mono text-sm">{item.agent}</span>
                <span className="text-gray-600">{item.message}</span>
                {item.progress && (
                  <span className="ml-auto text-sm text-gray-500">
                    {item.progress}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="border rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Research Results</h2>

          {/* Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Summary</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.summary}</p>
          </div>

          {/* Professor Score */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Quality Score</h3>
            <div className="text-3xl font-bold text-blue-600">
              {result.professor_eval_score.score}/10
            </div>
            <p className="text-gray-700 mt-2">{result.professor_eval_score.feedback}</p>
          </div>

          {/* Facts Table */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Facts</h3>
            <div className="space-y-3">
              {result.facts_table.map((fact, idx) => (
                <div key={idx} className="border-l-4 border-green-500 pl-4 py-2">
                  <p className="font-medium">{fact.claim}</p>
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="font-semibold">Confidence:</span> {fact.confidence}
                  </div>
                  <div className="text-sm text-blue-600 mt-1">
                    {fact.sources.map((src, i) => (
                      <a key={i} href={src} target="_blank" rel="noopener" className="block">
                        {src}
                      </a>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Opinions Table */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Opinions</h3>
            <div className="space-y-3">
              {result.opinions_table.map((opinion, idx) => (
                <div key={idx} className="border-l-4 border-yellow-500 pl-4 py-2">
                  <p className="font-medium">{opinion.claim}</p>
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="font-semibold">Perspective:</span> {opinion.perspective}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Citations */}
          <div>
            <h3 className="text-lg font-semibold mb-2">Citations</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-600">
              {result.citations_list.map((citation, idx) => (
                <li key={idx}>
                  <a href={citation} target="_blank" rel="noopener">
                    {citation}
                  </a>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Option 2: Background Jobs with Polling

**Best for:** Simple implementation, works everywhere
**Backend:** `main_jobs.py`

### React Example with Polling

```tsx
import { useState, useEffect } from 'react';

interface JobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  data: any;
  error: string | null;
}

export function ResearchJobs() {
  const [query, setQuery] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Submit research job
  const submitJob = async () => {
    try {
      const response = await fetch('https://api.vouchai.app/research/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const result = await response.json();
      setJobId(result.job_id);
      setIsPolling(true);
    } catch (error) {
      console.error('Error submitting job:', error);
    }
  };

  // Poll for job status
  useEffect(() => {
    if (!jobId || !isPolling) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(
          `https://api.vouchai.app/research/status/${jobId}`
        );
        const data = await response.json();
        setStatus(data);

        // Stop polling when done
        if (data.status === 'completed' || data.status === 'failed') {
          setIsPolling(false);
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [jobId, isPolling]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">VouchAI Research (Jobs)</h1>

      {/* Input */}
      <div className="mb-6">
        <textarea
          className="w-full p-4 border rounded-lg"
          rows={3}
          placeholder="What do you want to research?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="mt-3 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          onClick={submitJob}
          disabled={isPolling || !query}
        >
          {isPolling ? 'Processing...' : 'Start Research'}
        </button>
      </div>

      {/* Job Status */}
      {status && (
        <div className="mb-6 p-4 bg-gray-100 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">Status: {status.status}</span>
            {status.progress !== null && (
              <span className="text-sm text-gray-600">{status.progress}%</span>
            )}
          </div>
          <div className="w-full bg-gray-300 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${status.progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">{status.message}</p>
        </div>
      )}

      {/* Results */}
      {status?.status === 'completed' && status.data && (
        <div className="border rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Research Results</h2>
          {/* Same results display as SSE example */}
          <pre className="bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(status.data, null, 2)}
          </pre>
        </div>
      )}

      {/* Error */}
      {status?.status === 'failed' && (
        <div className="border border-red-300 bg-red-50 rounded-lg p-4">
          <h3 className="text-red-700 font-semibold">Error</h3>
          <p className="text-red-600">{status.error}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Option 3: Vanilla JavaScript (No Framework)

### SSE with Vanilla JS

```html
<!DOCTYPE html>
<html>
<head>
  <title>VouchAI Research</title>
  <style>
    body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; }
    textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
    button { margin-top: 12px; padding: 12px 24px; background: #2563eb; color: white;
             border: none; border-radius: 8px; cursor: pointer; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .progress { margin: 20px 0; padding: 16px; background: #f3f4f6; border-radius: 8px; }
    .progress-item { margin: 8px 0; }
  </style>
</head>
<body>
  <h1>VouchAI Research</h1>

  <textarea id="query" rows="3" placeholder="What do you want to research?"></textarea>
  <button id="submit">Start Research</button>

  <div id="progress" class="progress" style="display: none;"></div>
  <div id="results"></div>

  <script>
    const queryInput = document.getElementById('query');
    const submitBtn = document.getElementById('submit');
    const progressDiv = document.getElementById('progress');
    const resultsDiv = document.getElementById('results');

    submitBtn.addEventListener('click', async () => {
      const query = queryInput.value.trim();
      if (!query) return;

      submitBtn.disabled = true;
      progressDiv.style.display = 'block';
      progressDiv.innerHTML = '';
      resultsDiv.innerHTML = '';

      try {
        const response = await fetch('https://api.vouchai.app/research/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6));

              // Update progress
              const progressItem = document.createElement('div');
              progressItem.className = 'progress-item';
              progressItem.textContent = `${data.agent}: ${data.message}`;
              progressDiv.appendChild(progressItem);

              // Check if completed
              if (data.status === 'completed') {
                displayResults(data.data);
                submitBtn.disabled = false;
              }
            }
          }
        }
      } catch (error) {
        console.error('Error:', error);
        submitBtn.disabled = false;
      }
    });

    function displayResults(data) {
      resultsDiv.innerHTML = `
        <h2>Results</h2>
        <h3>Quality Score: ${data.professor_eval_score.score}/10</h3>
        <p><strong>Summary:</strong> ${data.summary}</p>
        <h3>Facts (${data.facts_table.length})</h3>
        <ul>
          ${data.facts_table.map(f => `<li>${f.claim} (${f.confidence})</li>`).join('')}
        </ul>
      `;
    }
  </script>
</body>
</html>
```

---

## Deployment Configuration

### Railway.app (with SSE)

**railway.json**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main_streaming:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300
  }
}
```

### Render.com (with Jobs)

**render.yaml**
```yaml
services:
  - type: web
    name: vouchai-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main_jobs:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
```

---

## Comparison

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **SSE Streaming** | Real-time updates, great UX, no polling overhead | Slightly more complex frontend | User-facing apps |
| **Background Jobs** | Simple, works everywhere, easy to scale | Requires polling, slight delay | APIs, mobile apps |
| **WebSockets** | Bidirectional, real-time | Most complex, needs WS support | Chat-like interfaces |

---

## Testing

### Test SSE Endpoint
```bash
curl -N -X POST https://api.vouchai.app/research/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}'
```

### Test Jobs Endpoint
```bash
# Submit job
JOB_ID=$(curl -X POST https://api.vouchai.app/research/submit \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}' | jq -r '.job_id')

# Check status
curl https://api.vouchai.app/research/status/$JOB_ID
```

---

## Recommendation

**For VouchAI (vouchai.app):** Use **SSE Streaming** (`main_streaming.py`)

**Why:**
1. Best user experience - see progress in real-time
2. No timeout issues on any platform
3. Reduces perceived wait time
4. Shows value immediately (users see agents working)
5. Professional polish

Deploy with Railway or Render, both support SSE natively.
