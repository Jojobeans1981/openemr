# AgentForge Implementation Plan

## Healthcare AI Agent System - Phased Delivery

**Project:** AgentForge - Production-Ready Healthcare AI Agent
**Developer:** Joe Panetta (Giuseppe)
**Cohort:** Gauntlet AI Cohort 4 - Week 2
**Sprint:** 7 days (Feb 24 - Mar 2, 2026)
**Final Deadline:** Sunday Mar 2, 10:59 PM CT

---

## Architecture Overview

AgentForge is a **standalone Python application** that integrates with OpenEMR via its REST/FHIR APIs.

```text
[Streamlit UI] --> [FastAPI Backend] --> [LangGraph ReAct Agent]
                                              |
                                    +---------+---------+
                                    |    |    |    |    |    |
                                  Drug Symptom Prov  Appt Insur Meds
                                  Inter Lookup Search Avail Cover Lookup
                                  (RxNav)(Local)(Mock)(Mock)(Mock)(FDA)
                                              |
                                    [4-Layer Verification]
                                    [LangSmith + Custom Observability]
```

**LLM Provider:** Groq / Llama 3.3 70B Versatile (free tier)
**Deployment:** Render (free tier) at https://agentforge-0p0k.onrender.com/

### OpenEMR Integration Points (from repo analysis)

- **REST API:** `/apis/default/api/` - patients, encounters, appointments, providers
- **FHIR R4:** `/apis/default/fhir/` - 30+ FHIR resources (Patient, Medication, etc.)
- **OAuth2:** `/oauth2/default/` - authentication for API access
- **Key tables:** patient_data, form_encounter, facility, users, billing
- **Docker dev env:** `docker/development-easy/` - localhost:8300 (admin/pass)

---

## Phase 1: MVP Gate (Day 1 | Mon Feb 24) -- COMPLETED

**Goal: Working agent with 3+ tools, deployed, publicly accessible**
**Result: Exceeded all requirements -- 6 tools, 56 eval cases, 4-type verification, 68 unit tests**

### Hour 0-4: Foundation + First Tool

- [x] Initialize Python project (pyproject.toml, dependencies)
- [x] Set up FastAPI backend skeleton
- [x] Configure LangChain + LLM integration (Groq/Llama 3.3 70B)
- [x] Implement `drug_interaction_check` tool (RxNorm/RxNav API)
- [x] Test: "Check interaction between warfarin and aspirin" -- structured response
- [x] Set up LangSmith tracing (env var export fix applied)

### Hour 4-8: Expand to 6 Tools (exceeded 3-tool target)

- [x] Implement `symptom_lookup` tool (CDC/NIH curated data)
- [x] Implement `provider_search` tool (mock data + OpenEMR FHIR fallback)
- [x] Implement `appointment_availability` tool (mock calendar by specialty)
- [x] Implement `insurance_coverage_check` tool (3 plans, 15+ CPT codes)
- [x] Implement `medication_lookup` tool (FDA OpenFDA API + 6-drug mock fallback)
- [x] All tools work independently with structured output (Pydantic schemas)

### Hour 8-16: Multi-Step Reasoning + Memory

- [x] Implement ReAct agent pattern (LangGraph `create_react_agent`)
- [x] Add conversation history (MemorySaver checkpointing)
- [x] Chain tools: symptom -> provider recommendation flow
- [x] Maintain context across conversation turns

### Hour 16-20: Verification + Error Handling

- [x] Implement 4-layer verification system:
  1. Hallucination Detection -- source attribution, unsupported claim flagging
  2. Confidence Scoring -- multi-factor (base + tools + sources + disclaimer - risk)
  3. Domain Constraints -- 16 emergency patterns, forbidden content, dosage limits
  4. Output Validation -- format, completeness, tool result inclusion
- [x] Emergency escalation (chest pain, overdose, suicidal ideation -> 911)
- [x] Medical disclaimer on all responses
- [x] Graceful failure handling (API timeouts, malformed input)

### Hour 20-24: Eval + Testing + Deploy

- [x] Write 56 test cases across 4 categories (21 happy, 12 edge, 12 adversarial, 11 multi-step)
- [x] Build async eval runner with category filtering and JSON export
- [x] Write 68 isolated unit tests (tools, verifier, observability) -- all pass in <2s
- [x] Deploy to Render (publicly accessible)
- [x] Streamlit UI with streaming, feedback, welcome screen, sidebar dashboard
- [x] **MVP gate: EXCEEDED**

### MVP Checklist (all completed):

- [x] Agent responds to natural language healthcare queries
- [x] 6 functional tools invokable by agent (exceeded 3 requirement)
- [x] Tool calls execute and return structured results
- [x] Agent synthesizes tool results into coherent responses
- [x] Conversation history maintained across turns
- [x] Graceful error handling
- [x] 4 domain-specific verification checks (exceeded 1 requirement)
- [x] 56 test cases with expected outcomes (exceeded 5 requirement)
- [x] 68 unit tests (not required, added for quality)
- [x] Deployed and publicly accessible at https://agentforge-0p0k.onrender.com/

