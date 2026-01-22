# VouchAI 🔍

**A Production-Ready Multi-Agent Research Platform with Built-in Guardrails and Evaluations**

VouchAI is an AI-powered research system that goes beyond simple prompting. It uses a coordinated team of 4 specialized agents with structured workflows, quality scoring, and comprehensive evaluation logging.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![Agno](https://img.shields.io/badge/Agno-2.4+-purple.svg)](https://github.com/agno-agi/agno)

---

## 🎯 What Makes This Production-Ready?

### 1. **Multi-Agent Specialization**
Not a single prompt - a coordinated team of 4 specialized agents:
- **Scout** 🔍: Primary source gathering using Tavily search
- **Adjudicator** ⚖️: Fact vs Opinion categorization with confidence scoring
- **Synthesizer** 📝: Structured report generation with citations
- **Professor** 🎓: Quality audit and hallucination detection (1-10 grading)

### 2. **Built-in Guardrails**
- **Quality Scoring**: Every research output gets audited and scored 1-10
- **Hallucination Detection**: Professor agent checks for unsupported claims
- **Source Validation**: All claims must be backed by sources
- **Structured Output**: Pydantic schemas enforce data integrity
- **Confidence Levels**: Facts labeled as High/Medium/Low confidence

### 3. **Production Evals & Logging**
- **Automatic Evaluation Logging**: Every query logged to `universal_research_evals.jsonl`
- **Quality Metrics**: Track professor scores, feedback, and recommendations
- **Error Handling**: Graceful degradation with detailed error logs
- **Statistics API**: Monitor average scores, success rates, trends

### 4. **Enterprise-Ready Architecture**
- **FastAPI Backend**: Type-safe, async REST API with OpenAPI docs
- **CORS Enabled**: Ready for frontend integration
- **Environment Config**: Proper secrets management with `.env`
- **Structured Schemas**: Full type safety with Pydantic models
- **Lazy Initialization**: Efficient resource management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              FastAPI Server                 │
│         (main.py + CORS enabled)           │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────▼─────────────┐
    │    run_research(query)    │
    └─────────────┬─────────────┘
                  │
    ┌─────────────▼─────────────┐
    │      Analyst Team         │
    │   (Agno Multi-Agent)      │
    └─────────────┬─────────────┘
                  │
    ┌─────────────▼─────────────┐
    │   1. Scout → Tavily API   │ 🔍 Searches primary sources
    ├───────────────────────────┤
    │   2. Adjudicator          │ ⚖️ Categorizes facts/opinions
    ├───────────────────────────┤
    │   3. Synthesizer          │ 📝 Generates report
    ├───────────────────────────┤
    │   4. Professor            │ 🎓 Quality audit (1-10)
    └─────────────┬─────────────┘
                  │
    ┌─────────────▼─────────────┐
    │   Structured Output       │
    │   + Eval Logging          │
    │   (ResearchOutput schema) │
    └───────────────────────────┘
```

---

## 📊 Data Flow & Schemas

### ResearchOutput Schema
```python
{
  "summary": str,                    # Executive summary (2-3 paragraphs)
  "facts_table": [                   # Verified facts with sources
    {
      "claim": str,
      "sources": [str],
      "confidence": "High|Medium|Low"
    }
  ],
  "opinions_table": [                # Subjective claims
    {
      "claim": str,
      "sources": [str],
      "perspective": str
    }
  ],
  "conflicting_data": [              # Contradictions found
    {
      "topic": str,
      "conflicting_claims": [str],
      "sources": [str]
    }
  ],
  "citations_list": [str],           # All sources used
  "professor_eval_score": {          # Quality audit
    "score": int (1-10),
    "feedback": str,
    "hallucination_check": str,
    "recommendations": [str]
  }
}
```

### Evaluation Logs (JSONL)
Every query automatically logs:
```json
{
  "timestamp": "2026-01-22T15:29:09.388608",
  "query": "What is quantum computing?",
  "professor_score": 8,
  "professor_feedback": "Strong analysis with credible sources...",
  "hallucination_check": "No hallucinations detected",
  "recommendations": ["Add more recent papers", "Include industry applications", "Compare quantum vs classical"]
}
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Google Gemini API key
- Tavily API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/truth-engine.git
cd truth-engine
```

2. **Set up environment**
```bash
# Install dependencies with uv
uv sync

# Create .env file
cp .env.example .env
# Edit .env and add your API keys:
# GOOGLE_API_KEY=your_gemini_key
# TAVILY_API_KEY=your_tavily_key
```

3. **Run the server**
```bash
uv run python main.py
```

Server runs at: `http://localhost:8000`

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 📡 API Endpoints

### POST /research
Submit a research query and get structured analysis.

**Request:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": "Quantum computing is...",
    "facts_table": [...],
    "opinions_table": [...],
    "conflicting_data": [...],
    "citations_list": [...],
    "professor_eval_score": {
      "score": 8,
      "feedback": "...",
      "hallucination_check": "...",
      "recommendations": [...]
    }
  },
  "error": null
}
```

### GET /stats
View aggregated evaluation metrics.

**Response:**
```json
{
  "total_queries": 42,
  "successful_queries": 40,
  "average_score": 7.8,
  "highest_score": 10,
  "lowest_score": 5
}
```

---

## 🎨 Frontend Integration

A beautiful React + TypeScript frontend is available using [Lovable.dev](https://lovable.dev).

See [LOVABLE_INSTRUCTIONS.md](LOVABLE_INSTRUCTIONS.md) for complete frontend setup.

**Frontend Features:**
- 🎯 Animated 4-agent pipeline visualization
- 📊 Interactive facts/opinions tables
- 🎓 Professor quality score badges (color-coded)
- 📱 Fully responsive design
- 🌙 Dark mode support
- 📥 Export to PDF/JSON
- 📈 Statistics dashboard

---

## 🔐 Security & Best Practices

### Environment Variables
- ✅ API keys stored in `.env` (gitignored)
- ✅ Proper secret management with `python-dotenv`
- ✅ CORS configured for production (update origins in production)

### Error Handling
- ✅ Graceful degradation on API failures
- ✅ Detailed error logging
- ✅ User-friendly error messages
- ✅ Timeout handling (90s default)

### Code Quality
- ✅ Type hints throughout (Pydantic schemas)
- ✅ Async/await for non-blocking operations
- ✅ Lazy initialization for efficient resource use
- ✅ Structured logging for debugging

---

## 📈 Monitoring & Evaluation

### View Evaluation Logs
```bash
# Real-time log viewing
tail -f universal_research_evals.jsonl

