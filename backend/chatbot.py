import os
import time
from pathlib import Path 
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

INTERNAL_DOCS_DIR = "./files"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables.")
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", )
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_completion_tokens=800)

# Chroma setup
chroma = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory="../data",
    collection_metadata={"name": "documents", "description": "A collection of documents for retrieval"}
)

METADATA_CONFIG = {
    "DFW_Airport_Operations_Manual_-_4-1-2024.pdf": {
        "airport": "dfw",
        "doc_type": "official",
        "source_name": "DFW Airport Operations Manual",
        "topic": "operations",
    },
    "DFW_Design_Criteria_Manual_2025_FINAL.pdf": {
        "airport": "dfw",
        "doc_type": "official",
        "source_name": "DFW Design Criteria Manual",
        "topic": "design",
    }
}


def should_include_sources(query: str) -> bool:
    """
    Detect if the user is explicitly requesting sources/citations.

    Returns True if query contains patterns like:
    - "give me sources", "show sources", "cite sources"
    - "what are your sources", "where did you find"
    - Keywords: "source", "citation", "reference"
    """
    import re
    query_lower = query.lower()

    # High-confidence patterns (direct requests)
    direct_patterns = [
        "give me source",
        "show source",
        "cite source",
        "provide source",
        "list source",
        "what are your source",
        "what's your source",
        "where did you find",
        "which document",
        "from which",
        "citation",
        "cite this",
        "cite that",
        "reference",
    ]

    for pattern in direct_patterns:
        if pattern in query_lower:
            return True

    # Check for standalone "source" keyword
    if re.search(r'\bsource[s]?\b', query_lower):
        return True

    return False


def load_internal_documents():
    # Load PDF documents from files directory
    pdf_loader = DirectoryLoader(
        INTERNAL_DOCS_DIR,
        glob="**/*.pdf",
    )

    docs = pdf_loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap=120,
    )   

    for doc in docs:
        src = doc.metadata.get("source", "")
        filename = Path(src).name if src else "Unknown document"
        doc.metadata.setdefault("doc_title", filename)
        doc.metadata.setdefault("page", "N/A")  # Add default for non-PDF documents
        # retrieval and prompt steering
        base_meta = METADATA_CONFIG.get(
            filename,
             {
                "airport": "dfw",
                "doc_type": "unknown",
                "source_name": filename,
                "topic": "unknown",
            },
        )
        for key,value in base_meta.items():
            doc.metadata.setdefault(key,value)
    if docs:
        split_docs = splitter.split_documents(docs)
        chroma.add_documents(split_docs)
        logger.info(f"Loaded {len(split_docs)} internal docs into Chroma")
    else:
        logger.info("No internal docs to be found for loading")

# Load documents only if collection is empty
# Uncomment the line below to force reload: chroma.reset_collection()
if chroma._collection.count() == 0:
    load_internal_documents()

# Retriever - no threshold filtering
retriever = chroma.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 3}  # Reduce from 5 to 3 - more focused
)
# STRICT PROMPT - Prevents Hallucination
# Shared base instructions
BASE_TEMPLATE = """
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
"""

# Template WITH sources (when explicitly requested)
TEMPLATE_WITH_SOURCES = BASE_TEMPLATE + """
6. Sources section
After the main answer, add a blank line and then a section titled exactly:
Sources:

In this Sources section:
- List each distinct document you actually used, one per line.
- Use the format: "<document-name> (page X)" when page numbers are available in the context; otherwise omit the page.
- Use the document names as they appear in the context when possible.
- Only include sources that contributed facts to your answer.
- If there was no usable context for the answer and you therefore said you do not know, write:
  Sources:
  None (no relevant documentation retrieved).

Now provide your answer, following all of the instructions above.
"""

# Template WITHOUT sources (default - cleaner responses)
TEMPLATE_WITHOUT_SOURCES = BASE_TEMPLATE + """
6. Response format
Provide a clear, direct answer based solely on the context.
Do not include citations, source references, or document names in your response.
Focus on delivering the information the user needs in a concise, helpful manner.

Now provide your answer, following all of the instructions above.
"""

# Document formatting template - applied to each retrieved Document
DOCUMENT_TEMPLATE = """{page_content}

[Source: {doc_title}, Page {page}]"""

doc_prompt = PromptTemplate.from_template(DOCUMENT_TEMPLATE)

# Note: Prompt template and chain creation now happens dynamically in ask_question()
# to support conditional source inclusion based on user query

## CORE FUNCTIONS

def retrieve_document(query: str):
    """Finds relevant documents for a query."""
    return retriever.invoke(input=query)

def ask_question(query: str) -> dict:
    """
    Process a question and return answer with optional sources.
    Detects if sources are requested and adjusts response accordingly.
    """
    t0 = time.time()

    # Detect if user is requesting sources
    include_sources = should_include_sources(query)
    logger.info(f"Sources requested: {include_sources}")

    # Select appropriate prompt template
    template = TEMPLATE_WITH_SOURCES if include_sources else TEMPLATE_WITHOUT_SOURCES
    prompt = ChatPromptTemplate.from_template(template)

    # Retrieve documents
    docs = retriever.invoke(query)

    # Create chain with selected prompt and document formatting
    llm_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt,
        document_prompt=doc_prompt,
        document_separator="\n\n",
        document_variable_name="context"
    )

    # Get LLM response - pass Document objects directly (LangChain will format using doc_prompt)
    response = llm_chain.invoke({
        "input": query,
        "context": docs
    })

    t1 = time.time()
    logger.info(f"Query processing time: {t1 - t0:.2f}s")
    logger.info(f"Raw LLM response: {response}")

    # Build sources list (always collected but only returned if requested)
    sources = []
    if include_sources:
        for doc in docs:
            metadata = doc.metadata
            sources.append({
                "title": metadata.get("doc_title", metadata.get("source", "Unknown document")),
                "page": str(metadata.get("page", "N/A")),
                "snippet": doc.page_content[:150] + "..."
            })

    return {
        "answer": response,
        "sources": sources,
    }
