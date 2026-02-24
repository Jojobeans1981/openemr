# AI Development Process
## AgentForge Healthcare AI Agent System

**Developer:** Joe Panetta (Giuseppe)
**Last Updated:** Feb 23, 2026

---

## 1. AI Tools Used in Development

| Tool | Purpose | Usage Pattern |
|------|---------|--------------|
| Claude Code (Opus 4.6) | Codebase analysis, implementation, debugging | Primary development tool |
| Gemini Pro | Primary LLM for agent reasoning | Agent runtime |
| Claude Sonnet | Fallback LLM for verification | Agent runtime (fallback) |
| LangSmith | Observability, tracing, eval | Monitoring & testing |
| GitHub Copilot | Code completion | IDE assistance |

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

### Decision 2: Technology Stack Selection
**AI Role:** Pre-Search analysis document (human-led with AI research support)
**Decision:** LangChain + Gemini Pro + LangSmith
**Rationale documented in:** `AgentForge_PreSearch_Document.pdf`

### Decision 3: Tool Design
**AI Role:** Will assist with implementing tool schemas and RxNorm integration
**Human Role:** Domain verification logic, safety guardrails, escalation rules
**Principle:** AI generates boilerplate, human owns safety-critical verification logic

---

## 3. Development Methodology

### Eval-Driven Development (EDD)
1. Write test case (expected input/output)
2. Implement feature
3. Run eval suite
4. Iterate on failures
5. Prevent regression

### AI Code Generation Guidelines
- **AI generates:** Boilerplate, API integration code, test scaffolding, documentation
- **Human reviews:** All safety-critical code, verification logic, escalation rules
- **Human writes:** Domain constraints, dosage validation rules, medical disclaimers
- **Principle:** "AI accelerates, human validates" - especially in healthcare

### Quality Gates
- All AI-generated code reviewed before commit
- Eval suite must pass >80% before merging features
- Safety tests must pass 100% (no exceptions)
- LangSmith traces reviewed for unexpected behavior

---

## 4. AI Cost Tracking During Development

| Date | Activity | AI Tool | Tokens | Cost |
|------|----------|---------|--------|------|
| Feb 23 | Repo exploration (6 agents) | Claude Code | ~300K | TBD |
| Feb 23 | Requirements analysis | Claude Code | ~50K | TBD |
| Feb 24 | Phase 1 implementation | TBD | TBD | TBD |
| ... | ... | ... | ... | ... |

*Updated daily during sprint.*

---

## 5. Lessons Learned

*To be populated as development progresses.*

### Week 1 Observations
- TBD

### What Worked Well
- Parallel agent exploration of large codebase (6 simultaneous agents)
- TBD

### What Could Improve
- TBD

### AI Limitations Encountered
- TBD
