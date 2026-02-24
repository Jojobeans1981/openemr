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

```
[Streamlit UI] → [FastAPI Backend] → [LangChain Agent]
                                          ├── Gemini Pro (primary LLM)
                                          ├── Claude/GPT-4 (fallback LLM)
                                          ├── 6 Healthcare Tools
                                          │   ├── drug_interaction_check (RxNorm/RxNav)
                                          │   ├── symptom_lookup (SNOMED CT/CDC)
                                          │   ├── provider_search (OpenEMR API)
                                          │   ├── appointment_availability (OpenEMR API)
                                          │   ├── insurance_coverage (OpenEMR API)
                                          │   └── medication_lookup (FDA database)
                                          ├── 4-Layer Verification System
                                          └── LangSmith Observability
```

### OpenEMR Integration Points (from repo analysis)
- **REST API:** `/apis/default/api/` - patients, encounters, appointments, providers
- **FHIR R4:** `/apis/default/fhir/` - 30+ FHIR resources (Patient, Medication, etc.)
- **OAuth2:** `/oauth2/default/` - authentication for API access
- **Key tables:** patient_data, form_encounter, facility, users, billing
- **Docker dev env:** `docker/development-easy/` - localhost:8300 (admin/pass)

---

## Phase 1: MVP Gate (Day 1-2 | Mon-Tue Feb 24-25)
**Deadline: Tuesday 24 hours after start**
**Goal: Working agent with 3+ tools, deployed, publicly accessible**

### Hour 0-4: Foundation + First Tool
- [ ] Initialize Python project (pyproject.toml, dependencies)
- [ ] Set up FastAPI backend skeleton
- [ ] Configure LangChain + Gemini Pro integration
- [ ] Implement `drug_interaction_check` tool (RxNorm/RxNav API)
- [ ] Test: "Check interaction between warfarin and aspirin" → structured response
- [ ] Set up LangSmith tracing (from day 1)

### Hour 4-8: Expand to 3 Tools
- [ ] Implement `symptom_lookup` tool (SNOMED CT / CDC mock data)
- [ ] Implement `provider_search` tool (OpenEMR API or mock)
- [ ] Verify each tool works independently with structured output
- [ ] Basic tool schema validation (Pydantic models)

### Hour 8-16: Multi-Step Reasoning + Memory
- [ ] Implement ReAct agent pattern with chain-of-thought
- [ ] Add conversation history (memory system)
- [ ] Chain tools: symptom → provider recommendation flow
- [ ] Maintain context across conversation turns

### Hour 16-20: Verification + Error Handling
- [ ] Implement source attribution requirement (all medical claims cite sources)
- [ ] Basic confidence scoring on responses
- [ ] Graceful failure handling (API timeouts, malformed input)
- [ ] Medical disclaimer system

### Hour 20-24: Eval + Deploy
- [ ] Write 5+ test cases with expected outcomes (happy path)
- [ ] Build simple eval runner
- [ ] Deploy to Railway/Modal (publicly accessible)
- [ ] Streamlit UI - basic chat interface
- [ ] **SUBMIT MVP for gate approval**

### MVP Checklist (all required):
- [ ] Agent responds to natural language healthcare queries
- [ ] At least 3 functional tools invokable by agent
- [ ] Tool calls execute and return structured results
- [ ] Agent synthesizes tool results into coherent responses
- [ ] Conversation history maintained across turns
- [ ] Basic error handling (graceful failure)
- [ ] At least one domain-specific verification check
- [ ] 5+ test cases with expected outcomes
- [ ] Deployed and publicly accessible

---

## Phase 2: Eval Framework + Observability (Day 3-4 | Wed-Thu Feb 26-27)
**Goal: 50+ test cases, full LangSmith observability, remaining tools**

### Day 3 (Wednesday): Eval Suite + Remaining Tools
- [ ] Implement `appointment_availability` tool (OpenEMR calendar API)
- [ ] Implement `insurance_coverage` tool (OpenEMR insurance DB)
- [ ] Implement `medication_lookup` tool (FDA database)
- [ ] Build eval framework structure:
  - [ ] 20+ correctness test cases (ground truth from medical DBs)
  - [ ] 10+ tool selection test cases
  - [ ] 10+ safety/adversarial test cases
  - [ ] 10+ edge case test cases
  - [ ] 10+ multi-step reasoning test cases
