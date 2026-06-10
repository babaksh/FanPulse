"""
Process the large Laws of the Game PDF by splitting it into chunks
"""

from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import json
from datetime import datetime
import PyPDF2

def split_pdf(input_pdf, output_dir, pages_per_chunk=20):
    """Split a large PDF into smaller chunks"""
    
    print(f"Splitting {input_pdf.name} into chunks...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the PDF
    with open(input_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        
        print(f"Total pages: {total_pages}")
        print(f"Pages per chunk: {pages_per_chunk}")
        
        chunks = []
        chunk_num = 0
        
        # Split into chunks
        for start_page in range(0, total_pages, pages_per_chunk):
            end_page = min(start_page + pages_per_chunk, total_pages)
            chunk_num += 1
            
            # Create a new PDF for this chunk
            pdf_writer = PyPDF2.PdfWriter()
            
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            # Save chunk
            chunk_filename = f"{input_pdf.stem}_chunk_{chunk_num:03d}.pdf"
            chunk_path = output_dir / chunk_filename
            
            with open(chunk_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            chunks.append({
                'filename': chunk_filename,
                'path': chunk_path,
                'start_page': start_page + 1,
                'end_page': end_page,
                'num_pages': end_page - start_page
            })
            
            print(f"  Created chunk {chunk_num}: pages {start_page + 1}-{end_page}")
    
    print(f"\nCreated {len(chunks)} chunks")
    return chunks

def process_chunks(chunks, output_dir):
    """Process each PDF chunk"""
    
    print("\nProcessing chunks...")
    
    # Configure pipeline
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.images_scale = 1.0
    pipeline_options.generate_page_images = False
    
    # Initialize converter
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend
            )
        }
    )
    
    results = []
    all_markdown = []
    
    for i, chunk_info in enumerate(chunks, 1):
        print(f"\n[{i}/{len(chunks)}] Processing {chunk_info['filename']}...")
        
        try:
            # Convert chunk
            result = converter.convert(str(chunk_info['path']))
            markdown_content = result.document.export_to_markdown()
            
            # Add section header
            section_header = f"\n\n<!-- Pages {chunk_info['start_page']}-{chunk_info['end_page']} -->\n\n"
            all_markdown.append(section_header + markdown_content)
            
            print(f"  SUCCESS - {len(markdown_content):,} characters")
            
            results.append({
                'chunk': chunk_info['filename'],
                'status': 'success',
                'pages': chunk_info['num_pages'],
                'characters': len(markdown_content)
            })
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results.append({
                'chunk': chunk_info['filename'],
                'status': 'error',
                'error': str(e)
            })
    
    # Combine all markdown
    combined_markdown = "\n".join(all_markdown)
    
    # Save combined markdown
    output_file = output_dir / "Laws of the Game 2026_27.md"
    output_file.write_text(combined_markdown, encoding='utf-8')
    
    print(f"\n✓ Combined markdown saved: {output_file}")
    print(f"  Total characters: {len(combined_markdown):,}")
    
    return results, combined_markdown

def process_large_pdf():
    """Main function to process the large PDF"""
    
    print("=" * 70)
    print("PROCESSING LARGE PDF: Laws of the Game 2026_27.pdf")
    print("=" * 70)
    
    # Paths
    input_pdf = Path("data/raw_documents/Laws of the Game 2026_27.pdf")
    temp_dir = Path("data/temp_chunks")
    output_dir = Path("data/processed_documents")
    
    if not input_pdf.exists():
        print(f"ERROR: PDF not found at {input_pdf}")
        return
    
    # Get file size
    size_mb = input_pdf.stat().st_size / (1024 * 1024)
    print(f"\nFile size: {size_mb:.1f} MB")
    
    try:
        # Step 1: Split PDF into chunks
        print("\nSTEP 1: Splitting PDF into chunks")
        print("-" * 70)
        chunks = split_pdf(input_pdf, temp_dir, pages_per_chunk=20)
        
        # Step 2: Process each chunk
        print("\nSTEP 2: Processing chunks with Docling")
        print("-" * 70)
        results, combined_markdown = process_chunks(chunks, output_dir)
        
        # Step 3: Save summary
        summary = {
            'processed_at': datetime.now().isoformat(),
            'input_file': input_pdf.name,
            'file_size_mb': size_mb,
            'total_chunks': len(chunks),
            'successful_chunks': sum(1 for r in results if r['status'] == 'success'),
            'failed_chunks': sum(1 for r in results if r['status'] == 'error'),
            'total_characters': len(combined_markdown),
            'chunks': results
        }
        
        summary_file = output_dir / "large_pdf_processing_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        
        # Step 4: Cleanup temp files
        print("\nSTEP 3: Cleaning up temporary files")
        print("-" * 70)
        for chunk_info in chunks:
            chunk_info['path'].unlink()
        temp_dir.rmdir()
        print("✓ Temporary files removed")
        
        # Final summary
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Input: {input_pdf.name} ({size_mb:.1f} MB)")
        print(f"Output: Laws of the Game 2026_27.md")
        print(f"Chunks processed: {summary['successful_chunks']}/{summary['total_chunks']}")
        print(f"Total characters: {summary['total_characters']:,}")
        print(f"Summary: {summary_file}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    process_large_pdf()

# Made with Bob
