# VAR-Lens Agent Setup Guide

## Overview

This guide walks you through setting up and testing the VAR-Lens RAG (Retrieval Augmented Generation) system.

## Architecture

```
VAR-Lens RAG Pipeline
=====================

FIFA PDF Documents
       ↓
   [Docling] ✅ (Already done - 7 files processed)
       ↓
Markdown Files (450 KB)
       ↓
   [Document Loader]
       ↓
   [Text Splitter] (1000 chars, 200 overlap)
       ↓
   [Embeddings] (HuggingFace: all-MiniLM-L6-v2)
       ↓
   [FAISS Vector Store]
       ↓
   [Retriever] (k=4 documents)
       ↓
   [LLM] (IBM Granite / OpenAI)
       ↓
   Answer + Sources
```

## Step 1: Build Vector Store

The vector store converts all FIFA documents into searchable vectors.

```bash
# Build vector store (first time)
python scripts/build_var_lens_vectorstore.py

# Rebuild if documents changed
python scripts/build_var_lens_vectorstore.py --rebuild
```

**What happens:**
- Loads all 7 Markdown files from `data/processed_documents/`
- Splits into ~1000 character chunks
- Converts to vectors using HuggingFace embeddings
- Saves to `data/vector_stores/var_lens/`

**Expected output:**
```
VAR-Lens Vector Store Builder
======================================================================

Initializing VAR-Lens RAG engine...
Loading documents from: data/processed_documents
Loaded 7 documents
Splitting documents into chunks...
Created XXX chunks
Initializing embeddings: sentence-transformers/all-MiniLM-L6-v2
Creating vector store...
Vector store created successfully
Saving vector store to: data/vector_stores/var_lens
Vector store saved successfully

======================================================================
Vector Store Statistics
======================================================================
  docs_path.......................................... data/processed_documents
  vector_store_path.................................. data/vector_stores/var_lens
  embedding_model.................................... sentence-transformers/all-MiniLM-L6-v2
  chunk_size......................................... 1000
  chunk_overlap...................................... 200
  k_documents........................................ 4
  vector_store_exists................................ True
  num_vectors........................................ XXX

======================================================================
✅ Vector store is ready!
======================================================================
```

## Step 2: Test Retrieval

Test that documents can be retrieved correctly.

```bash
python scripts/test_var_lens_rag.py
```

**What it tests:**
1. Vector store loading
2. Document retrieval for sample questions
3. Shows how LLM integration would work

**Sample questions tested:**
- "What is the VAR protocol?"
- "When can VAR be used?"
- "What is offside rule?"
- "What are the reviewable incidents in VAR?"

## Step 3: Integration Options

### Option A: Use in Python (Direct)

```python
from src.agents.var_lens.rag_engine import VARLensRAG
from langchain_openai import ChatOpenAI

# Initialize
rag = VARLensRAG()
rag.load_vector_store()

# Add LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
rag.create_qa_chain(llm)

# Query
result = rag.query("Why was that goal disallowed for offside?")
print(result["answer"])
```

### Option B: Use in Langflow (Visual)

1. **Open Langflow:**
   ```bash
   langflow run
   # Opens at http://localhost:7860
   ```

2. **Create New Flow:**
   - Name: "VAR-Lens Agent"

3. **Add Components:**

   **Component 1: Directory Loader**
   - Type: `Data > Directory Loader`
   - Path: `data/processed_documents`
   - Glob: `**/*.md`
   - Recursive: `true`

   **Component 2: Text Splitter**
   - Type: `Processing > Recursive Character Text Splitter`
   - Chunk Size: `1000`
   - Chunk Overlap: `200`

   **Component 3: Embeddings**
   - Type: `Embeddings > HuggingFace Embeddings`
   - Model: `sentence-transformers/all-MiniLM-L6-v2`

   **Component 4: Vector Store**
   - Type: `Vector Stores > FAISS`
   - Connect: Documents from Splitter
   - Connect: Embeddings from Embeddings component

   **Component 5: Chat Input**
   - Type: `Inputs > Chat Input`
   - Name: "User Question"

   **Component 6: Retriever**
   - Type: `Retrievers > Vector Store Retriever`
   - Vector Store: Connect to FAISS
   - Search Type: `similarity`
   - K: `4`

   **Component 7: Prompt Template**
   - Type: `Prompts > Prompt Template`
   - Template: (See below)

   **Component 8: LLM**
   - Type: `Models > OpenAI` or `IBM Granite`
   - Model: `gpt-3.5-turbo` or granite model
   - Temperature: `0`

   **Component 9: Chat Output**
   - Type: `Outputs > Chat Output`

