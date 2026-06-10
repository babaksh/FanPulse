"""
Optimized FIFA Documents Processing Script
Uses SimplePdfPipeline for lower memory usage
"""

from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import json
from datetime import datetime

def process_fifa_documents():
    """Process FIFA PDF documents with optimized settings"""
    
    print("Starting FIFA documents processing (Optimized)...")
    print("=" * 60)
    
    # Define paths
    raw_docs_dir = Path("data/raw_documents")
    processed_docs_dir = Path("data/processed_documents")
    processed_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure pipeline for lower memory usage
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Disable OCR since PDFs are text-based
    pipeline_options.do_table_structure = True  # Keep table detection
    pipeline_options.images_scale = 1.0  # Don't scale images
    pipeline_options.generate_page_images = False  # Don't generate page images
    
    # Initialize converter with optimized settings
    print("\nInitializing Docling converter with optimized settings...")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend  # Lighter backend
            )
        }
    )
    print("Converter ready!")
    
    # Get all PDF files
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDF file(s) to process\n")
    
    # Track processing results
    results = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        print("=" * 60)
        print(f"Processing: {pdf_file.name}")
        print("=" * 60)
        
        try:
            # Convert PDF to markdown
            print("Converting PDF...")
            result = converter.convert(str(pdf_file))
            
            # Export to markdown
            markdown_content = result.document.export_to_markdown()
            
            # Save markdown file
            output_file = processed_docs_dir / f"{pdf_file.stem}.md"
            output_file.write_text(markdown_content, encoding='utf-8')
            
            # Get statistics
            num_pages = len(result.document.pages)
            num_chars = len(markdown_content)
            
            print(f"✓ Successfully processed!")
            print(f"  - Pages: {num_pages}")
            print(f"  - Characters: {num_chars:,}")
            print(f"  - Output: {output_file.name}")
            
            # Track result
            results.append({
                "filename": pdf_file.name,
                "status": "success",
                "pages": num_pages,
                "characters": num_chars,
                "output_file": output_file.name
            })
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {str(e)}")
            results.append({
                "filename": pdf_file.name,
                "status": "error",
                "error": str(e)
            })
        
        print()
    
    # Save processing summary
    summary = {
        "processed_at": datetime.now().isoformat(),
        "total_files": len(pdf_files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }
    
    summary_file = processed_docs_dir / "processing_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    
    # Print final summary
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total files: {summary['total_files']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nProcessed documents saved to: {processed_docs_dir}")
    print(f"Summary saved to: {summary_file}")
    print("=" * 60)

if __name__ == "__main__":
    process_fifa_documents()

# Made with Bob
