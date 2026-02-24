# Weekly Development Log

## AgentForge Healthcare AI Agent System

**Developer:** Joe Panetta (Giuseppe)
**Sprint:** Feb 24 - Mar 2, 2026

---

## Pre-Sprint: Sunday Feb 23 (Discovery Day)

### Activities

- Received project requirements (Gauntlet AI Cohort 4, Week 2)
- Completed Pre-Search Requirements Document
- Performed comprehensive OpenEMR codebase analysis

### OpenEMR Repository Analysis (6 parallel research agents)

| Agent | Focus | Key Findings |
|-------|-------|-------------|
| 1 | Top-level structure | 132 PHP + 19 NPM deps, v8.0.1-dev, GPL v3 |
| 2 | /src/ architecture | 33 modules, 500+ FHIR files, 150+ services |
| 3 | Database schema | 282 MySQL tables, dual migration system |
| 4 | Test suite | 239 test files, 7 categories, 3 PHPUnit configs |
| 5 | API + interface | 10-listener pipeline, OAuth2, 30+ FHIR resources |
| 6 | Docker + CI/CD | 27 GitHub Actions, 5 Docker configs |

### Key Architecture Decisions Made

1. AgentForge will be a **standalone Python app** connecting to OpenEMR via REST/FHIR APIs
2. Will use OpenEMR's OAuth2 for authentication
3. Target APIs: Patient, Medication, Appointment, Practitioner, Coverage FHIR resources
4. Development against Docker dev environment (localhost:8300)

### Blockers

- None

### Tomorrow's Plan

- Initialize Python project structure
- Set up LangChain + Gemini Pro
- Implement first tool (drug_interaction_check)

---

## Day 1: Monday Feb 24

### Planned

- [x] Project initialization (pyproject.toml, FastAPI, Streamlit)
- [x] LangChain + LLM setup (Gemini -> Groq pivot)
- [x] drug_interaction_check tool (RxNorm API)
- [x] symptom_lookup tool (curated medical DB)
- [x] provider_search tool (mock + OpenEMR)
- [x] appointment_availability tool
- [x] insurance_coverage_check tool
- [x] medication_lookup tool (FDA OpenFDA API)
- [x] 4-layer verification system
- [x] Custom observability module (6 PRD requirements)
- [x] LangSmith integration (env var fix)
- [x] Streamlit chat UI with streaming, feedback, welcome screen
- [x] SSE streaming endpoint (`POST /api/chat/stream`)
- [x] Deploy to Render (publicly accessible)
- [x] 68 isolated unit tests (all passing)
- [x] 56 integration eval test cases

### Completed

- **Full MVP exceeded requirements**: 6 tools (vs 3 required), 56 eval cases (vs 5 required), 4-type verification (vs 1 required), 68 unit tests
- **Project structure**: FastAPI backend + Streamlit frontend + LangChain/LangGraph agent
- **6 Healthcare tools**:
  1. `drug_interaction_check` -- RxNorm API + curated 10-pair interaction DB
  2. `symptom_lookup` -- 5 symptom categories, 16 emergency keywords
  3. `provider_search` -- Mock providers across 8 specialties, OpenEMR FHIR fallback
  4. `appointment_availability` -- Mock calendar by specialty
  5. `insurance_coverage_check` -- 3 plans (PPO/HMO/Medicare), 15+ CPT codes each
  6. `medication_lookup` -- FDA OpenFDA API + 6-drug mock fallback
- **Verification system**: 4 layers -- hallucination detection, confidence scoring, domain constraints, output validation
- **Observability (6 requirements)**:
  - Trace logging: `TraceRecord` dataclass, persisted to JSONL
  - Latency tracking: `RequestTracer` times LLM, tool, verification, total
  - Error tracking: Errors captured with category, rates in dashboard
  - Token usage: Input/output/total per request, provider-aware cost ($0 for Groq)
  - Eval results: Historical runs stored in eval_history.jsonl
  - User feedback: Thumbs up/down via trace_id, stored in feedback.jsonl
- **LangSmith integration**: Fixed silent bug -- env vars now exported to `os.environ` at module init
- **Streaming**: `chat_stream()` async generator -> SSE endpoint -> `st.write_stream()`
- **Testing**:
  - 68 unit tests: 30 tools + 22 verifier + 8 observability (all pass, <2s, no API keys)
  - 56 eval test cases: 21 happy path + 12 edge + 12 adversarial + 11 multi-step
- **Deployment**: Live at https://agentforge-0p0k.onrender.com/

### Blockers Hit and Resolved

1. **Gemini Pro quota exhausted** (429 RESOURCE_EXHAUSTED, limit: 0)
   - **Resolution:** Switched to Groq/Llama 3.3 70B (free, no credit card)
   - **Impact:** Added multi-provider LLM support (LLM_PROVIDER env var)

2. **LangSmith not capturing traces** (env vars in Pydantic settings but not in os.environ)
   - **Resolution:** Added module-level env var export in healthcare_agent.py
   - **Root cause:** LangChain SDK reads from `os.environ`, not from Python variables