4. **Prompt Template:**
   ```
   You are VAR-Lens, an expert AI assistant specialized in explaining VAR decisions.

   Context from FIFA/IFAB Documents:
   {context}

   Question: {question}

   Instructions:
   - Answer based ONLY on the provided context
   - Reference specific rules when applicable
   - Use simple language
   - Be objective and educational

   Answer:
   ```

5. **Connect Components:**
   ```
   Directory Loader → Text Splitter → FAISS Vector Store
                                            ↓
   Chat Input → Retriever ← Vector Store
                    ↓
              Prompt Template → LLM → Chat Output
   ```

6. **Test in Playground:**
   - Click "Playground" button
   - Ask: "What is VAR?"
   - Should get answer with sources

7. **Export Flow:**
   - Click "Export" → "JSON"
   - Save as: `langflow_flows/var_lens_agent.json`

### Option C: Use via FastAPI

```python
# src/api/routes/var_lens.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.agents.var_lens.rag_engine import VARLensRAG

router = APIRouter(prefix="/var-lens", tags=["VAR-Lens"])

# Initialize RAG (do this once at startup)
rag = VARLensRAG()
rag.load_vector_store()
# Add LLM here

class Question(BaseModel):
    question: str
    language: str = "en"

@router.post("/explain")
async def explain_var(q: Question):
    """Explain a VAR decision."""
    result = rag.query(q.question)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }
```

## Step 4: Add LLM

### Option 1: OpenAI (for testing)

```bash
# Install
pip install langchain-openai

# Set API key
export OPENAI_API_KEY="sk-..."
```

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    max_tokens=500
)

rag.create_qa_chain(llm)
```

### Option 2: IBM Granite (production)

```bash
# Install IBM watsonx SDK
pip install ibm-watsonx-ai

# Set credentials
export IBM_CLOUD_API_KEY="your-key"
export IBM_WATSONX_PROJECT_ID="your-project-id"
```

```python
from ibm_watsonx_ai.foundation_models import Model

# Initialize Granite
granite = Model(
    model_id="ibm/granite-13b-chat-v2",
    credentials={
        "apikey": os.getenv("IBM_CLOUD_API_KEY"),
        "url": "https://us-south.ml.cloud.ibm.com"
    },
    project_id=os.getenv("IBM_WATSONX_PROJECT_ID")
)

# Wrap for LangChain
from langchain_ibm import WatsonxLLM
llm = WatsonxLLM(model=granite)

rag.create_qa_chain(llm)
```

### Option 3: HuggingFace (free, slower)

```python
from langchain_community.llms import HuggingFaceHub

llm = HuggingFaceHub(
    repo_id="google/flan-t5-large",
    model_kwargs={"temperature": 0, "max_length": 512}
)

rag.create_qa_chain(llm)
```

## Troubleshooting

### Issue: "Vector store not found"
**Solution:** Run `python scripts/build_var_lens_vectorstore.py`

### Issue: "No module named 'langchain'"
**Solution:** 
```bash
pip install langchain langchain-community
pip install sentence-transformers faiss-cpu
```

### Issue: "Documents not loading"
**Solution:** Check that processed documents exist:
```bash
ls data/processed_documents/
# Should show 7 .md files
```

### Issue: "Out of memory"
**Solution:** Reduce chunk size or use smaller embedding model:
```python
rag = VARLensRAG(
    chunk_size=500,  # Smaller chunks
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # Smaller model
)
```

## Performance Tips

1. **First Query is Slow:** Embeddings load on first use (~5-10 seconds)
2. **Subsequent Queries:** Fast (<1 second for retrieval)
3. **LLM Speed:** Depends on model (Granite: 2-5s, GPT-3.5: 1-3s)
4. **Batch Processing:** Process multiple questions together

## Next Steps

1. ✅ Build vector store
2. ✅ Test retrieval
3. ⏳ Add LLM (OpenAI or Granite)
4. ⏳ Test full Q&A
5. ⏳ Integrate with Langflow
6. ⏳ Build FastAPI endpoint
7. ⏳ Create demo scenarios

## Files Created

```
src/agents/var_lens/
├── __init__.py
└── rag_engine.py          # Core RAG implementation

scripts/
├── build_var_lens_vectorstore.py  # Build vector store
└── test_var_lens_rag.py           # Test system

data/
├── processed_documents/    # 7 Markdown files (450 KB)
└── vector_stores/
    └── var_lens/          # FAISS index (created by script)
```

## Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [HuggingFace Embeddings](https://huggingface.co/sentence-transformers)
- [IBM Granite Models](https://www.ibm.com/products/watsonx-ai/foundation-models)

---

**Last Updated:** 2026-06-10  
**Status:** Ready for testing 🚀