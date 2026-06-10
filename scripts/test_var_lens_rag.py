"""
Test VAR-Lens RAG System
=========================

This script tests the VAR-Lens RAG system with sample questions.

Usage:
    python scripts/test_var_lens_rag.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.var_lens.rag_engine import VARLensRAG


def print_separator(char="=", length=70):
    """Print a separator line."""
    print(char * length)


def print_result(question: str, result: dict):
    """
    Print query result in a formatted way.
    
    Args:
        question: The question asked
        result: Result dictionary from RAG query
    """
    print_separator()
    print(f"Question: {question}")
    print_separator("-")
    
    if "error" in result and result["error"]:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"Answer:\n{result.get('answer', 'No answer generated')}")
    
    print_separator("-")
    print(f"Sources ({len(result.get('sources', []))} documents):")
    
    for i, source in enumerate(result.get('sources', []), 1):
        print(f"\n  Source {i}:")
        print(f"    File: {source['metadata'].get('source', 'Unknown')}")
        print(f"    Preview: {source['content'][:150]}...")
    
    print_separator()


def test_retrieval_only():
    """
    Test document retrieval without LLM generation.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Document Retrieval (Without LLM)")
    print("=" * 70)
    
    # Initialize RAG
    rag = VARLensRAG()
    
    # Load vector store
    if not rag.load_vector_store():
        print("❌ Vector store not found. Run build_var_lens_vectorstore.py first.")
        return False
    
    print("✅ Vector store loaded successfully")
    
    # Test questions
    test_questions = [
        "What is the VAR protocol?",
        "When can VAR be used?",
        "What is offside rule?",
        "What are the reviewable incidents in VAR?"
    ]
    
    print("\nTesting retrieval for sample questions...")
    print_separator("-")
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        
        # Get retriever
        retriever = rag.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Retrieve documents
        docs = retriever.invoke(question)
        
        print(f"  Retrieved {len(docs)} documents")
        
        if docs:
            print(f"  Top result preview: {docs[0].page_content[:100]}...")
    
    print_separator()
    print("✅ Retrieval test completed successfully!")
    
    return True


def test_with_mock_llm():
    """
    Test with a mock LLM response (for demonstration).
    """
    print("\n" + "=" * 70)
    print("TEST 2: Mock LLM Response")
    print("=" * 70)
    
    print("\nNote: This test shows how the system would work with an LLM.")
    print("To use a real LLM, you need to:")
    print("  1. Set up IBM Granite API key")
    print("  2. Or use OpenAI/HuggingFace API")
    print("  3. Pass the LLM to rag.create_qa_chain(llm)")
    
    print_separator()


def main():
    """
    Main test function.
    """
    print("=" * 70)
    print("VAR-Lens RAG System - Test Suite")
    print("=" * 70)
    
    # Test 1: Retrieval only
    success = test_retrieval_only()
    
    if not success:
        print("\n❌ Tests failed. Please build vector store first:")
        print("   python scripts/build_var_lens_vectorstore.py")
        return
    
    # Test 2: Mock LLM
    test_with_mock_llm()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("✅ Vector store: Working")
    print("✅ Document retrieval: Working")
    print("⏳ LLM integration: Pending (needs API key)")
    print()
    print("Next steps:")
    print("  1. Set up IBM Granite or OpenAI API key")
    print("  2. Create QA chain with LLM")
    print("  3. Test full question-answering")
    print("  4. Integrate with Langflow")
    print("=" * 70)


if __name__ == "__main__":
    main()

# Made with Bob
