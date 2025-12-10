# YouTube Summarizer AI 🧠

A powerful AI-powered tool that generates concise summaries of YouTube videos and allows you to chat with the video content using a conversational interface. Built with FastAPI, Streamlit, and LangChain.

## 🚀 Features

- **Instant Summarization**: Extract and summarize transcripts from YouTube videos in seconds.
- **Interactive Chat**: Ask questions about the video content and get AI-generated answers based on the transcript.
- **Executive Summary**: Get a quick overview of the key points.
- **Video Playback**: Watch the video directly within the application.
- **Modern UI**: Clean and responsive user interface built with Streamlit.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI/LLM**: [LangChain](https://www.langchain.com/) (Groq integration)
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss)
- **Transcript Service**: [YouTube Transcript API](https://pypi.org/project/youtube-transcript-api/)

## 📋 Prerequisites

- Python 3.8 or higher
- A [Groq API Key](https://console.groq.com/)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/ldotmithu/yt-summarizer-ai.git
    cd yt-summarizer-ai
    ```

2.  **Create a virtual environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**
    Create a `.env` file in the root directory and add your Groq API key:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

## 🏃‍♂️ Usage

You need to run both the backend and frontend servers.

### 1. Start the Backend Server
Open a terminal and run:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```
The backend API will start at `http://localhost:8000`.

### 2. Start the Frontend Application
Open a new terminal window and run:
```bash
streamlit run frontend/app.py
```
The application will open in your default web browser (usually at `http://localhost:8501`).

## 📂 Project Structure

```
yt-summarizer-ai/
├── backend/
│   └── app.py          # FastAPI backend application
├── frontend/
│   └── app.py          # Streamlit frontend application
├── Utils/
│   └── agents.py       # AI agents and logic (LangChain, FAISS)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── README.md           # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.