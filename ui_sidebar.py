import streamlit as st

def render_sidebar():
    """Renders the sidebar with session stats and model info."""

    st.sidebar.markdown("""
    <style>
    .sidebar-header {
        font-size: 1.5em;
        color: #4CAF50; /* Green for health */
        text-align: center;
        margin-bottom: 10px;
    }
    .sidebar-info {
        font-size: 1.1em;
        color: #333;
        margin-bottom: 20px;
    }
    .sidebar-divider {
        border-top: 2px solid #4CAF50;
        margin: 20px 0;
    }

    /* Bubble Container */
    .bubble-container {
        position: relative;
        width: 100%;
        height: 100px;
        overflow: hidden;
        background: none;
    }

   

    /* Additional styles for bottom container */
    .sidebar-bottom {
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("Session Info")
    st.sidebar.markdown(f"**Number of calls:** {st.session_state.num_calls}")
    st.sidebar.markdown(f"**Total input tokens:** {st.session_state.total_input_tokens}")
    st.sidebar.markdown(f"**Total output tokens:** {st.session_state.total_output_tokens}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Model Used:** `meta/llama-3.3-70b-instruct`")
