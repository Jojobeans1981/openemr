import time
import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.healthcare_agent import chat
from app.agent.memory import clear_session
from app.observability import get_dashboard_stats, record_feedback
from app.verification.verifier import post_process_response, verify_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    session_id: str = Field(default="", description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    confidence: float
    tools_used: list[str]
    session_id: str
    trace_id: str
    latency_ms: float
    tokens: dict
    verification: dict


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process a healthcare chat message through the AI agent."""
    session_id = request.session_id or str(uuid.uuid4())

    # Run the agent
    result = await chat(message=request.message, session_id=session_id)

    # Verify the response
    v_start = time.time()
    verification = verify_response(
        response=result["response"],
        tools_used=result["tools_used"],
        original_query=request.message,
    )
    v_latency = (time.time() - v_start) * 1000

    # Post-process (add disclaimers, escalation notices)
    processed_response = post_process_response(result["response"], verification)

    return ChatResponse(
        response=processed_response,
        sources=result["sources"],
        confidence=verification.confidence,
        tools_used=result["tools_used"],
        session_id=session_id,
        trace_id=result.get("trace_id", ""),
        latency_ms=result.get("latency_ms", 0),
        tokens=result.get("tokens", {"input": 0, "output": 0, "total": 0}),
        verification=verification.to_dict(),
    )


class SessionRequest(BaseModel):
    session_id: str


@router.post("/clear-session")
async def clear_session_endpoint(request: SessionRequest):
    """Clear conversation history for a session."""
    clear_session(request.session_id)
    return {"status": "ok", "message": f"Session {request.session_id} cleared"}


class FeedbackRequest(BaseModel):
    trace_id: str = Field(..., description="Trace ID of the response being rated")
    session_id: str = Field(default="", description="Session ID")
    rating: str = Field(..., pattern="^(up|down)$", description="'up' or 'down'")
    correction: str = Field(default="", description="Optional correction text")


@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest):
    """Record user feedback (thumbs up/down) for a response."""
    record_feedback(
        trace_id=request.trace_id,
        session_id=request.session_id,
        rating=request.rating,
        correction=request.correction,
    )
    return {"status": "ok", "message": "Feedback recorded"}


@router.get("/dashboard")
async def dashboard_endpoint():
    """Get observability dashboard stats."""
    return get_dashboard_stats()
