"""
Process only the VAR Protocol PDF - the most important document for VAR-Lens Agent
"""

from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import json
from datetime import datetime

def process_var_protocol():
    """Process only the VAR Protocol PDF"""
    
    print("Processing VAR Protocol PDF...")
    print("=" * 60)
    
    # Define paths
    raw_docs_dir = Path("data/raw_documents")
    processed_docs_dir = Path("data/processed_documents")
    processed_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find VAR Protocol PDF
    var_pdf = raw_docs_dir / "Video Assistant Referee (VAR) protocol _ IFAB.pdf"
    
    if not var_pdf.exists():
        print(f"ERROR: VAR Protocol PDF not found at {var_pdf}")
        return
    
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
    
    try:
        # Convert PDF
        print(f"\nConverting: {var_pdf.name}")
        result = converter.convert(str(var_pdf))
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Save markdown file
        output_file = processed_docs_dir / f"{var_pdf.stem}.md"
        output_file.write_text(markdown_content, encoding='utf-8')
        
        # Get statistics
        num_pages = len(result.document.pages)
        num_chars = len(markdown_content)
        
        print(f"\n✓ Successfully processed!")
        print(f"  - Pages: {num_pages}")
        print(f"  - Characters: {num_chars:,}")
        print(f"  - Output: {output_file}")
        
        # Save metadata
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "filename": var_pdf.name,
            "pages": num_pages,
            "characters": num_chars,
            "output_file": str(output_file)
        }
        
        metadata_file = processed_docs_dir / "var_protocol_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        print(f"\nMetadata saved to: {metadata_file}")
        print("=" * 60)
        print("VAR Protocol processing complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    process_var_protocol()

# Made with Bob
