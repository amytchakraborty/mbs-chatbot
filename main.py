from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os

from app.rag_engine import RAGEngine
from app.mbs_analyzer import MBSAnalyzer
from app.response_formatter import ResponseFormatter

app = FastAPI(title="MBS Chatbot", description="Mortgage-Backed Securities Analysis Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
rag_engine = RAGEngine()
mbs_analyzer = MBSAnalyzer()
response_formatter = ResponseFormatter()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    tables: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    summary: str
    session_id: str

@app.get("/")
async def root():
    return {"message": "MBS Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Process question through RAG
        relevant_rules = await rag_engine.retrieve_relevant_rules(request.question)
        
        # Analyze MBS data based on question and rules
        analysis_result = await mbs_analyzer.analyze_question(request.question, relevant_rules)
        
        # Format response
        formatted_response = await response_formatter.format_response(
            request.question, 
            analysis_result, 
            relevant_rules
        )
        
        return ChatResponse(
            answer=formatted_response["answer"],
            tables=formatted_response["tables"],
            charts=formatted_response["charts"],
            summary=formatted_response["summary"],
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
