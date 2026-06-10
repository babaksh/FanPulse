# Document Processing Workflow with Docling

## 🎯 Goal

Convert all documents (FIFA rules, documentations, etc.) into standardized Markdown format using Docling, for use in agents and Langflow.

---

## 📋 Processing Process

### Step 1: Document Collection

```
data/raw_documents/
├── fifa_rules/
│   ├── laws_of_the_game_2026.pdf
│   ├── var_protocol_2026.pdf
│   └── ifab_guidelines.pdf
├── tournament_docs/
│   └── world_cup_regulations.pdf
└── other/
    └── referee_handbook.pdf
```

### Step 2: Processing with Docling

```python
from docling.document_converter import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Process each document
for pdf_file in pdf_files:
    # Convert to Docling Document
    result = converter.convert(pdf_file)
    doc = result.document
    
    # Export to Markdown
    markdown_content = doc.export_to_markdown()
    
    # Save processed markdown
    save_markdown(markdown_content, output_path)
```

### Step 3: Output Structure

```
data/processed_documents/
├── fifa_rules/
│   ├── laws_of_the_game_2026.md
│   ├── var_protocol_2026.md
│   └── ifab_guidelines.md
├── tournament_docs/
│   └── world_cup_regulations.md
└── metadata/
    └── document_index.json
```

---

## 🔧 Processing Script

### `scripts/process_documents.py`

```python
"""
Document processing script with Docling
Convert all PDFs to standardized Markdown
"""

import os
import json
from pathlib import Path
from docling.document_converter import DocumentConverter
from typing import Dict, List

class DocumentProcessor:
    def __init__(self, raw_dir: str, processed_dir: str):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.converter = DocumentConverter()
        self.metadata = []
        
    def process_all_documents(self):
        """Process all documents in raw directory"""
        
        print("🚀 Starting document processing with Docling...")
        
        # Find all PDF files
        pdf_files = list(self.raw_dir.rglob("*.pdf"))
        
        print(f"📄 {len(pdf_files)} PDF files found")
        
        for pdf_file in pdf_files:
            self.process_single_document(pdf_file)
            
        # Save metadata
        self.save_metadata()
        
        print("✅ All documents processed successfully!")
        
    def process_single_document(self, pdf_path: Path):
        """Process a single document"""
        
        print(f"\n📖 Processing: {pdf_path.name}")
        
        try:
            # Convert PDF to Docling Document
            result = self.converter.convert(str(pdf_path))
            doc = result.document
            
            # Extract information
            markdown_content = doc.export_to_markdown()
            
            # Create output path
            relative_path = pdf_path.relative_to(self.raw_dir)
            output_path = self.processed_dir / relative_path.with_suffix('.md')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save Markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            # Save metadata
            metadata = {
                "source_file": str(pdf_path),
                "output_file": str(output_path),
                "title": self.extract_title(doc),
                "page_count": len(doc.pages) if hasattr(doc, 'pages') else 0,
                "tables_count": len(doc.tables) if hasattr(doc, 'tables') else 0,
                "processed_date": str(Path(output_path).stat().st_mtime)
            }
            
            self.metadata.append(metadata)
            
            print(f"   ✓ Saved: {output_path}")
            print(f"   ✓ Pages: {metadata['page_count']}")
            print(f"   ✓ Tables: {metadata['tables_count']}")
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            
    def extract_title(self, doc) -> str:
        """Extract document title"""
        # Attempt to find the first header
        if hasattr(doc, 'texts'):
            for text in doc.texts[:5]:  # Check the first 5 text blocks
                if len(text.strip()) > 0 and len(text.strip()) < 100:
                    return text.strip()
        return "Untitled Document"
        
    def save_metadata(self):
        """Save metadata of all documents"""
        metadata_path = self.processed_dir / "metadata" / "document_index.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Metadata saved: {metadata_path}")


def main():
    """Main function"""
    
    # Paths
    raw_dir = "data/raw_documents"
    processed_dir = "data/processed_documents"
    
    # Build processor
    processor = DocumentProcessor(raw_dir, processed_dir)
    
    # Process all documents
    processor.process_all_documents()


if __name__ == "__main__":
    main()
```

---

## 🎯 Usage in VAR-Lens Agent

### Step 1: Loading Processed Markdowns

