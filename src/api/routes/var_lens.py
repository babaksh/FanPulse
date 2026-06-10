"""
VAR-Lens API Routes
===================

FastAPI routes for the VAR-Lens agent.
Provides endpoints for explaining VAR decisions.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/var-lens",
    tags=["VAR-Lens"],
    responses={404: {"description": "Not found"}}
)


# Request/Response Models
class VARQuestion(BaseModel):
    """Request model for VAR questions."""
    question: str = Field(
        ...,
        description="Question about VAR decision or rule",
        min_length=5,
        max_length=500,
        example="Why was that goal disallowed for offside?"
    )
    language: str = Field(
        default="en",
        description="Response language (en, es, ar, fa, etc.)",
        example="en"
    )
    include_sources: bool = Field(
        default=True,
        description="Include source documents in response"
    )


class SourceDocument(BaseModel):
    """Model for source document."""
    content: str = Field(description="Document content snippet")
    file: str = Field(description="Source file name")
    relevance_score: Optional[float] = Field(
        default=None,
        description="Relevance score (0-1)"
    )


class VARAnswer(BaseModel):
    """Response model for VAR answers."""
    question: str = Field(description="Original question")
    answer: str = Field(description="AI-generated answer")
    sources: List[SourceDocument] = Field(
        default=[],
        description="Source documents used"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score (0-1)"
    )
    language: str = Field(description="Response language")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agent: str
    vector_store_loaded: bool
    llm_available: bool


# Global RAG instance (initialized at startup)
rag_engine = None


def initialize_rag():
    """
    Initialize the RAG engine.
    Called at application startup.
    """
    global rag_engine
    
    try:
        from src.agents.var_lens.rag_engine import VARLensRAG
        
        logger.info("Initializing VAR-Lens RAG engine...")
        rag_engine = VARLensRAG()
        
        # Load vector store
        if not rag_engine.load_vector_store():
            logger.warning("Vector store not found. Building new one...")
            rag_engine.setup(force_rebuild=False)
        
        logger.info("VAR-Lens RAG engine initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of the VAR-Lens agent
    """
    return HealthResponse(
        status="healthy" if rag_engine is not None else "unhealthy",
        agent="VAR-Lens",
        vector_store_loaded=rag_engine is not None and rag_engine.vector_store is not None,
        llm_available=rag_engine is not None and rag_engine.qa_chain is not None
    )


@router.post("/explain", response_model=VARAnswer)
async def explain_var_decision(request: VARQuestion):
    """
    Explain a VAR decision or rule.
    
    Args:
        request: Question about VAR
        
    Returns:
        Answer with sources
        
    Raises:
        HTTPException: If RAG engine not initialized or query fails
    """
    # Check if RAG engine is initialized
    if rag_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VAR-Lens agent not initialized. Please contact administrator."
        )
    
    # Check if vector store is loaded
    if rag_engine.vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not loaded. Please build vector store first."
        )
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Query the RAG engine
        result = rag_engine.query(request.question)
        
        # Check for errors
        if "error" in result and result["error"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query failed: {result['error']}"
            )
        
        # Format sources
        sources = []
        if request.include_sources and "sources" in result:
            for source in result["sources"]:
                sources.append(SourceDocument(
                    content=source["content"][:200] + "..." if len(source["content"]) > 200 else source["content"],
                    file=source["metadata"].get("source", "Unknown"),
                    relevance_score=source["metadata"].get("score")
                ))
        
        # Return response
        return VARAnswer(
            question=request.question,
            answer=result.get("answer", "No answer generated"),
            sources=sources,
            language=request.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """
    Get VAR-Lens agent statistics.
    
    Returns:
        Agent statistics
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VAR-Lens agent not initialized"
        )
    
    try:
        stats = rag_engine.get_stats()
        return {
            "agent": "VAR-Lens",
            "status": "operational",
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rebuild-index")
async def rebuild_vector_store():
    """
    Rebuild the vector store from documents.
    
    Note: This is a maintenance endpoint and should be protected in production.
    
    Returns:
        Success message
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VAR-Lens agent not initialized"
        )
    
    try:
        logger.info("Rebuilding vector store...")
        rag_engine.setup(force_rebuild=True)
        logger.info("Vector store rebuilt successfully")
        
        return {
            "status": "success",
            "message": "Vector store rebuilt successfully",
            "stats": rag_engine.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding vector store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild vector store: {str(e)}"
        )


# Sample questions for testing
SAMPLE_QUESTIONS = [
    "What is VAR?",
    "When can VAR be used?",
    "What are the reviewable incidents?",
    "Can VAR review a yellow card?",
    "What is the offside rule?",
    "What happens if the referee makes a clear and obvious error?",
    "Can VAR intervene for a handball?",
    "What is the VAR protocol for goals?"
]


@router.get("/sample-questions")
async def get_sample_questions():
    """
    Get sample questions for testing.
    
    Returns:
        List of sample questions
    """
    return {
        "questions": SAMPLE_QUESTIONS,
        "count": len(SAMPLE_QUESTIONS)
    }

# Made with Bob
