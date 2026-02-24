import logging
import os
import uuid

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.agent.memory import get_session_history, trim_history
from app.agent.prompts import HEALTHCARE_AGENT_SYSTEM_PROMPT
from app.config import settings
from app.observability import RequestTracer
from app.tools.appointment_availability import appointment_availability
from app.tools.drug_interaction import drug_interaction_check
from app.tools.insurance_coverage import insurance_coverage_check
from app.tools.provider_search import provider_search
from app.tools.symptom_lookup import symptom_lookup

logger = logging.getLogger(__name__)

# All available healthcare tools (5 required by PRD)
TOOLS = [drug_interaction_check, symptom_lookup, provider_search, appointment_availability, insurance_coverage_check]


def _create_llm() -> ChatGoogleGenerativeAI:
    """Create the primary LLM (Gemini Pro)."""
    if settings.google_api_key:
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key

    return ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=settings.model_temperature,
        max_output_tokens=settings.model_max_tokens,
    )


def create_agent():
    """Create the healthcare ReAct agent with tools and memory."""
    llm = _create_llm()
    memory = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        checkpointer=memory,
        state_modifier=HEALTHCARE_AGENT_SYSTEM_PROMPT,
    )
    return agent


_agent = None


def get_agent():
    """Get or create the singleton agent instance."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


async def chat(message: str, session_id: str = "default") -> dict:
    """Process a chat message through the healthcare agent with full observability."""
    agent = get_agent()
    trace_id = str(uuid.uuid4())[:8]

    # Start observability trace
    tracer = RequestTracer(query=message, session_id=session_id, trace_id=trace_id)
    tracer.start()

    config = {"configurable": {"thread_id": session_id}}

    history = get_session_history(session_id)
    history.add_user_message(message)

    try:
        tracer.start_llm()
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )
        tracer.end_llm()

        # Extract response and tool usage
        messages = result.get("messages", [])
        response_text = ""
        tools_used = []
        sources = []
        input_tokens = 0
        output_tokens = 0

        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tools_used.append(tc["name"])
                    tracer.end_tool(tc["name"])
            if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
                response_text = msg.content
            # Track token usage from message metadata
            if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                usage = msg.usage_metadata
                input_tokens += getattr(usage, "input_tokens", 0) or 0
                output_tokens += getattr(usage, "output_tokens", 0) or 0
            elif hasattr(msg, "response_metadata"):
                meta = msg.response_metadata or {}
                if "usage_metadata" in meta:
                    usage = meta["usage_metadata"]
                    input_tokens += usage.get("prompt_token_count", 0)
                    output_tokens += usage.get("candidates_token_count", 0)

        if not response_text:
            for msg in reversed(messages):
                if msg.type == "ai" and msg.content:
                    response_text = msg.content
                    break

        # Extract sources
        if "Source:" in response_text:
            for line in response_text.split("\n"):
                if line.strip().startswith("Source:"):
                    sources.append(line.strip().replace("Source: ", ""))

        # Record observability data
        tracer.set_tokens(input_tokens, output_tokens)
        tracer.set_response(response_text, confidence=0.0, sources=sources)

        # Store in history
        history.add_ai_message(response_text)
        trim_history(session_id)

        trace_record = tracer.finish()

        return {
            "response": response_text,
            "sources": sources,
            "confidence": 0.0,  # Will be set by verification layer
            "tools_used": list(set(tools_used)),
            "session_id": session_id,
            "trace_id": trace_id,
            "latency_ms": trace_record.total_latency_ms,
            "tokens": {"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
        }

    except Exception as e:
        logger.error("Agent error: %s", e, exc_info=True)
        tracer.set_error(str(e), category=type(e).__name__)
        tracer.finish()

        error_msg = (
            "I apologize, but I encountered an error processing your request. "
            "Please try rephrasing your question or try again later.\n\n"
            "If you're experiencing a medical emergency, please call 911 immediately."
        )
        history.add_ai_message(error_msg)
        return {
            "response": error_msg,
            "sources": [],
            "confidence": 0.0,
            "tools_used": [],
            "session_id": session_id,
            "trace_id": trace_id,
            "error": str(e),
        }
