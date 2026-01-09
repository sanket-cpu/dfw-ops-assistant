#FastAPI backend implementation
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot import ask_question
from pydantic import BaseModel
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DFW Airport RAG Assistant",
    description="A RAG chatbot for DFW Airport operations and design criteria using OpenAI.",
    version="0.1",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# define PyDantic Models

class AskResponse(BaseModel):
   query: str
   answer: str
   sources: List[dict] = []
   error: str = None

# FastAPI API Endpoints

@app.get("/ask")
# try using a dict instead of a string for response
def ask(query: str) -> AskResponse:
    try:
        result = ask_question(query)  # Now returns dict
        return {
            "query": query, 
            "answer": result["answer"],
            "sources": result["sources"]
        }
        #event handling here!!!
    except Exception as e:
        logger.error(f"Error asking question: {e}", exc_info=True)
        return {"error": str(e), "query": query, "answer": "", "sources": []}