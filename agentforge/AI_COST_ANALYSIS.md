# AI Cost Analysis
## AgentForge Healthcare AI Agent System

**Developer:** Joe Panetta (Giuseppe)
**Period:** Feb 24 - Mar 2, 2026 (7-day sprint)
**Last Updated:** Feb 24, 2026

---

## 1. Development & Testing Costs (Actual)

### Pre-Development Phase (Feb 23 - Repo Exploration)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Claude Code (repo analysis) | ~300K tokens | 6 agent sessions | ~$4.50 |
| Claude Code (requirements analysis) | ~50K tokens | 1 session | ~$0.75 |
| **Subtotal Pre-Dev** | **~350K** | **7** | **~$5.25** |

### Phase 1: MVP (Day 1 - Feb 24)

| Item | Tokens Used | API Calls | Cost |
|------|------------|-----------|------|
| Groq/Llama 3.3 70B (dev/test) | ~500K tokens | ~50 calls | $0.00 (free tier) |
| Gemini Pro (initial testing) | ~100K tokens | ~10 calls | $0.00 (free tier, hit quota) |
| LangSmith (tracing) | N/A | N/A | $0.00 (free tier) |
| Claude Code (implementation) | ~800K tokens | ~30 sessions | ~$12.00 |
| Render (deployment) | N/A | N/A | $0.00 (free tier) |
| **Subtotal Phase 1** | **~1.4M** | **~90** | **~$12.00** |

### Total Development Cost (Through Day 1)

| Category | Estimated | Actual |
|----------|-----------|--------|
| Claude Code (AI dev tool) | ~$15 | ~$17.25 |
| Groq Llama 3.3 70B (runtime) | $0 | $0.00 |
| Gemini Pro (initial, quota exceeded) | ~$2.25 | $0.00 |
| LangSmith (observability) | $0 | $0.00 |
| OpenEMR (self-hosted Docker) | $0 | $0.00 |
| Render (deployment) | $0 | $0.00 |
| **TOTAL DEV COST** | **~$17** | **~$17.25** |

---

## 2. Production Cost Projections

### Key Change: Switched to Groq (Free Tier)

On Day 1, Gemini Pro free tier quota was exhausted (429 RESOURCE_EXHAUSTED with limit: 0). Pivoted to **Groq** with Llama 3.3 70B Versatile, which provides:
- Free API access (no credit card required)
- Rate limits: 30 requests/min, 6,000 tokens/min
- Latency: 800ms - 5,000ms per query

### Assumptions
- 5 queries per user per day
- Average 3,000 tokens per query (2K input, 1K output)
- 100% routed to Groq/Llama 3.3 70B (free tier)
- 1.5 tool calls per query average
- 20% verification overhead
- 30-day months

### LLM Pricing Comparison (as of Feb 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Used By |
|-------|----------------------|----------------------|---------|
| Groq Llama 3.3 70B | $0.00 (free tier) | $0.00 (free tier) | AgentForge (primary) |
| Gemini Pro | $0.50 | $1.50 | Unavailable (quota) |
| Claude Sonnet | $3.00 | $15.00 | Fallback (not active) |

### Monthly Cost Projections (Groq Free Tier)

| Users | Queries/Month | LLM Cost | Infra Cost | Total/Month |
|-------|--------------|----------|-----------|-------------|
| 100 | 15,000 | $0.00 | $0 (Render free) | **$0/month** |
| 500 | 75,000 | $0.00 | $7 (Render starter) | **$7/month** |
| 1,000 | 150,000 | $0.00 | $25 (Render pro) | **$25/month** |

### Cost Per Query Breakdown (Current)

| Component | Cost/Query |
|-----------|-----------|
| Groq Llama 3.3 70B | $0.000 |
| Tool execution (RxNorm, FDA APIs) | $0.000 (free public APIs) |
| Verification overhead | $0.000 |
| Infrastructure (Render free) | $0.000 |
| **Total per query** | **$0.000** |

### Scaling Beyond Free Tier

If Groq free tier limits are exceeded, options:
1. **Groq paid tier**: $0.59/1M input, $0.79/1M output → ~$0.002/query
2. **Switch to Gemini Pro**: $0.50/$1.50 per 1M → ~$0.003/query (requires billing enabled)
3. **Self-hosted Llama**: $0/token but requires GPU infrastructure (~$50-200/month)

---

## 3. Cost Optimization Strategies

1. **Free tier maximization** - Groq free tier handles development and demo loads
2. **Prompt caching** - Reuse system prompts and tool schemas (LangChain built-in)
3. **Response caching** - Cache common drug interaction results (TTL: 24h)
4. **Rate limiting** - Cap queries per user (20/day free, 50/day premium)
5. **Token optimization** - Minimize prompt size, use structured output to reduce output tokens
6. **Multi-provider routing** - Already implemented (LLM_PROVIDER env var supports groq/gemini)

---

## 4. Actual Cost vs. Budget

| Metric | Target | Actual |
|--------|--------|--------|
| Development cost | <$50 | ~$17.25 |
| Per-query cost (production) | <$0.05 | $0.000 |
| Monthly cost (100 users) | <$100 | $0.00 |
| Monthly cost (1,000 users) | <$500 | $25.00 |

**Result:** Significantly under budget by switching to Groq free tier.

---

## 5. Observability Cost

| Service | Tier | Monthly Cost | What It Provides |
|---------|------|-------------|-----------------|
| LangSmith | Free | $0.00 | Trace logging, latency breakdown, token tracking |
| Custom module | Built-in | $0.00 | TraceRecord persistence, dashboard stats, feedback, eval history |
| Render logs | Free | $0.00 | Application logging, deployment monitoring |

All observability is free-tier or self-hosted. The custom observability module (`app/observability.py`) provides:

- Per-request trace records (17 fields) persisted to JSONL
- Latency breakdown: LLM time, tool time, verification time, total time
- Token usage and provider-aware cost tracking ($0.00 for Groq)
- User feedback (thumbs up/down) stored per trace_id
- Eval history with pass rates and category breakdown
- Dashboard API (`GET /api/dashboard`) for Streamlit sidebar

---

## 6. Testing Infrastructure Cost

| Component | Tests | Runtime | Cost |
|-----------|-------|---------|------|
| Unit tests (pytest) | 68 | <2 seconds | $0.00 (no API keys needed) |
| Integration evals | 56 | ~5-10 min | $0.00 (Groq free tier) |
| LangSmith tracing | N/A | Always-on | $0.00 (free tier) |

Testing requires zero additional spend -- unit tests are fully isolated, and integration evals use the same Groq free tier as production.
