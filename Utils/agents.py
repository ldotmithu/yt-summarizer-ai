from pydantic import BaseModel,Field
from typing_extensions import Optional
from dotenv import load_dotenv

load_dotenv()
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
import os 
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.vectorstores import FAISS
llm = ChatGroq(model_name="openai/gpt-oss-120b",api_key=os.getenv("GROQ_API_KEY"),temperature=0.6)

class YTState(BaseModel):
    video_url: str = Field(..., description="URL of the YouTube video")
    video_id: Optional[str] = Field(None, description="ID of the YouTube video")
    transcript: Optional[str] = Field(None, description="Transcript of the YouTube video")
    summary: Optional[str] = Field(None, description="Summary of the YouTube video")
    vectorstore: Optional[object] = Field(None, description="Vectorstore of the YouTube summary")
    question: Optional[str] = Field(None, description="Question to be answered")

    class Config:
        arbitrary_types_allowed = True


class ExtractVideoID(BaseModel):
    video_id: Optional[str] = Field(None, description="ID of the YouTube video")  


def extract_id(state:YTState):
    video = state.video_url 
    prompt = PromptTemplate(
        template="Extract the video ID from the following URL: {video_url}",
        input_variables=["video_url"],
    )
    llm_with_stroutput = llm.with_structured_output(ExtractVideoID)
    chain = prompt | llm_with_stroutput
    result = chain.invoke({"video_url": video})
    return {"video_id": result.video_id} 

def get_transcript(state:YTState):
    video_id = state.video_id
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
    question = state.question
    vectorstore = state.vectorstore.as_retriever()
    
    # Retrieve relevant documents
    docs = vectorstore.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = PromptTemplate(
        template="Answer the following question: {question}" + "\n" + "Context: {context} if you don't have context say i don't have context",
        input_variables=["question","context"],
    )
    chain= prompt |llm
    result = chain.invoke({"question": question,"context": context})
    return {"answer": result.content}