- [ ] Implement automated eval runner with pass/fail reporting

### Day 4 (Thursday): Observability + Fallback LLM
- [ ] Full LangSmith integration:
  - [ ] Trace logging (input → reasoning → tool calls → verification → output)
  - [ ] Latency breakdown (LLM time, tool time, verification time)
  - [ ] Error tracking and categorization
  - [ ] Token usage and cost tracking
  - [ ] Tool success rate monitoring
- [ ] Implement fallback LLM strategy:
  - [ ] Gemini Pro primary (90% of queries)
  - [ ] Claude fallback on: confidence <70%, drug interaction detected, verification failure
- [ ] Build verification layer:
  - [ ] Fact checking (cross-ref drug interactions against RxNorm)
  - [ ] Confidence scoring (composite: LLM self-assessment + verification)
  - [ ] Domain constraints (dosage limits, age restrictions)

---

## Phase 3: Early Submission (Day 5 | Fri Feb 28)
**Goal: Comprehensive verification, eval suite >80%, submit for feedback**

- [ ] Complete 4-layer verification system:
  1. Fact Checking - cross-reference against RxNorm
  2. Source Attribution - require citations for all medical claims
  3. Confidence Scoring - composite score with escalation
  4. Domain Constraints - dosage limits, allergy checks
- [ ] Escalation rules implemented:
  - [ ] Confidence <70% → flag for human review
  - [ ] High severity drug interaction → always escalate
  - [ ] Missing source → refuse to return claim
  - [ ] Dosage outside safe range → block + suggest consultation
- [ ] Full eval suite passing >80%
- [ ] Observability dashboards configured
- [ ] Streamlit UI polished (conversation view, verification indicators)
- [ ] **SUBMIT for early feedback**

---

## Phase 4: Open Source + Final (Day 6-7 | Sat-Sun Mar 1-2)
**Deadline: Sunday Mar 2, 10:59 PM CT**

### Day 6 (Saturday): Open Source Prep
- [ ] Package `langchain-healthcare-tools` for PyPI
  - [ ] drug_interaction_check, symptom_lookup, provider_search
  - [ ] Pre-configured verification chains
  - [ ] Example usage and docs
- [ ] Publish eval dataset (50+ test cases, de-identified)
- [ ] Security hardening:
  - [ ] Prompt injection prevention
  - [ ] PHI scrubbing before LLM calls
  - [ ] Input sanitization
  - [ ] API key management

### Day 7 (Sunday): Documentation + Final Submit
- [ ] Agent Architecture Document (1-2 pages)
- [ ] Record demo video (3-5 min)
- [ ] Finalize AI Cost Analysis (actual dev spend + projections)
- [ ] Finalize AI Development Process document
- [ ] Finalize Weekly Development Log
- [ ] LinkedIn post (tag @GauntletAI)
- [ ] Final deployment verification
- [ ] Interview preparation notes
- [ ] **FINAL SUBMISSION by 10:59 PM CT**

---

## Success Metrics

| Metric | MVP Target | Final Target |
|--------|-----------|--------------|
| Tool success rate | >95% | >98% |
| Eval pass rate | >80% | >90% |
| Hallucination rate | <10% | <5% |
| Verification accuracy | >85% | >95% |
| Single-tool latency | <5s | <3s |
| Multi-step latency | <15s | <10s |
| Cost per query | <$0.05 | <$0.03 |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenEMR API complexity | Medium | High | Start with mock data, swap to real API |
| 1-week timeline pressure | High | High | Strict phase gates, MVP-first approach |
| LLM hallucination | Medium | Critical | 4-layer verification, source attribution |
| RxNorm API rate limits | Low | Medium | Caching, fallback to local data |
| Deployment issues | Medium | Medium | Test deploy early (Day 1), have backup |
