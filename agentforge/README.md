# AgentForge - Healthcare AI Agent System

Production-ready healthcare AI agent powered by LangChain + Gemini Pro, integrating with OpenEMR via REST/FHIR APIs.

## Features

- **Drug Interaction Checking** - Real-time lookups via NIH RxNorm/RxNav API
- **Symptom Analysis** - Evidence-based condition mapping with emergency escalation
- **Provider Search** - Find healthcare providers via OpenEMR FHIR API
- **Verification Layer** - Source attribution, confidence scoring, medical disclaimers
- **Conversation Memory** - Multi-turn context across sessions
- **LangSmith Observability** - Full trace logging and eval framework

## Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Setup

```bash
cd agentforge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run

```bash
# Start FastAPI backend
uvicorn app.main:app --reload --port 8000

# In another terminal, start Streamlit UI
streamlit run ui/streamlit_app.py
```

### Run Evals

```bash
python -m evals.runner
python -m evals.runner --category drug_interaction --verbose
```

## Architecture

```
[Streamlit UI] --> [FastAPI Backend] --> [LangChain ReAct Agent]
                                              |
                                    +----+----+----+
                                    |    |         |
                              Drug  | Symptom | Provider
                           Interact | Lookup  | Search
                            (RxNav) | (Local) | (OpenEMR)
                                    |         |
                              [Verification Layer]
                              [LangSmith Tracing]
```

## API

- `POST /api/chat` - Send a healthcare query
- `POST /api/clear-session` - Clear conversation history
- `GET /health` - Health check

## OpenEMR Integration

AgentForge connects to OpenEMR via its REST/FHIR APIs:
- Docker dev environment: `docker/development-easy/` at `localhost:8300`
- OAuth2 authentication for API access
- Falls back to mock data when OpenEMR is unavailable

## License

MIT
