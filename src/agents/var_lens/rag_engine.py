"""
VAR-Lens RAG Engine
===================

This module implements the core RAG (Retrieval Augmented Generation) engine
for the VAR-Lens agent. It processes FIFA documents and provides accurate
answers to VAR-related questions.

Components:
- Document Loading: Loads processed Markdown files
- Text Splitting: Chunks documents for better retrieval
- Embeddings: Converts text to vectors using HuggingFace
- Vector Store: FAISS for efficient similarity search
- RAG Chain: Combines retrieval with LLM generation
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from .llm_providers import LLMFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VARLensRAG:
    """
    VAR-Lens RAG Engine
    
    This class handles the entire RAG pipeline for VAR decision explanations.
    """
    
    def __init__(
        self,
        docs_path: str = "data/processed_documents",
        vector_store_path: str = "data/vector_stores/var_lens",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        k_documents: int = 4
    ):
        """
        Initialize the VAR-Lens RAG engine.
        
        Args:
            docs_path: Path to processed Markdown documents
            vector_store_path: Path to save/load vector store
            embedding_model: HuggingFace embedding model name
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            k_documents: Number of documents to retrieve
        """
        self.docs_path = Path(docs_path)
        self.vector_store_path = Path(vector_store_path)
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k_documents = k_documents
        
        # Initialize components
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        
        logger.info("VAR-Lens RAG Engine initialized")
    
    def load_documents(self) -> List[Any]:
        """
        Load all Markdown documents from the processed documents directory.
        
        Returns:
            List of loaded documents
        """
        logger.info(f"Loading documents from: {self.docs_path}")
        
        # Load all .md files
        loader = DirectoryLoader(
            str(self.docs_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents")
        
        return documents
    
    def split_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        logger.info("Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        
        return chunks
    
    def create_embeddings(self):
        """
        Initialize the embedding model.
        """
        logger.info(f"Initializing embeddings: {self.embedding_model_name}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embeddings initialized successfully")
    
    def create_vector_store(self, chunks: List[Any], save: bool = True):
        """
        Create FAISS vector store from document chunks.
        
        Args:
            chunks: List of document chunks
            save: Whether to save the vector store to disk
        """
        logger.info("Creating vector store...")
        
        if self.embeddings is None:
            self.create_embeddings()
        
        # Type guard to ensure embeddings is not None
        if self.embeddings is None:
            raise ValueError("Failed to create embeddings")
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        logger.info("Vector store created successfully")
        
        # Save to disk
        if save:
            self.save_vector_store()
    
    def save_vector_store(self):
        """
        Save the vector store to disk.
        """
        if self.vector_store is None:
            logger.error("No vector store to save")
            return
        
        # Create directory if it doesn't exist
        self.vector_store_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving vector store to: {self.vector_store_path}")
        self.vector_store.save_local(str(self.vector_store_path))
        logger.info("Vector store saved successfully")
    
    def load_vector_store(self):
        """
        Load vector store from disk.
        """
        if not self.vector_store_path.exists():
            logger.error(f"Vector store not found at: {self.vector_store_path}")
            return False
        
        logger.info(f"Loading vector store from: {self.vector_store_path}")
        
        if self.embeddings is None:
            self.create_embeddings()
        
        # Type guard to ensure embeddings is not None
        if self.embeddings is None:
            raise ValueError("Failed to create embeddings")
        
        self.vector_store = FAISS.load_local(
            str(self.vector_store_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        logger.info("Vector store loaded successfully")
        return True
    
    def create_prompt_template(self) -> PromptTemplate:
        """
        Create the prompt template for VAR explanations.
        
        Returns:
            PromptTemplate object
        """
        template = """You are VAR-Lens, an expert AI assistant specialized in explaining VAR (Video Assistant Referee) decisions in football/soccer.

Your role is to:
1. Provide clear, accurate explanations based on official FIFA/IFAB rules
2. Reference specific rules and protocols when explaining decisions
3. Use simple language that fans can understand
4. Be objective and educational

