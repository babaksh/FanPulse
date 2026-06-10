"""
Test VAR-Lens RAG System with LLM Integration
Tests the complete Q&A pipeline with different LLM providers
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.var_lens.rag_engine import VARLensRAG
from src.agents.var_lens.llm_providers import LLMFactory, print_provider_info


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def test_llm_provider(provider: str, model_name: str | None = None):
    """
    Test a specific LLM provider
    
    Args:
        provider: Provider name (ibm_granite, openai, huggingface)
        model_name: Optional specific model name
    """
    print_section(f"Testing {provider.upper()} Provider")
    
    try:
        # Initialize RAG engine
        print("Initializing VAR-Lens RAG Engine...")
        rag = VARLensRAG()
        
        # Load vector store
        print("Loading vector store...")
        if not rag.load_vector_store():
            print("❌ Failed to load vector store")
            return False
        
        print("✅ Vector store loaded successfully")
        
        # Create QA chain with specified provider
        print(f"\nCreating QA chain with {provider}...")
        try:
            rag.create_qa_chain(
                provider=provider,
                model_name=model_name,
                temperature=0.7,
                max_tokens=500
            )
            print("✅ QA chain created successfully")
        except ValueError as e:
            print(f"⚠️  Configuration error: {e}")
            print(f"   Please set the required environment variables for {provider}")
            return False
        except ImportError as e:
            print(f"⚠️  Missing dependency: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to create QA chain: {e}")
            return False
        
        # Test questions
        test_questions = [
            "What is VAR?",
            "When can VAR be used?",
            "What are the reviewable incidents?"
        ]
        
        print("\nTesting Q&A with sample questions...")
        print("-" * 70)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            try:
                result = rag.query(question)
                print(f"   Answer: {result['answer'][:200]}...")
                print(f"   Sources: {len(result['source_documents'])} documents")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "="*70)
        print(f"✅ {provider.upper()} test completed successfully!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print_section("VAR-Lens RAG System - LLM Integration Test")
    
    # Print available providers
    print_provider_info()
    
    # Check which providers are configured
    print_section("Checking Provider Configuration")
    
    providers_to_test = []
    
    # Check IBM Granite
    if os.getenv("IBM_WATSONX_API_KEY") and os.getenv("IBM_WATSONX_PROJECT_ID"):
        print("✅ IBM Granite (watsonx.ai) - Configured")
        providers_to_test.append(("ibm_granite", "ibm/granite-13b-chat-v2"))
    else:
        print("⚠️  IBM Granite - Not configured")
        print("   Set IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID")
    
    # Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI - Configured")
        providers_to_test.append(("openai", "gpt-3.5-turbo"))
    else:
        print("⚠️  OpenAI - Not configured")
        print("   Set OPENAI_API_KEY")
    
    # Check HuggingFace
    if os.getenv("HUGGINGFACE_API_KEY"):
        print("✅ HuggingFace - Configured")
        providers_to_test.append(("huggingface", "mistralai/Mistral-7B-Instruct-v0.2"))
    else:
        print("⚠️  HuggingFace - Not configured (optional)")
        print("   Set HUGGINGFACE_API_KEY")
    
    # Test configured providers
    if not providers_to_test:
        print("\n" + "="*70)
        print("❌ No LLM providers configured!")
        print("="*70)
        print("\nTo test LLM integration, configure at least one provider:")
        print("\n1. IBM Granite (Recommended for challenge):")
        print("   $env:IBM_WATSONX_API_KEY='your-api-key'")
        print("   $env:IBM_WATSONX_PROJECT_ID='your-project-id'")
        print("\n2. OpenAI (For quick testing):")
        print("   $env:OPENAI_API_KEY='sk-...'")
        print("\n3. HuggingFace (Free alternative):")
        print("   $env:HUGGINGFACE_API_KEY='hf_...'")
        return
    
    # Run tests
    results = {}
    for provider, model in providers_to_test:
        success = test_llm_provider(provider, model)
        results[provider] = success
    
    # Print summary
    print_section("Test Summary")
    for provider, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{provider:20s} {status}")
    
    print("\n" + "="*70)
    if all(results.values()):
        print("🎉 All configured providers tested successfully!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("="*70)


if __name__ == "__main__":
    main()

# Made with Bob
