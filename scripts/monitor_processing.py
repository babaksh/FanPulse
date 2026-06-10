"""
Monitor PDF processing progress
"""

import time
from pathlib import Path
import json

def monitor_processing():
    """Monitor the processing of PDF files"""
    
    raw_docs_dir = Path("data/raw_documents")
    processed_docs_dir = Path("data/processed_documents")
    
    # Get list of PDF files to process
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    total_pdfs = len(pdf_files)
    
    print("=" * 70)
    print("PDF PROCESSING MONITOR")
    print("=" * 70)
    print(f"\nTotal PDFs to process: {total_pdfs}")
    print(f"Source directory: {raw_docs_dir}")
    print(f"Output directory: {processed_docs_dir}")
    print("\n" + "=" * 70)
    
    # List all PDFs
    print("\nPDF Files:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name}")
    
    print("\n" + "=" * 70)
    print("PROCESSING STATUS")
    print("=" * 70)
    
    # Check which files have been processed
    processed_files = list(processed_docs_dir.glob("*.md"))
    processed_count = len(processed_files)
    
    print(f"\nProcessed: {processed_count}/{total_pdfs}")
    print(f"Remaining: {total_pdfs - processed_count}")
    print(f"Progress: {(processed_count/total_pdfs)*100:.1f}%")
    
    if processed_files:
        print("\nCompleted Files:")
        for md_file in processed_files:
            size_kb = md_file.stat().st_size / 1024
            print(f"  - {md_file.name} ({size_kb:.1f} KB)")
    
    # Check for processing summary
    summary_file = processed_docs_dir / "processing_summary.json"
    if summary_file.exists():
        print("\nProcessing Summary:")
        summary = json.loads(summary_file.read_text(encoding='utf-8'))
        print(f"  - Processed at: {summary.get('processed_at', 'N/A')}")
        print(f"  - Successful: {summary.get('successful', 0)}")
        print(f"  - Failed: {summary.get('failed', 0)}")
    
    print("\n" + "=" * 70)
    
    # Show which PDFs are pending
    processed_names = {f.stem for f in processed_files}
    pending_pdfs = [pdf for pdf in pdf_files if pdf.stem not in processed_names]
    
    if pending_pdfs:
        print("\nPending Files:")
        for pdf in pending_pdfs:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  - {pdf.name} ({size_mb:.1f} MB)")
    else:
        print("\nAll PDFs have been processed!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    monitor_processing()

# Made with Bob
