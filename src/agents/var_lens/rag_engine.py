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

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

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
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
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
            result = self.qa_chain({"query": question})
            
            return {
                "answer": result["result"],
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
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
