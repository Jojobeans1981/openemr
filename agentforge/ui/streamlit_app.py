import uuid

import httpx
import streamlit as st

# Configuration
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="AgentForge Healthcare AI",
    page_icon="🏥",
    layout="centered",
)


def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []


def send_message(message: str) -> dict | None:
    """Send a message to the AgentForge API."""
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{API_BASE_URL}/chat",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id,
                },
            )
            if resp.status_code == 200:
                return resp.json()
            st.error(f"API error: {resp.status_code}")
            return None
    except httpx.ConnectError:
        st.error("Cannot connect to backend. Please try again in a moment.")
        return None


def send_feedback(trace_id: str, rating: str):
    """Send feedback for a response."""
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(
                f"{API_BASE_URL}/feedback",
                json={
                    "trace_id": trace_id,
                    "session_id": st.session_state.session_id,
                    "rating": rating,
                },
            )
    except httpx.ConnectError:
        pass


def get_dashboard_stats() -> dict | None:
    """Fetch observability dashboard stats."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{API_BASE_URL}/dashboard")
            if resp.status_code == 200:
                return resp.json()
    except httpx.ConnectError:
        pass
    return None


EXAMPLE_QUESTIONS = [
    "Check interaction between warfarin and aspirin",
    "I have a persistent headache with fever",
    "Find me a cardiologist",
    "What appointments are available for neurology?",
    "Does Blue Cross PPO cover an MRI?",
]


def main():
    init_session()

    # Header
    st.title("AgentForge Healthcare AI")

    # Medical disclaimer banner
    st.warning(
        "This is an AI assistant for **educational purposes only**. "
        "It is not a substitute for professional medical advice, diagnosis, or treatment. "
        "If you are experiencing a medical emergency, call **911** immediately.",
        icon="⚕️",
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### About")
        st.markdown(
            "AgentForge is a healthcare AI agent powered by "
            "LangChain + Llama 3.3 with 5 specialized tools:\n\n"
            "**Drug Interactions** · **Symptom Lookup** · "
            "**Provider Search** · **Appointments** · **Insurance**"
        )

        st.divider()

        if st.button("New Conversation", use_container_width=True):
            try:
                with httpx.Client(timeout=10.0) as client:
                    client.post(
                        f"{API_BASE_URL}/clear-session",
                        json={"session_id": st.session_state.session_id},
                    )
            except httpx.ConnectError:
                pass
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        # Observability dashboard
        stats = get_dashboard_stats()
        if stats and stats.get("total_requests", 0) > 0:
            st.divider()
            st.markdown("### Stats")
            c1, c2 = st.columns(2)
            c1.metric("Requests", stats["total_requests"])
            c2.metric("Errors", stats.get("error_count", 0))
            c1.metric("Avg Latency", f"{stats.get('avg_latency_ms', 0):.0f}ms")
            c2.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.0%}")

            fb = stats.get("feedback", {})
            if fb.get("thumbs_up", 0) or fb.get("thumbs_down", 0):
                st.caption(f"Feedback: {fb.get('thumbs_up', 0)} up / {fb.get('thumbs_down', 0)} down")

            total_cost = stats.get("total_cost_usd", 0)
            if total_cost > 0:
                st.caption(f"Est. cost: ${total_cost:.4f}")

        # Debug (collapsed by default)
        with st.expander("System Debug", expanded=False):
            st.caption(f"Session: {st.session_state.session_id[:8]}")
            if st.button("Run Diagnostics", key="diag"):
                try:
                    with httpx.Client(timeout=15.0) as client:
                        resp = client.get(f"{API_BASE_URL.replace('/api', '')}/debug")
                        if resp.status_code == 200:
                            st.json(resp.json())
                        else:
                            st.error(f"Debug returned {resp.status_code}")
                except Exception as e:
                    st.error(f"Debug failed: {e}")

    # Chat area
    if not st.session_state.messages:
        # Welcome state with example prompts
        st.markdown("#### Try asking:")
        cols = st.columns(2)
        for i, example in enumerate(EXAMPLE_QUESTIONS):
            col = cols[i % 2]
            with col:
                if st.button(f"💬 {example}", key=f"welcome_{i}", use_container_width=True):
                    st.session_state.pending_example = example
                    st.rerun()
    else:
        # Display chat history
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("metadata"):
                    _render_metadata(msg["metadata"], i)

    # Handle pending example question
    if "pending_example" in st.session_state:
        example = st.session_state.pop("pending_example")
        _process_message(example)

    # Chat input
    if prompt := st.chat_input("Ask a healthcare question..."):
        _process_message(prompt)


def _render_metadata(meta: dict, msg_index: int):
    """Render response metadata (tools, confidence, feedback)."""
    # Compact info line
    parts = []
    if meta.get("tools_used"):
        tools_str = ", ".join(meta["tools_used"])
        parts.append(f"**Tools:** {tools_str}")

    confidence = meta.get("confidence", 0)
    color = "green" if confidence >= 0.7 else "orange" if confidence >= 0.5 else "red"
    parts.append(f"**Confidence:** :{color}[{confidence:.0%}]")

    latency = meta.get("latency_ms", 0)
    if latency:
        parts.append(f"**Latency:** {latency:.0f}ms")

    if meta.get("sources"):
        parts.append(f"**Sources:** {len(meta['sources'])}")

    st.caption(" · ".join(parts))

    # Feedback buttons
    trace_id = meta.get("trace_id", "")
    if trace_id:
        feedback_key = f"feedback_{msg_index}"
        if feedback_key not in st.session_state:
            bcol1, bcol2, bcol3 = st.columns([1, 1, 10])
            with bcol1:
                if st.button("👍", key=f"up_{msg_index}", help="Helpful"):
                    send_feedback(trace_id, "up")
                    st.session_state[feedback_key] = "up"
                    st.rerun()
            with bcol2:
                if st.button("👎", key=f"down_{msg_index}", help="Not helpful"):
                    send_feedback(trace_id, "down")
                    st.session_state[feedback_key] = "down"
                    st.rerun()
        else:
            rating = st.session_state[feedback_key]
            icon = "👍" if rating == "up" else "👎"
            st.caption(f"Feedback: {icon} recorded")


def _process_message(message: str):
    """Process a user message and get agent response."""
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your query..."):
            result = send_message(message)

        if result:
            st.markdown(result["response"])
            meta = {
                "tools_used": result.get("tools_used", []),
                "confidence": result.get("confidence", 0),
                "sources": result.get("sources", []),
                "trace_id": result.get("trace_id", ""),
                "latency_ms": result.get("latency_ms", 0),
                "tokens": result.get("tokens", {}),
            }
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"],
                "metadata": meta,
            })
            _render_metadata(meta, len(st.session_state.messages) - 1)
        else:
            error_msg = "Sorry, I couldn't process your request. Please try again."
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
