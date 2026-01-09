#FastAPI backend implementation 
from fastapi import FastAPI
from chatbot import retrieve_document,ask_question
from pydantic import BaseModel
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Airport RAG Assistant",
    description= "A simple chatbot using OpenAI. Enables asking questions and getting answers based on uploaded documents.",
      version="0.1",
)

# define PyDantic Models 

class DocumentResponse(BaseModel):
    documents: List 
    total: int
    query: str
    error: str = None


class AskResponse(BaseModel):
   query: str
   answer: str
   sources: List[dict] = []
   error: str = None

# FastAPI API Endpoints 

@app.get("/")
def read_root():
    return {
        "service": "RAG Assistant using FastAPI, OPENAI  and Streamlit",
        "description": "Welcome to the Airport Assistant!",
        "status": "running"
    }

@app.get("/documents/{query}")
def search_documents(query: str) ->  DocumentResponse:
    try:
        documents = retrieve_document(query)
        return {"documents": documents ,"total": len(documents) , "query": query}

    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        return {"error": str(e), "documents": [], "total": 0, "query": query}


"""@app.post("/documents")
async def upload_documents(files: List[UploadFile]) -> DocumentUploadResponse:
    try:
        documents = []
        for file in files:
            if file.content_type != "application/pdf":
                logger.error(f"Unsupported file type: {file.content_type}")
                raise ValueError("Only PDF files are supported")
            content = await file.read()
            parsed_docs = parse_pdf(content)
            documents.extend(parsed_docs)
        status = store_documents(documents)
        return {"documents": documents, "total": len(documents), "status": status}
    except Exception as e:
        logger.error(f"Error uploading documents: {e}", exc_info=True)
        return {"error": str(e), "status": "failed", "documents": [], "total": 0}

"""
@app.get("/ask")
def ask(query: str) -> AskResponse:
    try:
        result = ask_question(query)  # Now returns dict
        return {
            "query": query, 
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        logger.error(f"Error asking question: {e}", exc_info=True)
        return {"error": str(e), "query": query, "answer": "", "sources": []}