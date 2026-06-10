"""
Docling Test Script
Convert a sample PDF to Markdown
"""

from docling.document_converter import DocumentConverter
from pathlib import Path
import sys

def test_docling():
    """Simple Docling test"""
    
    print("Starting Docling test...")
    print("-" * 50)
    
    try:
        # Initialize converter
        print("Initializing Docling...")
        converter = DocumentConverter()
        print("Docling is ready!")
        
        # Check for sample file
        sample_pdf = Path("data/raw_documents/sample.pdf")
        
        if not sample_pdf.exists():
            print("\nSample file not found!")
            print(f"Please place a sample PDF at:")
            print(f"  {sample_pdf.absolute()}")
            print("\nYou can use any simple PDF for testing.")
            return False
            
        print(f"\nProcessing: {sample_pdf.name}")
        
        # Convert PDF to Docling Document
        result = converter.convert(str(sample_pdf))
        doc = result.document
        
        print("PDF processed successfully!")
        
        # Export to Markdown
        markdown_content = doc.export_to_markdown()
        
        # Save Markdown
        output_path = Path("data/processed_documents/sample.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Markdown saved: {output_path}")
        
        # Display summary
        print("\nSummary:")
        print(f"  - Content length: {len(markdown_content)} characters")
        print(f"  - Number of lines: {len(markdown_content.splitlines())}")
        
        # Display first 10 lines
        print("\nFirst 10 lines of Markdown:")
        print("-" * 50)
        lines = markdown_content.splitlines()[:10]
        for line in lines:
            print(line)
        print("-" * 50)
        
        print("\nDocling test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"\nError: Docling is not installed!")
        print(f"Please install with:")
        print(f"  pip install docling")
        return False
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_docling()
    sys.exit(0 if success else 1)

# Made with Bob