Context from FIFA/IFAB Documents:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so clearly
- Reference specific rule numbers or sections when applicable
- Keep explanations concise but complete
- Use bullet points for clarity when appropriate

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def create_llm(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Create an LLM instance using the LLM Factory.
        
        Args:
            provider: LLM provider (ibm_granite, openai, huggingface, etc.)
            model_name: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM instance
        """
        logger.info(f"Creating LLM with provider: {provider}")
        
        try:
            llm = LLMFactory.create_llm(
                provider=provider,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
            logger.info(f"LLM created successfully: {provider}")
            return llm
        except Exception as e:
            logger.error(f"Failed to create LLM: {e}")
            raise
    
    def create_qa_chain(
        self,
        llm: Optional[Any] = None,
        provider: str = "openai",
        model_name: Optional[str] = None,
        **llm_kwargs
    ):
        """
        Create the QA chain combining retrieval and generation.
        
        Args:
            llm: Pre-configured language model (if None, creates one using provider)
            provider: LLM provider to use if llm is None
            model_name: Model name to use if llm is None
            **llm_kwargs: Additional arguments for LLM creation
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized. Call create_vector_store() or load_vector_store() first.")
            return
        
        logger.info("Creating QA chain...")
        
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k_documents}
        )
        
        # Create prompt
        prompt = self.create_prompt_template()
        
        # Create or use provided LLM
        if llm is None:
            logger.info(f"No LLM provided, creating one with provider: {provider}")
            try:
                llm = self.create_llm(
                    provider=provider,
                    model_name=model_name,
                    **llm_kwargs
                )
            except Exception as e:
                logger.error(f"Failed to create LLM: {e}")
                logger.warning("QA chain created but needs LLM to function.")
                return
        
        # Create QA chain using LCEL (LangChain Expression Language)
        # This is the modern way to build chains in LangChain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.retriever = retriever
        self.qa_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("QA chain created successfully")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the VAR-Lens system with a question.
        
        Args:
            question: User's question about VAR
            
        Returns:
            Dictionary containing answer and source documents
        """
        if self.qa_chain is None:
            logger.error("QA chain not initialized. Call create_qa_chain() first.")
            return {
                "error": "System not initialized",
                "answer": None,
                "sources": []
            }
        
        logger.info(f"Processing query: {question}")
        
        try:
            # Get answer from chain
            answer = self.qa_chain.invoke(question)
            
            # Get source documents separately using invoke
            source_docs = self.retriever.invoke(question)
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in source_docs
                ]
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    def add_document_from_file(
        self,
        file_path: str,
        match_id: Optional[str] = None,
        document_type: str = "match_report",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new document (PDF or Markdown) to the existing vector store.
        This allows dynamic ingestion of match reports, VAR decisions, etc.
        
        Args:
            file_path: Path to the document file (PDF or MD)
            match_id: Optional match identifier
            document_type: Type of document (match_report, var_decision, etc.)
            metadata: Additional metadata to attach to the document
            
        Returns:
            Dictionary with ingestion results
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized. Call setup() first.")
            return {
                "success": False,
                "error": "Vector store not initialized",
                "chunks_added": 0
            }
        
        logger.info(f"Adding document from: {file_path}")
        
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "chunks_added": 0
                }
            
            # Load document based on file type
            if file_path_obj.suffix.lower() == '.pdf':
                # Process PDF with Docling
                content = self._process_pdf_with_docling(file_path)
            elif file_path_obj.suffix.lower() in ['.md', '.txt']:
                # Load text file directly
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_path_obj.suffix}",
                    "chunks_added": 0
                }
            
            # Create document with metadata
            doc_metadata = {
                "source": str(file_path),
                "document_type": document_type,
                "added_at": datetime.now().isoformat(),
                "file_name": file_path_obj.name
            }
            
            if match_id:
                doc_metadata["match_id"] = match_id
            
            if metadata:
                doc_metadata.update(metadata)
            
            # Create LangChain document
            document = Document(
                page_content=content,
                metadata=doc_metadata
            )
            
            # Split into chunks
            chunks = self.split_documents([document])
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            # Save updated vector store
            self.save_vector_store()
            
            logger.info(f"Successfully added {len(chunks)} chunks from {file_path}")
            
            return {
                "success": True,
                "chunks_added": len(chunks),
                "file_name": file_path_obj.name,
                "match_id": match_id,
                "document_type": document_type
            }
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks_added": 0
            }
    
    def _process_pdf_with_docling(self, pdf_path: str) -> str:
        """
        Process PDF file using Docling to extract text.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            from docling.document_converter import DocumentConverter
            
            logger.info(f"Processing PDF with Docling: {pdf_path}")
            
            converter = DocumentConverter()
            result = converter.convert(pdf_path)
            
            # Export to markdown
            markdown_content = result.document.export_to_markdown()
            
            return markdown_content
            
        except ImportError:
            logger.warning("Docling not available, using fallback text extraction")
            # Fallback: simple text extraction
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except:
                raise Exception("Could not process PDF. Install docling or PyPDF2.")
    
    def add_text_content(
        self,
        content: str,
        match_id: Optional[str] = None,
        document_type: str = "text_content",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add text content directly to the vector store without a file.
        Useful for adding live data, API responses, etc.
        
        Args:
            content: Text content to add
            match_id: Optional match identifier
            document_type: Type of content
            metadata: Additional metadata
            
        Returns:
            Dictionary with ingestion results
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized. Call setup() first.")
            return {
                "success": False,
                "error": "Vector store not initialized",
                "chunks_added": 0
            }
        
        logger.info(f"Adding text content ({len(content)} characters)")
        
        try:
            # Create document with metadata
            doc_metadata = {
                "source": "direct_input",
                "document_type": document_type,
                "added_at": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            if match_id:
                doc_metadata["match_id"] = match_id
            
            if metadata:
                doc_metadata.update(metadata)
            
            # Create LangChain document
            document = Document(
                page_content=content,
                metadata=doc_metadata
            )
            
            # Split into chunks
            chunks = self.split_documents([document])
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            # Save updated vector store
            self.save_vector_store()
            
            logger.info(f"Successfully added {len(chunks)} chunks from text content")
            
            return {
                "success": True,
                "chunks_added": len(chunks),
                "match_id": match_id,
                "document_type": document_type,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error adding text content: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks_added": 0
            }
    
    def query_with_filter(
        self,
        question: str,
        match_id: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the system with optional filtering by match_id or document_type.
        
        Args:
            question: User's question
            match_id: Filter by specific match
            document_type: Filter by document type
            
        Returns:
            Dictionary containing answer and filtered sources
        """
        if self.qa_chain is None:
            logger.error("QA chain not initialized. Call create_qa_chain() first.")
            return {
                "error": "System not initialized",
                "answer": None,
                "sources": []
            }
        
        logger.info(f"Processing filtered query: {question}")
        
        try:
            # Get all relevant documents first
            source_docs = self.retriever.invoke(question)
            
            # Apply filters
            filtered_docs = []
            for doc in source_docs:
                metadata = doc.metadata
                
                # Check match_id filter
                if match_id and metadata.get("match_id") != match_id:
                    continue
                
                # Check document_type filter
                if document_type and metadata.get("document_type") != document_type:
                    continue
                
                filtered_docs.append(doc)
            
            # If no documents match filter, use all documents
            if not filtered_docs:
                logger.warning("No documents matched filter, using all retrieved documents")
                filtered_docs = source_docs
            
            # Format context from filtered documents
            context = "\n\n".join(doc.page_content for doc in filtered_docs)
            
            # Generate answer using the chain
            answer = self.qa_chain.invoke(question)
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in filtered_docs
                ],
                "filter_applied": {
                    "match_id": match_id,
                    "document_type": document_type
                },
                "total_sources": len(source_docs),
                "filtered_sources": len(filtered_docs)
            }
            
        except Exception as e:
            logger.error(f"Error processing filtered query: {e}")
            return {
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    def setup(self, force_rebuild: bool = False):
        """
        Complete setup of the RAG system.
        
        Args:
            force_rebuild: If True, rebuild vector store even if it exists
        """
        logger.info("Starting VAR-Lens RAG setup...")
        
        # Try to load existing vector store
        if not force_rebuild and self.load_vector_store():
            logger.info("Using existing vector store")
        else:
            # Build new vector store
            logger.info("Building new vector store...")
            documents = self.load_documents()
            chunks = self.split_documents(documents)
            self.create_vector_store(chunks, save=True)
        
        logger.info("VAR-Lens RAG setup complete!")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            "docs_path": str(self.docs_path),
            "vector_store_path": str(self.vector_store_path),
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "k_documents": self.k_documents,
            "vector_store_exists": self.vector_store is not None
        }
        
        if self.vector_store is not None:
            stats["num_vectors"] = self.vector_store.index.ntotal
        
        return stats


def main():
    """
    Main function for testing the RAG engine.
    """
    print("=" * 60)
    print("VAR-Lens RAG Engine - Setup and Test")
    print("=" * 60)
    
    # Initialize
    rag = VARLensRAG()
    
    # Setup (build or load vector store)
    rag.setup(force_rebuild=False)
    
    # Print stats
    print("\nSystem Statistics:")
    print("-" * 60)
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("Setup complete! Vector store is ready.")
    print("=" * 60)
    
    # Note about LLM
    print("\nNote: To use the QA chain, you need to provide an LLM.")
    print("Example with OpenAI:")
    print("  from langchain_openai import ChatOpenAI")
    print("  llm = ChatOpenAI(model='gpt-3.5-turbo')")
    print("  rag.create_qa_chain(llm)")
    print("  result = rag.query('What is offside?')")


if __name__ == "__main__":
    main()

# Made with Bob
