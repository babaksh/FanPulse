# VAR-Lens Setup Scripts

This directory contains all scripts related to VAR-Lens agent setup and document processing.

## 📁 Files

### 1. `process_documents.py`
Process FIFA/IFAB PDF documents with IBM Docling and convert to Markdown.

**Usage:**
```bash
# Process all PDFs
python scripts/var_lens_setup/process_documents.py

# Process specific file
python scripts/var_lens_setup/process_documents.py --file "document.pdf"

# Force reprocess
python scripts/var_lens_setup/process_documents.py --force
```

### 2. `build_var_lens_vectorstore.py`
Complete RAG engine + vector store builder (combined module).

**Usage as Script:**
```bash
# Build or load vector store
python scripts/var_lens_setup/build_var_lens_vectorstore.py

# Force rebuild
python scripts/var_lens_setup/build_var_lens_vectorstore.py --rebuild
```

### 3. `add_referee_decision.py`
Add referee decisions and VAR reviews to match database.

**Usage:**
```bash
# Interactive mode
python scripts/var_lens_setup/add_referee_decision.py

# Programmatic usage
from scripts.var_lens_setup.add_referee_decision import add_referee_decision

add_referee_decision(
    match_id="WC2026_2026_06_15_Brazil_Argentina",
    minute=67,
    event_type="goal_disallowed",
    description="Neymar goal cancelled for offside",
    var_decision={
        "reason": "offside",
        "review_duration": "2:15",
        "referee": "Pierluigi Collina"
    }
)
```

**Usage as Module:**
```python
from build_var_lens_vectorstore import VARLensRAG

# Initialize and setup
rag = VARLensRAG()
rag.setup()

# Query (requires LLM from LangFlow)
result = rag.query("What is offside?")
```

## 🔄 Workflow

```
1. Add PDF → data/raw_documents/
2. Process → python scripts/var_lens_setup/process_documents.py
3. Build Vector Store → python scripts/var_lens_setup/build_var_lens_vectorstore.py --rebuild
4. Add Match Decisions → python scripts/var_lens_setup/add_referee_decision.py
5. Ready to use in VAR-Lens agent!
```

## 📚 Related Files

- **Raw Documents**: `data/raw_documents/`
- **Processed Documents**: `data/processed_documents/`
- **Vector Store**: `data/vector_stores/var_lens/`
- **Referee Decisions**: `data/referee_decisions/`
- **LangFlow Components**: `langflow_components/var_lens_agent.py`

## 🎯 Purpose

These scripts handle the **knowledge base** for VAR-Lens agent:
- Converting official FIFA/IFAB PDFs to searchable format
- Building vector embeddings for semantic search
- Enabling RAG (Retrieval Augmented Generation) pipeline

---

**Made with Bob**