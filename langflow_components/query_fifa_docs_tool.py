"""
Query FIFA Documents Tool for LangFlow
Provides access to official FIFA/IFAB documents via RAG - Returns JSON for LLM analysis
"""

from lfx.custom import Component
from lfx.io import Output, MessageTextInput
from lfx.field_typing import Tool, LanguageModel
from langchain_core.tools import StructuredTool
from pathlib import Path
import json
import logging

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


class QueryFIFADocsTool(Component):
    display_name: str = "Query FIFA Documents"
    description: str = "Search official FIFA/IFAB documents for rules and regulations"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "book-open"
    name: str = "query_fifa_docs_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vector_store = None
        self.retriever = None
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
    
    def _init_rag(self):
        """Initialize RAG components (retriever only - no LLM needed)"""
        if self.vector_store is None:
            try:
                self.log("Initializing VAR-Lens RAG...")
                
                # Build path to vector store
                vector_store_path = self.project_root / "data" / "vector_stores" / "var_lens"
                
                if not vector_store_path.exists():
                    error_msg = f"FAISS index not found at: {vector_store_path}"
                    self.log(error_msg)
                    self.status = "Error - FAISS index not found"
                    raise FileNotFoundError(error_msg)
                
                # Initialize embeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                
                # Load vector store
                self.vector_store = FAISS.load_local(
                    str(vector_store_path),
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                
                # Create retriever
                self.retriever = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}
                )
                
                self.log("VAR-Lens retriever initialized successfully")
                self.status = "Ready"
                
            except Exception as e:
                error_msg = f"Failed to initialize VAR-Lens RAG: {e}"
                self.log(error_msg)
                self.status = f"Error: {str(e)}"
                raise
    
    def build_tool(self) -> Tool:
        """Build the FIFA documents query tool"""
        
        # Initialize RAG (retriever only)
        self._init_rag()
        
        def query_fifa_documents(question: str) -> str:
            """Search official FIFA/IFAB documents for rules and regulations.
            
            Args:
                question: Question about FIFA rules, VAR, or regulations
                
            Returns:
                JSON with retrieved documents for LLM analysis
            """
            try:
                self.log(f"Querying FIFA documents: {question[:100]}...")
                self.status = "Searching documents..."
                
                # Get relevant documents
                source_docs = self.retriever.invoke(question)
                
                if not source_docs:
                    return json.dumps({
                        "question": question,
                        "documents_found": 0,
                        "message": "No relevant documents found for your question."
                    }, indent=2)
                
                # Build JSON response with retrieved documents
                documents = []
                seen_sources = set()
                
                # Friendly document titles (no file names or extensions)
                _title_map = {
                    "Laws of the Game 2026_27": "FIFA/IFAB Laws of the Game 2026/27",
                    "Changes to the Laws of the Game 2026_27": "Changes to Laws of the Game 2026/27",
                    "Video Assistant Referee (VAR) protocol _ IFAB": "VAR Protocol (IFAB)",
                    "FWC26_regulations_EN": "FIFA World Cup 2026 Regulations",
                    "Off-field treatment and assessment protocol": "Off-field Treatment Protocol",
                    "Throw-in and goal-kick countdown protocol": "Throw-in & Goal-kick Countdown Protocol",
                    "Time-limited substitution protocol": "Time-limited Substitution Protocol",
                }

                for i, doc in enumerate(source_docs, 1):
                    raw_name = Path(doc.metadata.get('source', 'Unknown')).stem
                    doc_title = _title_map.get(raw_name, "Official FIFA/IFAB Document")

                    documents.append({
                        "rank": i,
                        "content": doc.page_content.strip(),
                        "source": doc_title,
                        "relevance": "high" if i <= 2 else "medium"
                    })

                    seen_sources.add(doc_title)

                result = {
                    "question": question,
                    "documents_found": len(source_docs),
                    "documents": documents,
                    "sources": list(seen_sources),
                    "note": "These are official FIFA/IFAB documents. Analyze and explain the rules clearly."
                }
                
                self.log(f"Successfully retrieved {len(source_docs)} documents")
                self.status = f"Processed {len(source_docs)} documents"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                self.log(f"Error querying FIFA documents: {e}")
                self.status = "Error"
                return json.dumps({"error": str(e)}, ensure_ascii=False)
        
        return StructuredTool.from_function(
            func=query_fifa_documents,
            name="query_fifa_documents",
            description=(
                "Search official FIFA/IFAB documents and return JSON with retrieved rule texts. "
                "Returns raw document content for LLM analysis and explanation. Use for questions about "
                "VAR, offside, penalties, handball, fouls, referee protocols, and FIFA/IFAB regulations. "
                "Data: 658 document chunks from 7 official sources. LLM must analyze and explain the rules."
            )
        )

# Made with Bob
