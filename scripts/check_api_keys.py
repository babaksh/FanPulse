"""
Check which LLM API keys are configured
"""
import os
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
    else:
        # Fallback for older Python versions
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_api_keys():
    """Check which API keys are set"""
    keys_found = []
    
    # Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        keys_found.append("[OK] OpenAI API key is set")
    else:
        keys_found.append("[--] OpenAI API key not found")
    
    # Check IBM Granite
    if os.getenv("IBM_WATSONX_API_KEY") and os.getenv("IBM_WATSONX_PROJECT_ID"):
        keys_found.append("[OK] IBM Granite API key and project ID are set")
    elif os.getenv("IBM_WATSONX_API_KEY"):
        keys_found.append("[!!] IBM Granite API key is set but PROJECT_ID is missing")
    else:
        keys_found.append("[--] IBM Granite API key not found")
    
    # Check HuggingFace
    if os.getenv("HUGGINGFACE_API_KEY"):
        keys_found.append("[OK] HuggingFace API key is set")
    else:
        keys_found.append("[--] HuggingFace API key not found")
    
    # Check Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        keys_found.append("[OK] Anthropic API key is set")
    else:
        keys_found.append("[--] Anthropic API key not found")
    
    # Check Google
    if os.getenv("GOOGLE_API_KEY"):
        keys_found.append("[OK] Google API key is set")
    else:
        keys_found.append("[--] Google API key not found")
    
    print("\n" + "="*60)
    print("LLM API Key Status")
    print("="*60)
    for status in keys_found:
        print(status)
    print("="*60 + "\n")
    
    # Check if any key is set
    has_key = any("[OK]" in status for status in keys_found)
    
    if not has_key:
        print("[!!] No LLM API keys found!")
        print("\nTo test with LLM, set one of these environment variables:")
        print("  • OPENAI_API_KEY (easiest option)")
        print("  • IBM_WATSONX_API_KEY + IBM_WATSONX_PROJECT_ID (for challenge)")
        print("  • HUGGINGFACE_API_KEY (free option)")
        print("\nExample (PowerShell):")
        print('  $env:OPENAI_API_KEY="sk-..."')
        print("\nSee docs/llm-setup-guide.md for detailed instructions.")
    else:
        print("[OK] At least one API key is configured!")
        print("You can now run: python scripts/test_var_lens_with_llm.py")
    
    return has_key

if __name__ == "__main__":
    check_api_keys()

# Made with Bob
