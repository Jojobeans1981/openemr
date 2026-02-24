import uuid

import httpx
import streamlit as st

# Configuration
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="AgentForge Healthcare AI",
    page_icon="🏥",
    layout="wide",
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
        st.error("Cannot connect to AgentForge backend. Make sure the API server is running on port 8000.")
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


def main():
    init_session()

    # Header
    st.title("AgentForge Healthcare AI")
    st.caption("AI-powered healthcare assistant - Not a substitute for professional medical advice")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown(
            "AgentForge is a healthcare AI agent that can:\n"
            "- Check drug interactions\n"
            "- Look up symptoms and conditions\n"
            "- Find healthcare providers\n"
            "- Check appointment availability\n"
            "- Verify insurance coverage\n"
        )

        st.divider()
        st.subheader("Session")
        st.text(f"ID: {st.session_state.session_id[:8]}...")
        if st.button("New Conversation"):
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

        st.divider()
        st.subheader("Example Questions")
        examples = [
            "Check interaction between warfarin and aspirin",
            "I have a persistent headache with fever",
            "Find me a cardiologist",
            "What appointments are available for neurology?",
            "Does Blue Cross PPO cover an MRI?",
        ]
        for example in examples:
            if st.button(example, key=f"ex_{example[:20]}"):
                st.session_state.pending_example = example
                st.rerun()

        # System debug info
        st.divider()
        st.subheader("System Debug")
        if st.button("Run Diagnostics"):
            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(f"{API_BASE_URL.replace('/api', '')}/debug")
                    if resp.status_code == 200:
                        debug_data = resp.json()
                        for key, val in debug_data.items():
                            st.text(f"{key}: {val}")
                    else:
                        st.error(f"Debug endpoint returned {resp.status_code}")
            except Exception as e:
                st.error(f"Debug failed: {e}")

        # Observability dashboard in sidebar
        st.divider()
        st.subheader("Observability")
        stats = get_dashboard_stats()
        if stats and stats.get("total_requests", 0) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Requests", stats["total_requests"])
                st.metric("Avg Latency", f"{stats.get('avg_latency_ms', 0):.0f}ms")
            with col2:
                st.metric("Errors", stats.get("error_count", 0))
                st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.0%}")

            fb = stats.get("feedback", {})
            if fb.get("thumbs_up", 0) or fb.get("thumbs_down", 0):
                st.caption(f"Feedback: {fb.get('thumbs_up', 0)} up / {fb.get('thumbs_down', 0)} down")

            total_cost = stats.get("total_cost_usd", 0)
            if total_cost > 0:
                st.caption(f"Total cost: ${total_cost:.4f}")
        else:
            st.caption("No data yet - start chatting!")

    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("metadata"):
                meta = msg["metadata"]
                _render_metadata(meta, i)

    # Handle pending example question
    if "pending_example" in st.session_state:
        example = st.session_state.pop("pending_example")
        _process_message(example)

    # Chat input
    if prompt := st.chat_input("Ask a healthcare question..."):
        _process_message(prompt)


def _render_metadata(meta: dict, msg_index: int):
    """Render response metadata (tools, confidence, sources, feedback)."""
    cols = st.columns(4)
    with cols[0]:
        if meta.get("tools_used"):
            st.caption(f"Tools: {', '.join(meta['tools_used'])}")
    with cols[1]:
        confidence = meta.get("confidence", 0)
        color = "green" if confidence >= 0.7 else "orange" if confidence >= 0.5 else "red"
        st.caption(f"Confidence: :{color}[{confidence:.0%}]")
    with cols[2]:
        if meta.get("sources"):
            st.caption(f"Sources: {len(meta['sources'])}")
    with cols[3]:
        latency = meta.get("latency_ms", 0)
        if latency:
            st.caption(f"Latency: {latency:.0f}ms")

    # Feedback buttons
    trace_id = meta.get("trace_id", "")
    if trace_id:
        feedback_key = f"feedback_{msg_index}"
        if feedback_key not in st.session_state:
            bcol1, bcol2, bcol3 = st.columns([1, 1, 8])
            with bcol1:
                if st.button("👍", key=f"up_{msg_index}", help="Helpful response"):
                    send_feedback(trace_id, "up")
                    st.session_state[feedback_key] = "up"
                    st.rerun()
            with bcol2:
                if st.button("👎", key=f"down_{msg_index}", help="Unhelpful response"):
                    send_feedback(trace_id, "down")
                    st.session_state[feedback_key] = "down"
                    st.rerun()
        else:
            rating = st.session_state[feedback_key]
            icon = "👍" if rating == "up" else "👎"
            st.caption(f"Feedback: {icon} recorded")


def _process_message(message: str):
    """Process a user message and get agent response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
