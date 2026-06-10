"""
FIFA Documents Processing Script
Process FIFA rulebooks and VAR guidelines using Docling
"""

from docling.document_converter import DocumentConverter
from pathlib import Path
import sys
import json

def process_fifa_documents():
    """Process FIFA documents and convert to Markdown"""
    
    print("Starting FIFA documents processing...")
    print("=" * 60)
    
    # Initialize Docling converter
    print("\nInitializing Docling converter...")
    converter = DocumentConverter()
    print("Converter ready!")
    
    # Define input and output directories
    input_dir = Path("data/raw_documents")
    output_dir = Path("data/processed_documents")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Look for PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\nNo PDF files found in {input_dir}")
        print("\nTo use this script:")
        print("1. Download FIFA Laws of the Game PDF")
        print("2. Download VAR Protocol PDF")
        print(f"3. Place them in: {input_dir.absolute()}")
        return False
    
    print(f"\nFound {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF
    results = []
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*60}")
        
        try:
            # Convert PDF to Docling Document
            print("Converting PDF...")
            result = converter.convert(str(pdf_file))
            doc = result.document
            
            # Export to Markdown
            print("Exporting to Markdown...")
            markdown_content = doc.export_to_markdown()
            
            # Save Markdown
            output_file = output_dir / f"{pdf_file.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Saved: {output_file.name}")
            print(f"  - Size: {len(markdown_content):,} characters")
            print(f"  - Lines: {len(markdown_content.splitlines()):,}")
            
            # Save metadata
            metadata = {
                "source_file": pdf_file.name,
                "output_file": output_file.name,
                "size_chars": len(markdown_content),
                "num_lines": len(markdown_content.splitlines()),
                "processed": True
            }
            results.append(metadata)
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
            results.append({
                "source_file": pdf_file.name,
                "error": str(e),
                "processed": False
            })
    
    # Save processing summary
    summary_file = output_dir / "processing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Processing Summary")
    print(f"{'='*60}")
    print(f"Total files: {len(pdf_files)}")
    print(f"Successful: {sum(1 for r in results if r.get('processed', False))}")
    print(f"Failed: {sum(1 for r in results if not r.get('processed', False))}")
    print(f"\nSummary saved to: {summary_file}")
    
    return True


if __name__ == "__main__":
    success = process_fifa_documents()
    sys.exit(0 if success else 1)

# Made with Bob