```python
# src/agents/var_lens/document_loader.py

from pathlib import Path
from typing import List, Dict
import json

class ProcessedDocumentLoader:
    """Loading documents processed with Docling"""
    
    def __init__(self, processed_dir: str):
        self.processed_dir = Path(processed_dir)
        self.documents = {}
        self.load_all_documents()
        
    def load_all_documents(self):
        """Load all Markdowns"""
        
        # Read metadata
        metadata_path = self.processed_dir / "metadata" / "document_index.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        # Load each document
        for doc_meta in metadata:
            output_file = Path(doc_meta['output_file'])
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.documents[doc_meta['title']] = {
                'content': content,
                'metadata': doc_meta
            }
            
    def search_in_documents(self, query: str) -> List[Dict]:
        """Search in documents"""
        results = []
        
        for title, doc in self.documents.items():
            if query.lower() in doc['content'].lower():
                # Find relevant section
                lines = doc['content'].split('\n')
                relevant_lines = [
                    line for line in lines 
                    if query.lower() in line.lower()
                ]
                
                results.append({
                    'title': title,
                    'relevant_content': '\n'.join(relevant_lines[:5]),
                    'metadata': doc['metadata']
                })
                
        return results
```

### Step 2: Usage in RAG Pipeline

```python
# src/agents/var_lens/rag_pipeline.py

from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class VARLensRAG:
    """RAG Pipeline for VAR-Lens using Docling Markdowns"""
    
    def __init__(self, processed_docs_dir: str):
        self.doc_loader = ProcessedDocumentLoader(processed_docs_dir)
        self.setup_rag()
        
    def setup_rag(self):
        """Set up RAG pipeline"""
        
        # Text splitter for Markdown
        self.text_splitter = MarkdownTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Build vector store from Markdowns
        all_chunks = []
        for title, doc in self.doc_loader.documents.items():
            chunks = self.text_splitter.split_text(doc['content'])
            all_chunks.extend(chunks)
            
        self.vectorstore = FAISS.from_texts(
            all_chunks,
            self.embeddings
        )
        
    def retrieve_relevant_rules(self, query: str, k: int = 3):
        """Retrieve relevant rules"""
        
        # Semantic search
        docs = self.vectorstore.similarity_search(query, k=k)
        
        return [doc.page_content for doc in docs]
```

---

## 🔄 Usage in Langflow

### Component for Docling Processed Documents

```python
# For use in Langflow
from langflow import CustomComponent
from langflow.field_typing import Text

class DoclingDocumentRetriever(CustomComponent):
    display_name = "Docling Document Retriever"
    description = "Retrieval of documents processed with Docling"
    
    def build_config(self):
        return {
            "processed_docs_dir": {
                "display_name": "Processed Documents Directory",
                "info": "Directory path of processed documents"
            },
            "query": {
                "display_name": "Query",
                "info": "Search text"
            }
        }
        
    def build(self, processed_docs_dir: str, query: str) -> Text:
        loader = ProcessedDocumentLoader(processed_docs_dir)
        results = loader.search_in_documents(query)
        
        # Format results
        formatted_results = "\n\n".join([
            f"📄 {r['title']}\n{r['relevant_content']}"
            for r in results
        ])
        
        return formatted_results
```

---

## ✅ Document Processing Checklist

### Before Starting
- [ ] Install Docling: `pip install docling`
- [ ] Download FIFA/IFAB documents
- [ ] Create directory structure

### Processing
- [ ] Run `scripts/process_documents.py`
- [ ] Check output Markdowns
- [ ] Check metadata

### Integration
- [ ] Test document loader
- [ ] Test RAG pipeline
- [ ] Test in Langflow

---

## 📊 Docling Output Example

### Input (PDF):
```
[Complex PDF with tables, figures, etc.]
```

### Output (Markdown):
```markdown
# Laws of the Game 2026

## Law 11 - Offside

### Offside Position

A player is in an offside position if:
- any part of the head, body or feet is in the opponents' half
- any part of the head, body or feet is nearer to the opponents' goal line than both the ball and the second-last opponent

### Offside Offence

A player in an offside position at the moment the ball is played or touched by a team-mate is only penalised on becoming involved in active play by:
- interfering with play
- interfering with an opponent
- gaining an advantage

| Situation | Offside? |
|-----------|----------|
| Player receives ball directly from goal kick | No |
| Player receives ball directly from throw-in | No |
| Player receives ball directly from corner kick | No |
```

---

## 🎯 Benefits of This Approach

1. **Standardized**: All documents in a uniform format (Markdown)
2. **Searchable**: Plain text and easy to index
3. **Structure Preserving**: Docling maintains the document structure
4. **Tables**: Tables are converted to Markdown table format
5. **Langflow Integrated**: Easily usable in Langflow
6. **Maintainable**: Markdowns can be version controlled

---

## 🚀 Next Steps

1. Download FIFA/IFAB documents
2. Run processing script
3. Verify Markdown quality
4. Integrate with VAR-Lens Agent
5. Test in Langflow

---

**Important Note**: Always process documents with Docling before using them in agents!