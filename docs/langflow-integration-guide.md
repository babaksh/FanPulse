# Langflow Integration Guide with Application

## 🎯 Key Questions

### 1. Do we do everything inside Langflow?
**Answer**: No! We use a hybrid approach:

#### Approach A: Langflow as Orchestrator (Recommended)
```
User Request
    ↓
FastAPI Backend
    ↓
Langflow API (Orchestrator)
    ↓
┌─────────────┴─────────────┐
│                           │
VAR-Lens Flow          Tactical Pulse Flow
(Inside Langflow)         (Inside Langflow)
```

#### Approach B: Python Code + Langflow Components
```
User Request
    ↓
FastAPI Backend
    ↓
Python Agents (Our code)
    ↓
Langflow Components (Only for specific parts)
```

**Our Recommendation**: Approach A - Because:
- ✅ Better Demo (Visual)
- ✅ Judges can see the workflow
- ✅ Easier to modify
- ✅ Better utilization of Langflow features

---

## 🏗️ Detailed Architecture

### General Structure

```
┌────────────────────────────────────────────────────────┐
│                    User Interface                      │
│              (Browser / API Client / Postman)          │
└────────────────────────┬───────────────────────────────┘
                         │ HTTP Request
                         ↓
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend                       │
│                  (src/api/main.py)                     │
│                                                        │
│  Endpoints:                                            │
│  • POST /api/var-lens/explain                          │
│  • POST /api/tactical-pulse/analyze                    │
│  • GET /api/health                                     │
└────────────────────────┬───────────────────────────────┘
                         │ HTTP Request
                         ↓
┌────────────────────────────────────────────────────────┐
│              Langflow Server (localhost:7860)          │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │         VAR-Lens Flow (JSON Workflow)            │  │
│  │                                                  │  │
│  │  [Input] → [Docling Loader] → [Vector Store]     │  │
│  │     ↓                                            │  │
│  │  [Retriever] → [Granite LLM] → [Output]          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Tactical Pulse Flow (JSON Workflow)         │  │
│  │                                                  │  │
│  │  [Input] → [Data Processor] → [IBM Bob]          │  │
│  │     ↓                                            │  │
│  │  [Pattern Detector] → [Granite LLM] → [Output]   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 How FastAPI Communicates with Langflow

### Step 1: Setting up Langflow

```bash
# Install Langflow
pip install langflow

# Run Langflow server
langflow run --host 0.0.0.0 --port 7860

# Langflow UI is available at:
# http://localhost:7860
```

### Step 2: Building Flows in Langflow UI

#### VAR-Lens Flow:
1. Open Langflow UI
2. Create a new Flow named "VAR-Lens"
3. Add Components:
   - **Input Component**: Receive user question
   - **Document Loader**: Load Docling Markdown files
   - **Text Splitter**: Split text into chunks
   - **Embeddings**: Convert to vectors
   - **Vector Store (FAISS)**: Store vectors
   - **Retriever**: Search for most relevant rules
   - **Granite LLM**: Generate response
   - **Output Component**: Return result

4. **Export Flow**: Save as JSON

```json
// var_lens_flow.json
{
  "name": "VAR-Lens",
  "description": "Explain VAR decisions",
  "nodes": [...],
  "edges": [...]
}
```

### Step 3: Calling Langflow from FastAPI

```python
# src/api/routes/var_lens.py

from fastapi import APIRouter, HTTPException
import requests
from pydantic import BaseModel

router = APIRouter()

class VARRequest(BaseModel):
    decision_type: str
    description: str
    language: str = "en"

