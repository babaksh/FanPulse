"""
Check setup and installed tools
"""

import sys
from pathlib import Path

def check_imports():
    """Check required imports"""
    
    print("Checking installed tools...")
    print("=" * 60)
    
    results = {}
    
    # Check Docling
    try:
        import docling
        results['docling'] = 'OK - Installed'
    except ImportError:
        results['docling'] = 'MISSING - pip install docling'
    
    # Check Langflow
    try:
        import langflow
        results['langflow'] = 'OK - Installed'
    except ImportError:
        results['langflow'] = 'MISSING - pip install langflow'
    
    # Check FastAPI
    try:
        import fastapi
        results['fastapi'] = 'OK - Installed'
    except ImportError:
        results['fastapi'] = 'MISSING - pip install fastapi'
    
    # Check LangChain
    try:
        import langchain
        results['langchain'] = 'OK - Installed'
    except ImportError:
        results['langchain'] = 'MISSING - pip install langchain'
    
    # Display results
    print("\nTools Status:")
    print("-" * 60)
    for tool, status in results.items():
        print(f"  {tool:20} {status}")
    
    # Check Langflow server
    print("\nChecking Langflow Server:")
    print("-" * 60)
    try:
        import requests
        response = requests.get("http://localhost:7860/health", timeout=2)
        if response.status_code == 200:
            print("  OK - Langflow is running (localhost:7860)")
        else:
            print("  WARNING - Langflow not responding")
    except:
        print("  ERROR - Langflow is not running")
        print("     Please start Langflow")
    
    # Check directory structure
    print("\nChecking Project Structure:")
    print("-" * 60)
    
    required_dirs = [
        "data/raw_documents",
        "data/processed_documents",
        "data/match_data",
        "src/agents",
        "src/services",
        "scripts"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  OK - {dir_path}")
        else:
            print(f"  MISSING - {dir_path}")
    
    print("\n" + "=" * 60)
    
    # Summary
    missing = [k for k, v in results.items() if 'MISSING' in v]
    if missing:
        print(f"\nWARNING: {len(missing)} tools not installed:")
        print("\nTo install all:")
        print("  pip install -r requirements.txt")
    else:
        print("\nSUCCESS: All tools are installed!")
    
    return len(missing) == 0


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)

# Made with Bob
