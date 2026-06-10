"""
Build VAR-Lens Vector Store
============================

This script builds the FAISS vector store for the VAR-Lens agent
from processed FIFA/IFAB documents.

Usage:
    python scripts/build_var_lens_vectorstore.py [--rebuild]

Options:
    --rebuild: Force rebuild even if vector store exists
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.var_lens.rag_engine import VARLensRAG


def main():
    """
    Main function to build vector store.
    """
    parser = argparse.ArgumentParser(
        description="Build VAR-Lens vector store from processed documents"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild even if vector store exists"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VAR-Lens Vector Store Builder")
    print("=" * 70)
    print()
    
    # Initialize RAG engine
    print("Initializing VAR-Lens RAG engine...")
    rag = VARLensRAG()
    
    # Setup (build or load)
    print()
    if args.rebuild:
        print("Force rebuild requested...")
    
    rag.setup(force_rebuild=args.rebuild)
    
    # Print statistics
    print()
    print("=" * 70)
    print("Vector Store Statistics")
    print("=" * 70)
    
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key:.<50} {value}")
    
    print()
    print("=" * 70)
    print("✅ Vector store is ready!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Test with: python scripts/test_var_lens_rag.py")
    print("  2. Use in Langflow or FastAPI")
    print()


if __name__ == "__main__":
    main()

# Made with Bob