# Pretty print latest entry
tail -n 1 universal_research_evals.jsonl | jq
```

### Quality Metrics
```bash
# Get statistics via API
curl http://localhost:8000/stats | jq
```

### Analyze Score Distribution
```python
import json

scores = []
with open('universal_research_evals.jsonl', 'r') as f:
    for line in f:
        entry = json.loads(line)
        if 'professor_score' in entry:
            scores.append(entry['professor_score'])

print(f"Average: {sum(scores)/len(scores):.2f}")
print(f"Distribution: {dict(Counter(scores))}")
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | High-performance async API |
| **Agent Framework** | Agno 2.4+ | Multi-agent orchestration |
| **LLM** | Google Gemini 2.0 | Reasoning & generation |
| **Search** | Tavily API | Web search & source gathering |
| **Validation** | Pydantic | Schema enforcement & type safety |
| **Package Manager** | uv | Fast dependency management |

---

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/

# Test research with timeout
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the benefits of solar energy?"}' \
  --max-time 90

# Check stats
curl http://localhost:8000/stats
```

### Example Queries
- "What is the current state of quantum computing?"
- "What are the health benefits and risks of intermittent fasting?"
- "How does climate change affect biodiversity?"
- "What is the status of renewable energy adoption globally?"

---

## 📁 Project Structure

```
truth-engine/
├── main.py                      # FastAPI server + endpoints
├── analyst_team.py              # 4-agent system definition
├── pyproject.toml              # Dependencies (uv)
├── .env                        # API keys (gitignored)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── LOVABLE_INSTRUCTIONS.md     # Frontend generation guide
├── FRONTEND_SETUP.md           # Frontend integration docs
└── universal_research_evals.jsonl  # Auto-generated eval logs
```

---

## 🎯 Key Differentiators

### Not Just Prompting - This is Production AI

| Vibe Coding ❌ | Production System ✅ |
|---------------|---------------------|
| Single prompt | 4 specialized agents |
| No validation | Built-in quality scoring (1-10) |
| No tracking | Comprehensive eval logging |
| No structure | Pydantic schemas + type safety |
| Hope it works | Hallucination detection |
| Unauditable | Every decision logged & scored |

### Guardrails in Action
1. **Input Validation**: Pydantic schemas reject malformed requests
2. **Source Requirements**: Claims must include sources
3. **Confidence Scoring**: Facts labeled with confidence levels
4. **Quality Audit**: Professor agent grades every output
5. **Hallucination Check**: Verifies claims against sources
6. **Structured Output**: No free-form text, enforced schemas

---

## 🚧 Roadmap

- [ ] Add unit tests with pytest
- [ ] Implement RAG with vector database for source verification
- [ ] Add streaming responses for real-time progress
- [ ] Implement caching layer (Redis) for repeated queries
- [ ] Add authentication & rate limiting
- [ ] Multi-language support
- [ ] PDF ingestion for private document research
- [ ] Fine-tuned evaluation model for Professor agent
- [ ] A/B testing framework for agent instructions
- [ ] Prometheus metrics export

---

## 🤝 Contributing

Contributions welcome! This project demonstrates production-ready agentic AI with proper guardrails and evaluation systems.

**Areas for contribution:**
- Additional agent types (e.g., Medical Specialist, Legal Analyst)
- Enhanced evaluation metrics
- Integration tests
- Performance optimizations
- Documentation improvements

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- [Agno](https://github.com/agno-agi/agno) - Multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Tavily](https://tavily.com/) - AI-powered search API
- [Google Gemini](https://ai.google.dev/) - Advanced LLM

---

## 📞 Contact

Built by [@yourusername](https://github.com/yourusername)

**This is not just another LLM wrapper** - it's a production-ready research platform with specialized agents, quality guardrails, and comprehensive evaluation tracking. Perfect for demonstrating enterprise-grade agentic AI architecture.

---

**⭐ If you found this useful, please star the repo!**

*Showing that we can build real, auditable, production-ready AI systems with proper evals - not just vibe coding.*
