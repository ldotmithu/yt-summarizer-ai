from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Utils.agents import summary_graph, qa_graph, YTState
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
        initial_state = {"video_url": request.video_url}
        result = summary_graph.invoke(initial_state)
        if result.get("transcript") and "Error" in result["transcript"]:
            raise HTTPException(status_code=400, detail=result["transcript"])
             
        state = YTState(**result)
        
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
        
        result = qa_graph.invoke(state.dict())
        
        return {"answer": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
