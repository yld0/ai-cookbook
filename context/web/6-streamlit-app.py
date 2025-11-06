import streamlit as st

from tools import SearchAgent


# Initialize agent (cached across reruns)
@st.cache_resource
def get_agent():
    """Initialize and cache the search agent."""
    return SearchAgent(verbose=False)


st.title("Research Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = get_agent()
if "generating" not in st.session_state:
    st.session_state.generating = False

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    if st.button("Clear Conversation"):
        st.session_state.agent.reset()
        st.session_state.messages = []
        st.session_state.generating = False
        st.rerun()

    st.divider()
    st.markdown("### Capabilities")
    st.markdown("""
    - Search AI implementation handbook
    - Fetch specific web pages
    - Perform web searches on government sites
    """)

# Display chat history (skip the last message if we're generating)
for i, message in enumerate(st.session_state.messages):
    # Skip the last assistant message if we're currently generating (it's shown in streaming)
    if (
        st.session_state.generating
        and i == len(st.session_state.messages) - 1
        and message["role"] == "assistant"
    ):
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    st.session_state.generating = True
    # Add user message to session state immediately
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response with streaming
    with st.chat_message("assistant"):
        # Create placeholders for tool calls (will be updated immediately)
        tool_calls_placeholder = st.empty()

        # Start streaming and check for tool calls after first yield
        stream_gen = st.session_state.agent.ask_stream(prompt)

        # Get first chunk (empty string that signals tool calls are ready)
        first_chunk = next(stream_gen, "")

        # Immediately check and display tool calls (before blocking parse call)
        tool_calls = st.session_state.agent.get_last_tool_calls()
        if tool_calls:
            with tool_calls_placeholder.expander("🔧 Tool Calls", expanded=True):
                for tool_call in tool_calls:
                    status_emoji = "✔️" if tool_call["status"] == "completed" else "⏳"
                    st.markdown(f"{status_emoji} **{tool_call['name']}**")

                    if tool_call["name"] == "get_web_page" and "url" in tool_call.get(
                        "args", {}
                    ):
                        st.caption(f"URL: {tool_call['args']['url']}")
                    elif tool_call[
                        "name"
                    ] == "search_handbook" and "query" in tool_call.get("args", {}):
                        st.caption(f"Query: {tool_call['args']['query']}")

                    if tool_call.get("result_size"):
                        st.caption(f"Retrieved: {tool_call['result_size']} characters")
        else:
            with tool_calls_placeholder.expander("Decision", expanded=False):
                st.info("No tools needed - responding directly")

        # Continue streaming the rest of the response
        # Create a generator that includes first_chunk if it's not empty, then continues
        def continue_stream():
            if first_chunk:
                yield first_chunk
            yield from stream_gen

        response_text = st.write_stream(continue_stream())

    # Add assistant response to session state and mark generation as complete
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.session_state.generating = False
