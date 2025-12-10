from pydantic import BaseModel,Field
from typing_extensions import Optional
from dotenv import load_dotenv
from langgraph.graph.state import StateGraph,START,END
load_dotenv()
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
import os 
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.vectorstores import FAISS
llm = ChatGroq(model_name="llama-3.3-70b-versatile",api_key=os.getenv("GROQ_API_KEY"),temperature=0.6)

class YTState(BaseModel):
    video_url: str = Field(..., description="URL of the YouTube video")
    video_id: Optional[str] = Field(None, description="ID of the YouTube video")
    transcript: Optional[str] = Field(None, description="Transcript of the YouTube video")
    summary: Optional[str] = Field(None, description="Summary of the YouTube video")
    vectorstore: Optional[object] = Field(None, description="Vectorstore of the YouTube summary")
    question: Optional[str] = Field(None, description="Question to be answered")
    answer: Optional[str] = Field(None, description="Answer to the question")

    class Config:
        arbitrary_types_allowed = True


import re

def extract_id(state:YTState):
    video_url = state.video_url
    # Regex to handle various YouTube URL formats including live streams and shorts
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|live)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, video_url)
    
    if match:
        return {"video_id": match.group(1)}
    
    return {"video_id": None} 

def get_transcript(state:YTState):
    video_id = state.video_id
    if not video_id:
        return {"transcript": "Error: Could not extract video ID from URL."}
    try:
        fetch = YouTubeTranscriptApi()
        fetch_text = fetch.fetch(video_id=video_id)
        transcript_text = ""
        for text in fetch_text:
            transcript_text += text.text
        return {"transcript": transcript_text}    
    except Exception as e:
        return {"transcript": f"Error fetching transcript: {str(e)}"}

def get_summary(state:YTState):
    transcript = state.transcript
    prompt = PromptTemplate(
        template="Generate a summary of the following transcript: {transcript}",
        input_variables=["transcript"],
    )
    chain = prompt | llm
    result = chain.invoke({"transcript": transcript})
    return {"summary": result.content}


def get_vectorstore(state:YTState):
    summary = state.summary
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts([summary], embeddings)
    return {"vectorstore": vectorstore}

def user_question_answer(state:YTState):
    try:
        print(f"DEBUG: Entering user_question_answer with state type: {type(state)}")
        # Handle dict input if LangGraph passes dict instead of Pydantic model
        if isinstance(state, dict):
            print("DEBUG: State is a dict, converting to object for easier access if needed, or accessing keys directly.")
            question = state.get("question")
            vectorstore = state.get("vectorstore")
        else:
            question = state.question
            vectorstore = state.vectorstore

        print(f"DEBUG: Question: {question}")
        print(f"DEBUG: Vectorstore: {type(vectorstore)}")

        if vectorstore is None:
            return {"answer": "Error: Vectorstore is missing. Please regenerate the summary."}

        retriever = vectorstore.as_retriever()
        
        # Retrieve relevant documents
        docs = retriever.invoke(question)
        context = "\n".join([doc.page_content for doc in docs])
        print(f"DEBUG: Context length: {len(context)}")

        prompt = PromptTemplate(
            template="Answer the following question: {question}" + "\n" + "Context: {context} if you don't have context say i don't have context",
            input_variables=["question","context"],
        )
        chain= prompt |llm
        result = chain.invoke({"question": question,"context": context})
        return {"answer": result.content}
    except Exception as e:
        print(f"ERROR in user_question_answer: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"answer": f"Error processing question: {str(e)}"}


# SUMMARY FLOW
builder = StateGraph(YTState)

builder.add_node("extract_video_id", extract_id)
builder.add_node("fetch_transcript", get_transcript)
builder.add_node("generate_summary", get_summary)
builder.add_node("create_vectorstore", get_vectorstore)

builder.add_edge(START, "extract_video_id")
builder.add_edge("extract_video_id", "fetch_transcript")
builder.add_edge("fetch_transcript", "generate_summary")
builder.add_edge("generate_summary", "create_vectorstore")
builder.add_edge("create_vectorstore", END)

summary_graph = builder.compile()


# QA FLOW
qa_builder = StateGraph(YTState)

qa_builder.add_node("answer_question", user_question_answer)
qa_builder.add_edge(START, "answer_question")
qa_builder.add_edge("answer_question", END)

qa_graph = qa_builder.compile()




