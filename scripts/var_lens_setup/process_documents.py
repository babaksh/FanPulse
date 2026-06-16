#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process FIFA/IFAB Documents with Docling
=========================================

This script processes PDF documents using IBM Docling and converts them to Markdown
for use in the VAR-Lens RAG system.

Usage:
    # Process all PDFs in raw_documents/
    python scripts/process_documents.py
    
    # Process specific PDF
    python scripts/process_documents.py --file "Laws of the Game 2026_27.pdf"
    
    # Force reprocess all (skip existing check)
    python scripts/process_documents.py --force
    
    # Set max file size (in MB)
    python scripts/process_documents.py --max-size 10

Requirements:
    pip install docling
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Check if docling is installed
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️  Warning: Docling not installed")
    print("   Install with: pip install docling")


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DOCS_PATH = PROJECT_ROOT / "data" / "raw_documents"
PROCESSED_DOCS_PATH = PROJECT_ROOT / "data" / "processed_documents"
SUMMARY_PATH = PROCESSED_DOCS_PATH / "processing_summary.json"


class DocumentProcessor:
    """Process PDF documents with IBM Docling"""
    
    def __init__(self, max_file_size_mb: float = 5.0, force: bool = False):
        """
        Initialize document processor.
        
        Args:
            max_file_size_mb: Maximum file size to process (in MB)
            force: Force reprocess even if output exists
        """
        self.max_file_size_mb = max_file_size_mb
        self.force = force
        self.converter = None
        
        # Create directories if they don't exist
        RAW_DOCS_PATH.mkdir(parents=True, exist_ok=True)
        PROCESSED_DOCS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docling converter
        if DOCLING_AVAILABLE:
            try:
                self.converter = DocumentConverter()
                print("✅ Docling converter initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Docling: {e}")
                self.converter = None
        else:
            print("❌ Docling not available - install with: pip install docling")
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB"""
        return file_path.stat().st_size / (1024 * 1024)
    
    def should_process(self, pdf_path: Path) -> tuple[bool, Optional[str]]:
        """
        Check if file should be processed.
        
        Returns:
            (should_process, reason)
        """
        # Check file size
        size_mb = self.get_file_size_mb(pdf_path)
        if size_mb > self.max_file_size_mb:
            return False, f"file_too_large (size: {size_mb:.2f} MB, max: {self.max_file_size_mb} MB)"
        
        # Check if already processed (unless force)
        output_path = PROCESSED_DOCS_PATH / f"{pdf_path.stem}.md"
        if output_path.exists() and not self.force:
            return False, "already_processed"
        
        return True, None
    
    def process_pdf(self, pdf_path: Path) -> Dict:
        """
        Process a single PDF file with Docling.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Processing result dictionary
        """
        result = {
            "filename": pdf_path.name,
            "status": "pending",
            "size_mb": self.get_file_size_mb(pdf_path)
        }
        
        # Check if should process
        should_process, reason = self.should_process(pdf_path)
        if not should_process:
            result["status"] = "skipped"
            result["reason"] = reason
            return result
        
        # Check if Docling is available
        if not self.converter:
            result["status"] = "failed"
            result["error"] = "Docling not available"
            return result
        
        try:
            print(f"\n📄 Processing: {pdf_path.name}")
            print(f"   Size: {result['size_mb']:.2f} MB")
            
            # Convert PDF to Markdown
            conversion_result = self.converter.convert(str(pdf_path))
            
            # Get markdown content
            markdown_content = conversion_result.document.export_to_markdown()
            
            # Save to file
            output_path = PROCESSED_DOCS_PATH / f"{pdf_path.stem}.md"
            output_path.write_text(markdown_content, encoding='utf-8')
            
            # Update result
            result["status"] = "success"
            result["pages"] = len(conversion_result.document.pages) if hasattr(conversion_result.document, 'pages') else None
            result["characters"] = len(markdown_content)
            result["output_file"] = output_path.name
            
            print(f"   ✅ Success!")
            print(f"   Pages: {result['pages']}")
            print(f"   Characters: {result['characters']:,}")
            print(f"   Output: {output_path.name}")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"   ❌ Failed: {e}")
        
        return result
    
    def process_all(self, specific_file: Optional[str] = None) -> Dict:
        """
        Process all PDF files in raw_documents directory.
        
        Args:
            specific_file: Process only this specific file (optional)
            
        Returns:
            Summary dictionary
        """
        print("=" * 70)
        print("📚 FIFA/IFAB Document Processor with IBM Docling")
        print("=" * 70)
        print()
        print(f"📁 Raw documents: {RAW_DOCS_PATH}")
        print(f"📁 Processed documents: {PROCESSED_DOCS_PATH}")
        print(f"📏 Max file size: {self.max_file_size_mb} MB")
        print(f"🔄 Force reprocess: {self.force}")
        print()
        
        # Get PDF files
        if specific_file:
            pdf_files = [RAW_DOCS_PATH / specific_file]
            if not pdf_files[0].exists():
                print(f"❌ File not found: {specific_file}")
                return {}
        else:
            pdf_files = sorted(RAW_DOCS_PATH.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in raw_documents/")
            return {}
        
        print(f"📋 Found {len(pdf_files)} PDF file(s)")
        print()
        
        # Process each file
        results = []
        for pdf_path in pdf_files:
            result = self.process_pdf(pdf_path)
            results.append(result)
        
        # Create summary
        summary = {
            "processed_at": datetime.now().isoformat(),
            "total_files": len(results),
            "processed": sum(1 for r in results if r["status"] == "success"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "max_file_size_mb": self.max_file_size_mb,
            "results": results
        }
        
        # Save summary
        with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print()
        print("=" * 70)
        print("📊 Processing Summary")
        print("=" * 70)
        print(f"  Total files: {summary['total_files']}")
        print(f"  ✅ Processed: {summary['processed']}")
        print(f"  ⏭️  Skipped: {summary['skipped']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print()
        print(f"📄 Summary saved to: {SUMMARY_PATH}")
        print()
        
        # Show details
        if summary['processed'] > 0:
            print("✅ Successfully processed:")
            for r in results:
                if r["status"] == "success":
                    print(f"   - {r['filename']} → {r['output_file']}")
        
        if summary['skipped'] > 0:
            print()
            print("⏭️  Skipped files:")
            for r in results:
                if r["status"] == "skipped":
                    print(f"   - {r['filename']} ({r['reason']})")
        
        if summary['failed'] > 0:
            print()
            print("❌ Failed files:")
            for r in results:
                if r["status"] == "failed":
                    print(f"   - {r['filename']}: {r.get('error', 'Unknown error')}")
        
        print()
        print("=" * 70)
        print("Next steps:")
        print("  1. Review processed Markdown files in data/processed_documents/")
        print("  2. Rebuild vector store: python scripts/build_var_lens_vectorstore.py --rebuild")
        print("=" * 70)
        print()
        
        return summary


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Process FIFA/IFAB PDF documents with IBM Docling"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Process specific file only (e.g., 'Laws of the Game 2026_27.pdf')"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocess even if output exists"
    )
    parser.add_argument(
        "--max-size",
        type=float,
        default=5.0,
        help="Maximum file size in MB (default: 5.0)"
    )
    
    args = parser.parse_args()
    
    # Check if Docling is available
    if not DOCLING_AVAILABLE:
        print()
        print("=" * 70)
        print("❌ ERROR: Docling is not installed")
        print("=" * 70)
        print()
        print("To install Docling:")
        print("  pip install docling")
        print()
        print("Or install all requirements:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)
    
    # Create processor and run
    processor = DocumentProcessor(
        max_file_size_mb=args.max_size,
        force=args.force
    )
    
    processor.process_all(specific_file=args.file)


if __name__ == "__main__":
    main()

# Made with Bob