3. **Insurance tool returned vague results for MRI**
   - **Resolution:** Added MRI, CT scan, blood work CPT codes to all 3 insurance plans

4. **LLM summarizing tool data vaguely**
   - **Resolution:** Updated system prompt with explicit instructions for specific data presentation

### Performance Metrics (Day 1)

| Metric | Target | Actual |
|--------|--------|--------|
| Tools implemented | 3+ | **6** |
| Eval test cases | 5+ | **56** |
| Unit tests | 0 (not required) | **68** |
| Verification types | 1+ | **4** |
| Observability requirements | 6 | **6** |
| Single-tool latency | <5s | **~1-3s** |
| Multi-step latency | <15s | **~3-5s** |
| Cost per query | <$0.05 | **$0.000** |
| Streaming | No | **Yes (SSE)** |

### Observability Data (Day 1)

- **Custom trace module**: `app/observability.py` (287 lines)
  - TraceRecord: 17 fields (trace_id, session_id, timestamp, query, tools_called, response, confidence, latency breakdown, tokens, cost, errors)
  - RequestTracer: Start/end timing for LLM, tool, verification phases
  - Dashboard: Aggregated stats (requests, errors, latency, tokens, tool usage, feedback, eval history)
- **LangSmith project**: `agentforge-healthcare` (tracing enabled after env var fix)
- **Dashboard API**: `GET /api/dashboard` returns real-time aggregated stats
- **Sidebar display**: Request count, error count, avg latency, avg confidence, feedback, estimated cost

### Eval Framework (Day 1)

- **Runner**: `evals/runner.py` -- async, category filtering, JSON export, verbose mode
- **Test cases**: `evals/test_cases.py` -- 56 cases across 4 categories
- **Output**: `evals/eval_results.json` -- detailed per-test results with keyword/tool pass/fail
- **Observability integration**: Results recorded via `record_eval_run()` for historical tracking
- **Commands**:
  - `python -m evals.runner` -- run all 56 tests
  - `python -m evals.runner --category adversarial --verbose` -- run category with details
  - `python -m evals.runner --json` -- load from published JSON dataset

### Notes

- Groq/Llama 3.3 70B is impressively fast and capable for this use case
- Mock data strategy proved essential when Gemini billing failed
- Streamlit + FastAPI dual-process deployment works well on Render single-port setup
- Streaming via SSE provides much better UX than waiting for full response

---

## Day 2: Tuesday Feb 25 (MVP DEADLINE)

### Planned

- [ ] Run full eval suite with valid Groq API key and capture pass rates
- [ ] Polish any failing eval cases (tune prompts, fix tool output)
- [ ] Update documentation with eval results
- [ ] **SUBMIT MVP**

### Completed

- TBD

### MVP Submission Status

- [ ] Submitted: YES/NO
- [ ] Gate: PASS/FAIL

---

## Day 3: Wednesday Feb 26

### Planned

- [ ] LangSmith dashboard review and screenshots
- [ ] Expand eval suite to 80+ cases (add medication_lookup tests)
- [ ] Security hardening (input sanitization)
- [ ] Prompt injection prevention testing

### Completed

- TBD

---

## Day 4: Thursday Feb 27

### Planned

- [ ] Fallback LLM strategy (Groq primary -> Gemini/Claude)
- [ ] Advanced confidence scoring refinement
- [ ] Performance optimization (caching common queries)

### Completed

- TBD

---

## Day 5: Friday Feb 28 (EARLY SUBMISSION)

### Planned

- [ ] Eval suite >80% pass rate confirmed
- [ ] All documentation complete and reviewed
- [ ] **SUBMIT for early feedback**

### Completed

- TBD

---

## Day 6: Saturday Mar 1

### Planned

- [ ] Open source packaging (langchain-healthcare-tools)
- [ ] Eval dataset publication (56+ test cases)
- [ ] Architecture document finalization

### Completed

- TBD

---

## Day 7: Sunday Mar 2 (FINAL DEADLINE 10:59 PM CT)

### Planned

- [ ] Demo video (3-5 min)
- [ ] Finalize all documentation
- [ ] LinkedIn post (tag @GauntletAI)
- [ ] **FINAL SUBMISSION**

### Completed

- TBD

### Final Submission Checklist

- [x] GitHub repo with setup guide (README.md rewritten)
- [ ] Demo video
- [x] Pre-Search document
- [x] Agent Architecture doc (README.md)
- [x] AI Cost Analysis (finalized)
- [x] AI Development Process (finalized)
- [x] Eval dataset (56 cases in test_cases.py)
- [ ] Open source contribution link
- [x] Deployed application (https://agentforge-0p0k.onrender.com/)
- [ ] Social post

---

## Sprint Retrospective (Post-Sprint)

### Velocity

- TBD (end of sprint)

### What Went Well

- TBD (end of sprint)

### What Didn't Go Well

- TBD (end of sprint)

### Key Learnings

- TBD (end of sprint)
