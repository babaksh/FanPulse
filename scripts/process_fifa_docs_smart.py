"""
Smart FIFA Documents Processing Script
Skips very large PDFs and processes smaller ones first
"""

from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import json
from datetime import datetime

# Maximum file size to process (in MB)
MAX_FILE_SIZE_MB = 5.0

def process_fifa_documents_smart():
    """Process FIFA PDF documents, skipping very large files"""
    
    print("Starting SMART FIFA documents processing...")
    print("=" * 60)
    print(f"Max file size: {MAX_FILE_SIZE_MB} MB")
    print("=" * 60)
    
    # Define paths
    raw_docs_dir = Path("data/raw_documents")
    processed_docs_dir = Path("data/processed_documents")
    processed_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure pipeline for lower memory usage
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.images_scale = 1.0
    pipeline_options.generate_page_images = False
    
    # Initialize converter
    print("\nInitializing Docling converter...")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend
            )
        }
    )
    print("Converter ready!")
    
    # Get all PDF files and sort by size
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    pdf_files_with_size = [(pdf, pdf.stat().st_size / (1024 * 1024)) for pdf in pdf_files]
    pdf_files_with_size.sort(key=lambda x: x[1])  # Sort by size (smallest first)
    
    print(f"\nFound {len(pdf_files)} PDF file(s)")
    print("\nFile sizes:")
    for pdf, size_mb in pdf_files_with_size:
        status = "WILL PROCESS" if size_mb <= MAX_FILE_SIZE_MB else "SKIP (too large)"
        print(f"  - {pdf.name}: {size_mb:.1f} MB [{status}]")
    
    # Filter files to process
    files_to_process = [(pdf, size) for pdf, size in pdf_files_with_size if size <= MAX_FILE_SIZE_MB]
    files_to_skip = [(pdf, size) for pdf, size in pdf_files_with_size if size > MAX_FILE_SIZE_MB]
    
    print(f"\nWill process: {len(files_to_process)} files")
    print(f"Will skip: {len(files_to_skip)} files")
    print()
    
    # Track processing results
    results = []
    
    # Process each PDF
    for pdf_file, size_mb in files_to_process:
        # Check if already processed
        output_file = processed_docs_dir / f"{pdf_file.stem}.md"
        if output_file.exists():
            print("=" * 60)
            print(f"SKIPPING (already processed): {pdf_file.name}")
            print("=" * 60)
            results.append({
                "filename": pdf_file.name,
                "status": "skipped",
                "reason": "already_processed"
            })
            continue
        
        print("=" * 60)
        print(f"Processing: {pdf_file.name} ({size_mb:.1f} MB)")
        print("=" * 60)
        
        try:
            # Convert PDF to markdown
            print("Converting PDF...")
            result = converter.convert(str(pdf_file))
            
            # Export to markdown
            markdown_content = result.document.export_to_markdown()
            
            # Save markdown file
            output_file.write_text(markdown_content, encoding='utf-8')
            
            # Get statistics
            num_pages = len(result.document.pages)
            num_chars = len(markdown_content)
            
            print(f"SUCCESS!")
            print(f"  - Pages: {num_pages}")
            print(f"  - Characters: {num_chars:,}")
            print(f"  - Output: {output_file.name}")
            
            # Track result
            results.append({
                "filename": pdf_file.name,
                "status": "success",
                "pages": num_pages,
                "characters": num_chars,
                "output_file": output_file.name,
                "size_mb": size_mb
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                "filename": pdf_file.name,
                "status": "error",
                "error": str(e),
                "size_mb": size_mb
            })
        
        print()
    
    # Add skipped files to results
    for pdf_file, size_mb in files_to_skip:
        results.append({
            "filename": pdf_file.name,
            "status": "skipped",
            "reason": "file_too_large",
            "size_mb": size_mb
        })
    
    # Save processing summary
    summary = {
        "processed_at": datetime.now().isoformat(),
        "total_files": len(pdf_files),
        "processed": sum(1 for r in results if r["status"] == "success"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "max_file_size_mb": MAX_FILE_SIZE_MB,
        "results": results
    }
    
    summary_file = processed_docs_dir / "processing_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    
    # Print final summary
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total files: {summary['total_files']}")
    print(f"Processed: {summary['processed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nProcessed documents saved to: {processed_docs_dir}")
    print(f"Summary saved to: {summary_file}")
    
    if files_to_skip:
        print(f"\nNOTE: {len(files_to_skip)} large file(s) were skipped:")
        for pdf, size in files_to_skip:
            print(f"  - {pdf.name} ({size:.1f} MB)")
        print("\nTo process these files, you may need:")
        print("  1. More RAM")
        print("  2. Cloud processing")
        print("  3. Split the PDF into smaller parts")
    
    print("=" * 60)

if __name__ == "__main__":
    process_fifa_documents_smart()

# Made with Bob