@router.post("/explain")
async def explain_var_decision(request: VARRequest):
    """
    Call VAR-Lens Flow in Langflow
    """
    
    # Langflow API URL
    langflow_url = "http://localhost:7860/api/v1/run/var-lens"
    
    # Create payload for Langflow
    payload = {
        "inputs": {
            "decision_type": request.decision_type,
            "description": request.description,
            "language": request.language
        },
        "tweaks": {}  # Additional settings
    }
    
    try:
        # Call Langflow
        response = requests.post(
            langflow_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Get result
        result = response.json()
        
        return {
            "success": True,
            "explanation": result["outputs"][0]["text"],
            "source_rules": result["outputs"][0]["metadata"]
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Langflow error: {str(e)}"
        )
```

---

## 📦 Building Knowledge Base in Langflow

### Do we build the Vector Database in Langflow?
**Answer**: Yes! Everything inside Langflow

### Steps:

#### 1. Process Documents with Docling (Outside Langflow)
```bash
# This is done once
python scripts/process_documents.py

# Result: Markdown files in data/processed_documents/
```

#### 2. Build Vector Store in Langflow

In Langflow UI:

```
┌─────────────────────────────────────────────────────┐
│              VAR-Lens Flow                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [1] Directory Loader Component                     │
│      ↓                                              │
│      Path: data/processed_documents/fifa_rules/     │
│      ↓                                              │
│  [2] Markdown Text Splitter                         │
│      ↓                                              │
│      Chunk Size: 1000                               │
│      Chunk Overlap: 200                             │
│      ↓                                              │
│  [3] Embeddings Component                           │
│      ↓                                              │
│      Model: sentence-transformers/all-MiniLM-L6-v2  │
│      ↓                                              │
│  [4] FAISS Vector Store                             │
│      ↓                                              │
│      Store vectors in memory or disk                │
│      ↓                                              │
│  [5] Retriever Component                            │
│      ↓                                              │
│      Search Type: similarity                        │
│      K: 3 (top 3 results)                           │
│      ↓                                              │
│  [6] Granite LLM Component                          │
│      ↓                                              │
│      Model: ibm/granite-13b-chat-v2                 │
│      Prompt: "Based on these rules: {context}       │
│               Explain: {question}"                  │
│      ↓                                              │
│  [7] Output Component                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### 3. Save Vector Store

Langflow automatically saves the vector store:
- In memory (for testing)
- Or on disk (for production)

```python
# In Langflow, FAISS Component has settings:
{
  "persist_directory": "data/vector_stores/var_lens_faiss",
  "allow_dangerous_deserialization": true
}
```

---

## 🔄 Complete Request Flow

### Example: Explaining a VAR Decision

```
1. User → Frontend/Postman
   POST http://localhost:8000/api/var-lens/explain
   {
     "decision_type": "offside",
     "description": "Player 5cm offside",
     "language": "fa"
   }

2. FastAPI Backend
   • Receive request
   • Validation with Pydantic
   • Prepare payload for Langflow

3. FastAPI → Langflow
   POST http://localhost:7860/api/v1/run/var-lens
   {
     "inputs": {
       "decision_type": "offside",
       "description": "Player 5cm offside",
       "language": "fa"
     }
   }

4. Langflow Processing
   • Receive input
   • Search in Vector Store (FAISS)
   • Find relevant rules
   • Send to Granite LLM
   • Generate explanation in Persian

5. Langflow → FastAPI
   {
     "outputs": [{
       "text": "According to Law 11...",
       "metadata": {
         "source_rules": ["Law 11 - Offside"],
         "confidence": 0.95
       }
     }]
   }

6. FastAPI → User
   {
     "success": true,
     "explanation": "According to Law 11...",
     "source_rules": ["Law 11 - Offside"]
   }
```

---

## 🎨 Building Agents in Langflow

### Do we build Agents in Langflow?
**Answer**: Yes! Langflow has Agent building capabilities

### Example: VAR-Lens Agent

```
┌─────────────────────────────────────────────────────┐
│           VAR-Lens Agent (in Langflow)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Agent Component]                                  │
│    ↓                                                │
│    Tools:                                           │
│    • search_fifa_rules (Vector Store Retriever)     │
│    • translate_to_language (Translation Tool)       │
│    • get_similar_cases (Historical DB)              │
│    ↓                                                │
│    LLM: Granite                                     │
│    ↓                                                │
│    System Prompt:                                   │
│    "You are a VAR expert. Use the tools to          │
│     find relevant rules and explain decisions."     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 💾 Data Management in Langflow

### Data Stored in Langflow:

1. **Vector Stores**: 
   - FAISS indexes
   - Path: `data/vector_stores/`

2. **Flows (Workflows)**:
   - JSON files
   - Path: `langflow_flows/`

3. **Cache**:
   - Temporary results
   - In memory or Redis

### Data Outside Langflow:

1. **Processed Markdown files**:
   - Path: `data/processed_documents/`
   - Generated with Docling

2. **Match data**:
   - Path: `data/match_data/`
   - For Tactical Pulse Agent

3. **Main Database**:
   - PostgreSQL/SQLite
   - For storing history and metadata

---

## 🚀 Complete Setup

### Step 1: Installation and Setup

```bash
# 1. Install dependencies
pip install langflow fastapi uvicorn

# 2. Start Langflow
langflow run --host 0.0.0.0 --port 7860 &

# 3. Start FastAPI
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
```

### Step 2: Build Flows in Langflow

1. Open `http://localhost:7860`
2. Create VAR-Lens Flow
3. Create Tactical Pulse Flow
4. Export both Flows to JSON
5. Save in `langflow_flows/`

### Step 3: Testing

```bash
# Test VAR-Lens
curl -X POST http://localhost:8000/api/var-lens/explain \
  -H "Content-Type: application/json" \
  -d '{
    "decision_type": "offside",
    "description": "Player was offside",
    "language": "en"
  }'

# Test Tactical Pulse
curl -X POST http://localhost:8000/api/tactical-pulse/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "test_match",
    "minute": 65,
    "events": []
  }'
```

---

## 📊 Advantages and Disadvantages

### Advantages of Using Langflow:

✅ **Visual and Understandable**: Judges can see the workflow
✅ **Faster**: No need for extensive coding
✅ **Modifiable**: Easy to change components
✅ **Built-in Components**: Many features ready to use
✅ **Great Demo**: Excellent for presentations

### Disadvantages:

❌ **Learning Curve**: Need to learn Langflow
❌ **Limitations**: Some complex tasks are harder
❌ **Debugging**: Debugging is harder than pure Python

---

## 🎯 Final Recommendation

### Recommended Strategy:

1. **Core Logic in Langflow** ✅
   - RAG pipeline
   - Agent workflows
   - LLM calls

2. **Preprocessing Outside Langflow** ✅
   - Document processing with Docling
   - Data cleaning
   - Feature engineering

3. **API Layer in FastAPI** ✅
   - Authentication
   - Rate limiting
   - Error handling
   - Logging

4. **Frontend (Optional)**
   - React dashboard
   - Or use Langflow UI directly

---

## 📝 Summary

**Question**: Do we do everything in Langflow?
**Answer**: No, but we build the main parts (agents and workflows) in Langflow.

**Question**: How do we communicate between the app and Langflow?
**Answer**: Through HTTP API - FastAPI sends requests to Langflow and receives responses.

**Question**: Where do we build the vector database?
**Answer**: Inside Langflow using the FAISS Component.

---

**Next Step**: Start building your first Flow in Langflow! 🚀