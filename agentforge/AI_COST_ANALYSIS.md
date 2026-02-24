# AI Cost Analysis
## AgentForge Healthcare AI Agent System

**Developer:** Joe Panetta (Giuseppe)
**Period:** Feb 24 - Mar 2, 2026 (7-day sprint)
**Last Updated:** Feb 23, 2026

---

## 1. Development & Testing Costs (Actual)

### Pre-Development Phase (Feb 23 - Repo Exploration)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Claude Code (repo analysis) | ~300K tokens | 6 agent sessions | $TBD |
| **Subtotal Pre-Dev** | **~300K** | **6** | **$TBD** |

### Phase 1: MVP (Day 1-2)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Gemini Pro (dev/test) | TBD | TBD | TBD |
| Claude (fallback testing) | TBD | TBD | TBD |
| LangSmith (tracing) | TBD | TBD | $0 (free tier) |
| **Subtotal Phase 1** | **TBD** | **TBD** | **TBD** |

### Phase 2: Eval + Observability (Day 3-4)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Gemini Pro (eval runs) | TBD | TBD | TBD |
| Claude (fallback eval) | TBD | TBD | TBD |
| LangSmith | TBD | TBD | $0 |
| **Subtotal Phase 2** | **TBD** | **TBD** | **TBD** |

### Phase 3-4: Polish + Final (Day 5-7)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Gemini Pro | TBD | TBD | TBD |
| Claude/GPT-4 | TBD | TBD | TBD |
| LangSmith | TBD | TBD | $0 |
| **Subtotal Phase 3-4** | **TBD** | **TBD** | **TBD** |

### Total Development Cost

| Category | Estimated | Actual |
|----------|-----------|--------|
| Gemini Pro (primary) | ~$2.25 | TBD |
| Claude (fallback) | ~$3.50 | TBD |
| LangSmith | $0 | $0 |
| OpenEMR (self-hosted) | $0 | $0 |
| Claude Code (AI dev tool) | ~$TBD | TBD |
| Deployment (Railway/Modal) | ~$5 | TBD |
| **TOTAL DEV COST** | **~$11** | **TBD** |

---

## 2. Production Cost Projections

### Assumptions
- 5 queries per user per day
- Average 3,000 tokens per query (2K input, 1K output)
- 90% routed to Gemini Pro, 10% fallback to Claude
- 1.5 tool calls per query average
- 20% verification overhead (additional tokens)
- 30-day months

### LLM Pricing (as of Feb 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|----------------------|
| Gemini Pro | $0.50 | $1.50 |
| Claude Sonnet | $3.00 | $15.00 |
| GPT-4 Turbo | $10.00 | $30.00 |

### Monthly Cost Projections

| Users | Queries/Month | Gemini Cost | Fallback Cost | Infra Cost | Total/Month |
|-------|--------------|-------------|---------------|-----------|-------------|
| 100 | 15,000 | $33.75 | $13.50 | $20 | **$67/month** |
| 1,000 | 150,000 | $337.50 | $135.00 | $50 | **$523/month** |
| 10,000 | 1,500,000 | $3,375 | $1,350 | $200 | **$4,925/month** |
| 100,000 | 15,000,000 | $33,750 | $13,500 | $2,000 | **$49,250/month** |

### Cost Per Query Breakdown

| Component | Cost/Query |
|-----------|-----------|
| Gemini Pro (primary) | $0.003 |
| Fallback overhead (10%) | $0.001 |
| Tool execution | ~$0.000 (API calls) |
| Verification overhead | $0.001 |
| **Total per query** | **~$0.005** |

---

## 3. Cost Optimization Strategies

1. **Prompt caching** - Reuse system prompts and tool schemas (LangChain built-in)
2. **Intelligent routing** - Simple queries to Gemini, complex to premium LLM only when needed
3. **Response caching** - Cache common drug interaction results (TTL: 24h)
4. **Rate limiting** - Cap queries per user (20/day free, 50/day premium)
5. **Batch verification** - Group multiple claims for single verification call
6. **Token optimization** - Minimize prompt size, use structured output to reduce output tokens

---

## 4. Cost vs. Budget Compliance

| Scale | Budget Target | Projected Cost | Status |
|-------|-------------|---------------|--------|
| 1,000 users | <$500/month | $523/month | Within range |
| 10,000 users | <$5,000/month | $4,925/month | Within budget |

*Note: Projections will be updated with actual usage data as development progresses.*
