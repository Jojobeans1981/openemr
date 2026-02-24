# AI Development Process
## AgentForge Healthcare AI Agent System

**Developer:** Joe Panetta (Giuseppe)
**Last Updated:** Feb 24, 2026

---

## 1. AI Tools Used in Development

| Tool | Purpose | Usage Pattern |
|------|---------|--------------|
| Claude Code (Opus 4.6) | Codebase analysis, implementation, debugging | Primary development tool — wrote all code |
| Groq / Llama 3.3 70B | Primary LLM for agent reasoning | Agent runtime (free tier) |
| LangSmith | Observability, tracing, eval | Monitoring & testing (free tier) |
| Render | Cloud deployment | Hosting (free tier) |
| RxNorm/RxNav API | Drug name validation | Free public NIH API |
| OpenFDA API | Medication information lookup | Free public FDA API |

---

## 2. AI-Assisted Development Decisions

### Decision 1: Repository Analysis (Feb 23)
**AI Role:** Claude Code performed deep codebase exploration
**Process:** 6 parallel research agents analyzed OpenEMR's architecture
**Findings Used:**
- Identified REST API endpoints at `/apis/default/api/` for tool integration
- Mapped FHIR R4 resources (30+) available for healthcare data
- Discovered OAuth2 authentication flow for API access
- Found 282 database tables, identified key ones (patient_data, form_encounter, etc.)
- Understood service layer pattern (BaseService) for potential contribution

**Impact:** Saved estimated 8-12 hours of manual code reading. Enabled informed architecture decisions about which OpenEMR APIs to target.

### Decision 2: LLM Provider Switch — Gemini to Groq (Feb 24)
**AI Role:** Claude Code diagnosed the 429 RESOURCE_EXHAUSTED error and recommended Groq
**Context:** Gemini Pro free tier quota was immediately exhausted (limit: 0). User could not enable billing on Google Cloud.
**Process:**
1. Claude Code identified the error from Render deployment logs
2. Evaluated alternatives: Groq (free, no credit card), OpenAI (paid), Anthropic (paid)
3. Recommended Groq with Llama 3.3 70B Versatile (free, fast, high quality)
4. Implemented multi-provider support (LLM_PROVIDER env var)
**Decision:** Groq as primary, Gemini as optional fallback
**Impact:** Unblocked development entirely. Zero cost for LLM inference. Added multi-provider architecture for resilience.

### Decision 3: Mock Data Fallback Strategy (Feb 24)
**AI Role:** Claude Code designed the fallback architecture
**Context:** OpenEMR Docker may not be running during development or demo
**Decision:** All 6 tools have curated mock data fallbacks:
- drug_interaction_check: 10 known drug pairs from FDA/NIH sources
- symptom_lookup: 5 symptom categories from CDC/NIH/Mayo Clinic
- provider_search: Mock providers across 8 specialties
- appointment_availability: Mock calendar data
- insurance_coverage: 3 plan types (PPO, HMO, Medicare) with 15+ CPT codes each
- medication_lookup: 6 common medications from FDA labels
**Impact:** Development and demos work without any external dependencies. Tools transparently upgrade to live APIs when available.

### Decision 4: 4-Layer Verification System (Feb 24)
**AI Role:** Claude Code implemented the verification pipeline
**Human Role:** Defined safety rules, emergency patterns, forbidden content patterns
**Architecture:**
1. **Hallucination Detection** — Source attribution checking, unsupported claim flagging
2. **Confidence Scoring** — Multi-factor score (base 0.3 + tools + sources + disclaimer - risk)
3. **Domain Constraints** — 16 emergency patterns, dosage prohibition, no definitive diagnoses
4. **Output Validation** — Length checks, tool result inclusion, error pattern detection
**Impact:** Every response is verified before reaching the user. Emergency symptoms trigger immediate escalation.

### Decision 5: ReAct Agent Pattern (Feb 24)
**AI Role:** Claude Code implemented using LangGraph's create_react_agent
**Decision:** LangGraph ReAct over custom agent loop
**Rationale:**
- Built-in tool calling with automatic schema binding
- Memory checkpointing (MemorySaver) for conversation persistence
- Compatible with LangSmith tracing out of the box
- state_modifier parameter for system prompt injection
**Impact:** Robust agent with conversation memory in ~50 lines of code.

---

## 3. Development Methodology

### Eval-Driven Development (EDD)
1. Define test cases (expected input/output/tool usage)
2. Implement feature (tool, verification rule, etc.)
3. Run eval suite (`python -m evals.runner`)
4. Iterate on failures
5. Prevent regression with unit tests

### Testing Strategy
- **68 isolated unit tests** — Test tools, verifier, and observability without API keys
- **43 integration eval cases** — Test full agent pipeline with live LLM
  - 21 happy path cases
  - 12 edge cases
  - 12 adversarial/safety cases
  - 11 multi-step reasoning cases

### AI Code Generation Guidelines
- **AI generates:** API integration code, test scaffolding, tool implementations, boilerplate
- **Human reviews:** All safety-critical code, verification logic, escalation rules
- **Human writes:** Domain constraints, emergency patterns, medical disclaimers
- **Principle:** "AI accelerates, human validates" — especially in healthcare

### Quality Gates
- All AI-generated code reviewed before commit
- Unit tests must pass 100% (`pytest tests/ -v`)
- Eval suite target: >80% pass rate
- Safety tests must pass 100% (no exceptions)
- LangSmith traces reviewed for unexpected behavior

---

## 4. AI Cost Tracking During Development

| Date | Activity | AI Tool | Tokens | Cost |
|------|----------|---------|--------|------|
| Feb 23 | Repo exploration (6 agents) | Claude Code | ~300K | ~$4.50 |
| Feb 23 | Requirements analysis | Claude Code | ~50K | ~$0.75 |
| Feb 24 | Full MVP implementation | Claude Code | ~800K | ~$12.00 |
| Feb 24 | Runtime testing (queries) | Groq Llama 3.3 | ~500K | $0.00 |
| Feb 24 | Gemini testing (quota hit) | Gemini Pro | ~100K | $0.00 |

**Total AI-assisted development cost:** ~$17.25

---

## 5. Lessons Learned

### Day 1 Observations
- Gemini Pro free tier is unreliable — quota exhausted immediately with no warning
- Groq free tier is excellent for development and demos — fast, free, no credit card
- Mock data strategy is essential — never depend on external services for core functionality
- Multi-provider LLM support should be built from Day 1

### What Worked Well
- Parallel agent exploration of large codebase (6 simultaneous agents saved ~10 hours)
- Claude Code for rapid full-stack implementation (FastAPI + Streamlit + LangChain in one session)
- Eval-driven development catches issues early
- Mock data fallback enables development without infrastructure dependencies
- 4-layer verification provides real safety value (caught forbidden patterns, missing sources)

### What Could Improve
- Should have tested Gemini API key limits before committing to it as primary LLM
- LangSmith env var bug (not exported to os.environ) should have been caught earlier with an integration test
- Documentation should be updated continuously, not batched at the end

### AI Limitations Encountered
- LLM sometimes summarizes tool data vaguely instead of presenting specific numbers — fixed with explicit system prompt instructions
- Agent occasionally chains unnecessary tools — addressed with clearer tool selection guidance in system prompt
- Groq/Llama 3.3 sometimes ignores formatting instructions — less of an issue than Gemini
