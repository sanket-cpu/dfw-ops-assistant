import os
import time
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from env_loader import load_env_robust
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.documents.base import Document
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

INTERNAL_DOCS_DIR = "./files"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables with encoding fallback
if not load_env_robust():
    logger.warning("Failed to load .env file, using system environment variables only")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables.")
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY, max_completion_tokens=800)

# Chroma setup
chroma = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory="../data",
    collection_metadata={"name": "documents", "description": "A collection of documents for retrieval"}
)

# Simplified metadata configuration - only essential fields for citations
METADATA_CONFIG = {
    "DFW_Airport_Operations_Manual_-_4-1-2024.pdf": {
        "doc_type": "operations_manual",
        "topic": "operations",
    },
    "DFW_Design_Criteria_Manual_2025_FINAL.pdf": {
        "doc_type": "design_manual",
        "topic": "design",
    },
    "HVAC Design Manual.pdf": {
        "doc_type": "technical_manual",
        "topic": "hvac",
    },
    "HVAC LAWA Guidelines.pdf": {
        "doc_type": "guidelines",
        "topic": "hvac",
    },
    "hvac-preventive-maintenance-checklist.pdf": {
        "doc_type": "checklist",
        "topic": "maintenance",
    },
}


def load_internal_documents():
    """Load and process documents from the files directory."""
    # Load all document types
    loaders = [
        DirectoryLoader(INTERNAL_DOCS_DIR, glob="**/*.pdf", loader_cls=PyMuPDFLoader),
        DirectoryLoader(INTERNAL_DOCS_DIR, glob="**/*.docx", loader_cls=Docx2txtLoader),
        DirectoryLoader(INTERNAL_DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader),
    ]

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    if not docs:
        logger.info("No documents found for loading")
        return

    # Add metadata to documents
    for doc in docs:
        filename = Path(doc.metadata.get("source", "")).name or "Unknown document"
        doc.metadata["doc_title"] = filename

        # Add additional metadata if configured
        if filename in METADATA_CONFIG:
            doc.metadata.update(METADATA_CONFIG[filename])

    # Split and store documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    split_docs = splitter.split_documents(docs)
    chroma.add_documents(split_docs)
    logger.info(f"Loaded {len(split_docs)} document chunks into ChromaDB")

#chroma.reset_collection()
if chroma._collection.count() == 0:
    load_internal_documents()

