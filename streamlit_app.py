import streamlit as st
import requests
import time
import re
from ui_sidebar import render_sidebar  # Import sidebar module

# -------------------------------
# Session State Initialization
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "num_calls" not in st.session_state:
    st.session_state.num_calls = 0
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0

# Set page config
st.set_page_config(
    page_title="AI Nutritionist Chatbot",
    page_icon="🥗",
    layout="wide"
)

# -------------------------------
# Custom CSS for Chat Layout
# -------------------------------
st.markdown("""
<style>
/* Fixed header styling */
.fixed-header {
    position: fixed;
    top: 0;
    left: 16rem;  /* Adjust based on sidebar width */
    right: 0;
    padding: 1rem 2rem;
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(5px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    z-index: 100;
}

/* Main content padding to prevent content from hiding under header */
.main-content {
    margin-top: 5rem;  /* Adjust based on header height */
    padding: 0 1rem;
}

/* Chat message styling */
.stChatMessage {
    border-radius: 8px;
    margin: 0.5rem 0;
    padding: 1rem;
    font-size: 0.95rem;
    line-height: 1.4;
}
h1 {
    color: #2F855A; /* a calm greenish color */
    margin-bottom: 0.2rem;
    text-align: left;
}
.stChatMessage.user {
    background-color: #c0eec0;
    border: 1px solid #a6d6a6;
}
.stChatMessage.assistant {
    background-color: #eaffea;
    border: 1px solid #d2f2d2;
}
/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #f8fff9; /* a lighter greenish tint */
    border-right: 1px solid #d2f2d2;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #2F855A;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Chat Interface Component
# -------------------------------
def render_chat_interface():
    """Renders the chat interface with a title and chat messages."""
    st.title(" 🥗AI Nutritionist Chatbot")
    st.markdown(
        "<p class='description'>Ask questions about nutrition, meal plans, or dietary guidelines, "
        "and get personalized, evidence-based responses.</p>",
        unsafe_allow_html=True
    )

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            formatted_text = message["content"].replace("<br>", "\n")  # Convert <br> to new lines
            st.write(formatted_text, unsafe_allow_html=True)

    # Chat input
    prompt = st.chat_input("Ask a question about nutrition...")

    if prompt:
        # Update usage stats
        st.session_state.num_calls += 1
        input_token_count = len(prompt.split())
        st.session_state.total_input_tokens += input_token_count

        # Convert user input newlines to <br>
        user_text = prompt.replace("\n", "<br>")

        # Show user message in chat
        with st.chat_message("user"):
            st.write(user_text, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": user_text})

        # Assistant response container
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                # Stream response from Flask backend
                with requests.post(
                    "http://127.0.0.1:5000/query",
                    json={"input": prompt},
                    stream=True
                ) as r:
                    for line in r.iter_lines():
                        if line and line.startswith(b"data: "):
                            chunk = line[6:].decode("utf-8", errors="ignore")
                            full_response += chunk
                            formatted_text = full_response.replace("<br>", "\n") + "▌"  # Show typing effect
                            response_placeholder.write(formatted_text, unsafe_allow_html=True)
                            time.sleep(0.01)

                # Final response formatting
                final_text = full_response.replace("<br>", "\n\n")  # Convert <br> to new lines
                response_placeholder.write(final_text, unsafe_allow_html=True)

                # Track output tokens
                output_token_count = len(full_response.split())
                st.session_state.total_output_tokens += output_token_count

                # Save assistant's response
                st.session_state.messages.append({"role": "assistant", "content": final_text})

            except Exception as e:
                st.error(f"Error: {str(e)}")

# -------------------------------
# Main Layout
# -------------------------------
render_chat_interface()

# -------------------------------
# Render Sidebar
# -------------------------------
render_sidebar()