---

## Phase 2: Eval Framework + Observability (Day 2-3 | Tue-Wed Feb 25-26)

**Goal: Full observability, eval reporting, streaming UX**

### Observability (6 PRD requirements)

- [x] Trace Logging -- `TraceRecord` dataclass, persisted to JSONL
- [x] Latency Tracking -- `RequestTracer` times LLM, tool, verification, total
- [x] Error Tracking -- Errors captured with category, rates in dashboard
- [x] Token Usage -- Input/output/total per request, provider-aware cost ($0 for Groq)
- [x] Eval Results -- Historical runs stored in `data/observability/eval_history.jsonl`
- [x] User Feedback -- Thumbs up/down via trace_id, stored in `data/observability/feedback.jsonl`

### LangSmith Integration

- [x] Env vars properly exported to `os.environ` (fixed silent bug)
- [x] Full trace chain: input -> reasoning -> tool calls -> verification -> output
- [x] Latency breakdown per component
- [x] Token usage and cost tracking
- [x] Project: `agentforge-healthcare`

### Streaming Responses

- [x] `chat_stream()` async generator using `agent.astream_events()`
- [x] `POST /api/chat/stream` SSE endpoint (FastAPI StreamingResponse)
- [x] Streamlit `st.write_stream()` with fallback to non-streaming
- [x] Tool status indicators during streaming ("Using tool: drug_interaction_check...")

### Remaining Tools (completed in Phase 1)

- [x] `appointment_availability` tool
- [x] `insurance_coverage_check` tool
- [x] `medication_lookup` tool (FDA OpenFDA API)

### Eval Framework

- [x] 56 test cases across 4 categories
- [x] Automated async runner with pass/fail reporting
- [x] Category breakdown and average latency reporting
- [x] Results saved to `evals/eval_results.json`
- [x] Results recorded in observability system
- [ ] Expand to 80+ test cases
- [ ] Add medication_lookup specific test cases

---

## Phase 3: Polish + Early Submission (Day 4-5 | Thu-Fri Feb 27-28)

**Goal: >80% eval pass rate, polished docs, early feedback**

- [x] 4-layer verification system complete
- [x] Escalation rules implemented:
  - [x] Emergency symptoms -> immediate 911 notice
  - [x] High severity drug interactions -> always escalate
  - [x] Low confidence (<50%) -> warning added to response
  - [x] Missing disclaimer -> auto-appended
- [ ] Full eval suite passing >80% (requires valid API key)
- [x] Observability dashboard in Streamlit sidebar
- [x] Streamlit UI polished (streaming, feedback, welcome screen, sidebar stats)
- [ ] **SUBMIT for early feedback**

---

## Phase 4: Open Source + Final (Day 6-7 | Sat-Sun Mar 1-2)

**Deadline: Sunday Mar 2, 10:59 PM CT**

### Day 6 (Saturday): Polish

- [ ] Package `langchain-healthcare-tools` for PyPI
- [ ] Publish eval dataset (56+ test cases, de-identified)
- [ ] Security hardening (prompt injection prevention, input sanitization)

### Day 7 (Sunday): Documentation + Final Submit

- [x] Agent Architecture Document (README.md)
- [ ] Record demo video (3-5 min)
- [x] AI Cost Analysis (finalized)
- [x] AI Development Process document
- [x] Weekly Development Log
- [ ] LinkedIn post (tag @GauntletAI)
- [x] Final deployment verification
- [ ] **FINAL SUBMISSION by 10:59 PM CT**

---

## Success Metrics

| Metric | MVP Target | Final Target | Day 1 Actual |
|--------|-----------|--------------|-------------|
| Tools implemented | 3+ | 6 | **6** |
| Eval test cases | 5+ | 50+ | **56** |
| Unit tests | 0 | 50+ | **68** |
| Verification types | 1+ | 4 | **4** |
| Single-tool latency | <5s | <3s | **~1-3s** |
| Multi-step latency | <15s | <10s | **~3-5s** |
| Cost per query | <$0.05 | <$0.03 | **$0.000** |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| OpenEMR API complexity | Medium | High | Mock data fallback for all 6 tools | **Mitigated** |
| 1-week timeline pressure | High | High | MVP-first approach, exceeded Day 1 | **Mitigated** |
| LLM hallucination | Medium | Critical | 4-layer verification, source attribution | **Mitigated** |
| Gemini API quota exhaustion | High | High | Switched to Groq free tier on Day 1 | **Resolved** |
| LangSmith env var bug | Medium | Medium | Fixed module-level env var export | **Resolved** |
| Groq API key expiration | Low | Medium | Multi-provider support built in | **Aware** |