# Retriever - no threshold filtering
retriever = chroma.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 3}  # Reduce from 5 to 3 - more focused
)
# STRICT PROMPT - Prevents Hallucination
TEMPLATE = """
You are an AI assistant specializing in Dallas Fort Worth International Airport (DFW) operations and design criteria.
You support airport staff with questions about DFW operations, design standards, and general airport knowledge.
You MUST answer only using the retrieved document context. If the answer is not supported by the context, you MUST say you do not know and stop.

Context from documents:
{context}

User question:
{input}

Instructions:

1. Role, scope, and grounding
- You answer questions about DFW Airport operations, design criteria, standards, procedures, and general DFW-related topics.
- Treat the context above as the ONLY source of truth. 
- The context may include chunks from these document types:
  - DFW Airport Operations Manual (OPS)
  - DFW Design Criteria Manual (DCM)
- Use ONLY information that is clearly supported or directly implied by the context when answering. 
- Do NOT use general world knowledge, training data, or guesses to fill in gaps.
- If the question is completely outside DFW scope (for example, questions about other airports, unrelated general trivia), answer:
  "I can only answer questions about DFW Airport based on the provided documents."
- If the context does not contain enough information to answer a DFW question, answer:
  "I don't know based on the available documentation."

2. Using multiple documents and resolving conflicts
- The context may contain chunks from both OPS and DCM.
- Read all relevant chunks and synthesize them into one coherent answer.
- If the two sources appear to conflict, briefly note the difference and follow this precedence:
  1) DFW Airport Operations Manual (OPS) for operational procedures and current practices
  2) DFW Design Criteria Manual (DCM) for design standards and specifications
- Prefer the more recent or more operationally specific document when this is clear from the context.
- Never fabricate document names, page numbers, sections, codes, or specifications. Only refer to what appears in the context.

3. Answer style, structure, and level of detail
- Provide practical, user-friendly answers grounded ONLY in the context.
- Provide a clear, direct answer from the documentation.
- Use bullet points or numbered lists for multi-part answers.
- When the context supports it, include concrete details such as:
  - Specific terminal designations, location information, or facility details.
  - Standards, codes, or regulatory requirements.
  - Required permits, approvals, or coordination steps.
  - Operational procedures, timelines, or responsibilities.
- If the user explicitly asks for a short or high-level answer, respond briefly but still grounded only in the context.
- Do NOT introduce theory, best practices, or explanations that are not present in the context.

4. Scenario-based and procedural questions
- When the question involves a scenario or asks about procedures:
  - Identify the relevant manual and section only if this can be inferred from the context.
  - Apply the relevant rules and procedures step-by-step, as described in OPS or DCM.
  - Make clear which manual you are using (for example, "According to the DFW Operations Manual..." or "Based on the Design Criteria Manual...").
- For procedural questions, provide steps in logical order when the context supports it.
- If any part of the scenario is not directly covered by the context, say which parts are clearly governed and explicitly state that the rest is not specified in the available documentation.

5. Safety, honesty, and limits
- Never fabricate:
  - Procedures, specifications, codes, terminal layouts, design standards, organizational roles, or requirements that are not present or clearly implied in the context.
  - Contact details, phone numbers, or personal names.
- When in doubt about a detail, state that the documents provided do not state it clearly instead of guessing.
- Explicitly call out, when supported by context:
  - When work must be escalated or coordinated with specific departments.
  - When regulatory approvals, permits, or special authorization are required.
  - When additional information, tools, or clearances are needed to proceed.
- If no relevant context is retrieved (empty or unrelated), answer:
  "I don't know based on the available documentation."

6. Sources section
After the main answer, add a blank line and then a section titled exactly:
Sources:

In this Sources section:
- List each distinct document you actually used, one per line.
- Use the format: "<document-name> (page X)" when page numbers are available in the context; otherwise omit the page.
- Use the document names as they appear in the context when possible.
- When available in the context, include a web link to the source next to the name.
- Only include sources that contributed facts to your answer.
- If there was no usable context for the answer and you therefore said you do not know, write:
  Sources:
  None (no relevant documentation retrieved).

Now provide your answer, following all of the instructions above.
"""

#FAQs implementation

doc_prompt = PromptTemplate.from_template( 
    "{page_content}\n\n[Source: {doc_title}, page {page}]"
    ) #prompting the model to cite source and metadata aware inside its response
PROMPT = ChatPromptTemplate.from_template(TEMPLATE)
llm_chain = create_stuff_documents_chain(llm, 
                                         PROMPT,
                                         document_prompt= doc_prompt,
                                         document_variable_name= "context"
                                         )
retrieval_chain = create_retrieval_chain(retriever, llm_chain)

## CORE FUNCTIONS

def retrieve_document(query: str) -> list[Document]:
    """Finds relevant documents for a query."""
    return retriever.invoke(input=query)

def ask_question(query: str) -> dict:
    """Ask a question and get an answer with sources."""
    t0 = time.time()
    response = retrieval_chain.invoke({"input": query})
    t1 = time.time()
    logger.info(f"Total query time: {t1 - t0:.2f}s")

    # Extract sources from retrieved documents
    sources = []
    for doc in response.get("context", []):
        metadata = doc.metadata
        sources.append({
            "title": metadata.get("doc_title", metadata.get("source", "Unknown document")),
            "page": str(metadata.get("page", "N/A")),
            "snippet": doc.page_content[:150] + "..."
        })

    return {
        "answer": response["answer"],
        "sources": sources,
    }
