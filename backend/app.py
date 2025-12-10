from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Utils.agents import extract_id, get_transcript, get_summary, get_vectorstore, user_question_answer, YTState
import uuid

app = FastAPI()


sessions = {}

class SummarizeRequest(BaseModel):
    video_url: str

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.post("/summarize")
async def summarize_video(request: SummarizeRequest):
    try:
        # Initialize state
        state = YTState(video_url=request.video_url)
        
        # Extract ID
        id_result = extract_id(state)
        state.video_id = id_result["video_id"]
        
        # Get Transcript
        transcript_result = get_transcript(state)
        if "Error" in transcript_result["transcript"]:
             raise HTTPException(status_code=400, detail=transcript_result["transcript"])
        state.transcript = transcript_result["transcript"]
        
        # Get Summary
        summary_result = get_summary(state)
        state.summary = summary_result["summary"]
        
        # Get Vectorstore
        vectorstore_result = get_vectorstore(state)
        state.vectorstore = vectorstore_result["vectorstore"]
        
        # Create Session
        session_id = str(uuid.uuid4())
        sessions[session_id] = state
        
        return {
            "session_id": session_id,
            "video_id": state.video_id,
            "summary": state.summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_video(request: ChatRequest):
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = sessions[request.session_id]
        state.question = request.question
        
        answer_result = user_question_answer(state)
        
        return {"answer": answer_result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
