import streamlit as st
import requests
import time


API_URL = "http://localhost:8000"


st.set_page_config(
    page_title="YouTube Summarizer AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
    }
    
    /* Main Container */
    .main {
        background-color: #f3f4f6;
        padding-top: 2rem;
    }

    /* Header Styling */
    .header-container {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 0 0 2rem 2rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }
    .header-subtitle {
        font-size: 1.25rem;
        opacity: 0.9;
        font-weight: 400;
    }

    /* Input Section */
    .input-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        background: linear-gradient(to right, #6366f1, #8b5cf6);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(99, 102, 241, 0.5);
    }

    /* Content Cards */
    .content-card {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        height: 100%;
        border: 1px solid #f3f4f6;
    }
    .card-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #f3f4f6;
        padding-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Summary Text */
    .summary-text {
        line-height: 1.7;
        color: #374151;
        font-size: 1.05rem;
    }

    /* Chat Interface */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-height: 500px;
        overflow-y: auto;
        padding-right: 0.5rem;
    }
    .message {
        padding: 1rem;
        border-radius: 1rem;
        max-width: 85%;
        line-height: 1.5;
        font-size: 0.95rem;
        animation: fadeIn 0.3s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background-color: #eff6ff;
        color: #1e40af;
        align-self: flex-end;
        border-bottom-right-radius: 0.25rem;
        margin-left: auto;
        border: 1px solid #dbeafe;
    }
    .bot-message {
        background-color: #f9fafb;
        color: #1f2937;
        align-self: flex-start;
        border-bottom-left-radius: 0.25rem;
        border: 1px solid #e5e7eb;
    }
    .message-role {
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        opacity: 0.7;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary" not in st.session_state:
    st.session_state.summary = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None


st.markdown("""
    <div class="header-container">
        <div class="header-title">YouTube Summarizer AI</div>
        <div class="header-subtitle">Transform long videos into concise, actionable insights in seconds</div>
    </div>
""", unsafe_allow_html=True)

# Input 
if not st.session_state.summary:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    video_url = st.text_input("Paste YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Generate Summary", use_container_width=True):
            if video_url:
                with st.spinner("Analyzing video content..."):
                    try:
                        response = requests.post(f"{API_URL}/summarize", json={"video_url": video_url})
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.session_id = data["session_id"]
                            st.session_state.video_id = data["video_id"]
                            st.session_state.summary = data["summary"]
                            st.session_state.chat_history = []
                            st.rerun()
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a valid YouTube URL")
    st.markdown('</div>', unsafe_allow_html=True)


if st.session_state.summary:
    col_left, col_right = st.columns([1.2, 0.8], gap="large")
    
    with col_left:
        st.markdown(f"""
        <div class="content-card">
            <div class="card-header">
                <span>📝</span> Executive Summary
            </div>
            <div class="summary-text">
                {st.session_state.summary}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.video_id:
            st.markdown("<br>", unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")

    with col_right:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="card-header">
                <span>💬</span> AI Assistant
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for role, text in st.session_state.chat_history:
            css_class = "user-message" if role == "User" else "bot-message"
            icon = "👤" if role == "User" else "🤖"
            st.markdown(f"""
            <div class="message {css_class}">
                <div class="message-role">{icon} {role}</div>
                {text}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask a question about the video...", placeholder="Type your question here...")
            submit_button = st.form_submit_button("Send Message")
            
            if submit_button and user_input:
                st.session_state.chat_history.append(("User", user_input))
                
                try:
                    with st.spinner("Thinking..."):
                        response = requests.post(f"{API_URL}/chat", json={
                            "session_id": st.session_state.session_id,
                            "question": user_input
                        })
                        if response.status_code == 200:
                            answer = response.json()["answer"]
                            st.session_state.chat_history.append(("AI", answer))
                            st.rerun()
                        else:
                            st.error("Failed to get answer")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset Button
        if st.button("🔄 Start New Video", use_container_width=True):
            st.session_state.summary = None
            st.session_state.video_id = None
            st.session_state.chat_history = []
            st.session_state.session_id = None
            st.rerun()

