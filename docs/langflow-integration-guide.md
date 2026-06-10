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
│                            │
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
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Browser / API Client / Postman)            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                  (src/api/main.py)                       │
│                                                           │
│  Endpoints:                                              │
│  • POST /api/var-lens/explain                           │
│  • POST /api/tactical-pulse/analyze                     │
│  • GET /api/health                                       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Langflow Server (localhost:7860)            │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │         VAR-Lens Flow (JSON Workflow)             │  │
│  │                                                    │  │
│  │  [Input] → [Docling Loader] → [Vector Store]     │  │
│  │     ↓                                              │  │
│  │  [Retriever] → [Granite LLM] → [Output]          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Tactical Pulse Flow (JSON Workflow)          │  │
│  │                                                    │  │
│  │  [Input] → [Data Processor] → [IBM Bob]          │  │
│  │     ↓                                              │  │
│  │  [Pattern Detector] → [Granite LLM] → [Output]   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
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

### مرحله 2: ساخت Flows در Langflow UI

#### VAR-Lens Flow:
1. باز کردن Langflow UI
2. ساخت یک Flow جدید با نام "VAR-Lens"
3. اضافه کردن Components:
   - **Input Component**: دریافت سوال کاربر
   - **Document Loader**: بارگذاری Markdown های Docling
   - **Text Splitter**: تقسیم متن
   - **Embeddings**: تبدیل به vector
   - **Vector Store (FAISS)**: ذخیره vectors
   - **Retriever**: جستجوی مرتبط‌ترین قوانین
   - **Granite LLM**: تولید پاسخ
   - **Output Component**: برگرداندن نتیجه

4. **Export Flow**: ذخیره به عنوان JSON

```json
// var_lens_flow.json
{
  "name": "VAR-Lens",
  "description": "Explain VAR decisions",
  "nodes": [...],
  "edges": [...]
}
```

### مرحله 3: فراخوانی Langflow از FastAPI

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
    فراخوانی VAR-Lens Flow در Langflow
    """
    
    # آدرس Langflow API
    langflow_url = "http://localhost:7860/api/v1/run/var-lens"
    
    # ساخت payload برای Langflow
    payload = {
        "inputs": {
            "decision_type": request.decision_type,
            "description": request.description,
            "language": request.language
        },
        "tweaks": {}  # تنظیمات اضافی
    }
    
    try:
        # فراخوانی Langflow
        response = requests.post(
            langflow_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # دریافت نتیجه
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

## 📦 ساخت پایگاه دانش در Langflow

### آیا Vector Database را در Langflow می‌سازیم؟
**جواب**: بله! همه چیز داخل Langflow

### مراحل:

#### 1. پردازش اسناد با Docling (خارج از Langflow)
```bash
# این کار یکبار انجام می‌شود
python scripts/process_documents.py

# نتیجه: Markdown files در data/processed_documents/
```

#### 2. ساخت Vector Store در Langflow

در Langflow UI:

```
┌─────────────────────────────────────────────────────┐
│              VAR-Lens Flow                           │
├─────────────────────────────────────────────────────┤
│                                                       │
│  [1] Directory Loader Component                      │
│      ↓                                                │
│      Path: data/processed_documents/fifa_rules/      │
│      ↓                                                │
│  [2] Markdown Text Splitter                          │
│      ↓                                                │
│      Chunk Size: 1000                                │
│      Chunk Overlap: 200                              │
│      ↓                                                │
│  [3] Embeddings Component                            │
│      ↓                                                │
│      Model: sentence-transformers/all-MiniLM-L6-v2   │
│      ↓                                                │
│  [4] FAISS Vector Store                              │
│      ↓                                                │
│      Store vectors in memory or disk                 │
│      ↓                                                │
│  [5] Retriever Component                             │
│      ↓                                                │
│      Search Type: similarity                         │
│      K: 3 (top 3 results)                           │
│      ↓                                                │
│  [6] Granite LLM Component                           │
│      ↓                                                │
│      Model: ibm/granite-13b-chat-v2                  │
│      Prompt: "Based on these rules: {context}        │
│               Explain: {question}"                   │
│      ↓                                                │
│  [7] Output Component                                │
│                                                       │
└─────────────────────────────────────────────────────┘
```

#### 3. ذخیره Vector Store

Langflow به صورت خودکار vector store رو ذخیره می‌کنه:
- در حافظه (برای تست)
- یا روی دیسک (برای production)

```python
# در Langflow، FAISS Component تنظیمات داره:
{
  "persist_directory": "data/vector_stores/var_lens_faiss",
  "allow_dangerous_deserialization": true
}
```

---

## 🔄 جریان کامل یک Request

### مثال: توضیح یک تصمیم VAR

```
1. User → Frontend/Postman
   POST http://localhost:8000/api/var-lens/explain
   {
     "decision_type": "offside",
     "description": "Player 5cm offside",
     "language": "fa"
   }

2. FastAPI Backend
   • دریافت request
   • Validation با Pydantic
   • آماده‌سازی payload برای Langflow

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
   • دریافت input
   • جستجو در Vector Store (FAISS)
   • پیدا کردن قوانین مرتبط
   • ارسال به Granite LLM
   • تولید توضیح به فارسی

5. Langflow → FastAPI
   {
     "outputs": [{
       "text": "طبق قانون 11...",
       "metadata": {
         "source_rules": ["Law 11 - Offside"],
         "confidence": 0.95
       }
     }]
   }

6. FastAPI → User
   {
     "success": true,
     "explanation": "طبق قانون 11...",
     "source_rules": ["Law 11 - Offside"]
   }
```

---

## 🎨 ساخت Agents در Langflow

### آیا Agents را در Langflow می‌سازیم؟
**جواب**: بله! Langflow قابلیت ساخت Agent دارد

### مثال: VAR-Lens Agent

```
┌─────────────────────────────────────────────────────┐
│           VAR-Lens Agent (در Langflow)              │
├─────────────────────────────────────────────────────┤
│                                                       │
│  [Agent Component]                                   │
│    ↓                                                  │
│    Tools:                                            │
│    • search_fifa_rules (Vector Store Retriever)     │
│    • translate_to_language (Translation Tool)       │
│    • get_similar_cases (Historical DB)              │
│    ↓                                                  │
│    LLM: Granite                                      │
│    ↓                                                  │
│    System Prompt:                                    │
│    "You are a VAR expert. Use the tools to          │
│     find relevant rules and explain decisions."     │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 💾 مدیریت داده در Langflow

### دیتاهایی که در Langflow ذخیره می‌شوند:

1. **Vector Stores**: 
   - FAISS indexes
   - مسیر: `data/vector_stores/`

2. **Flows (Workflows)**:
   - JSON files
   - مسیر: `langflow_flows/`

3. **Cache**:
   - نتایج موقت
   - در حافظه یا Redis

### دیتاهایی که خارج از Langflow هستند:

1. **Markdown های پردازش شده**:
   - مسیر: `data/processed_documents/`
   - تولید شده با Docling

2. **دیتای مسابقات**:
   - مسیر: `data/match_data/`
   - برای Tactical Pulse Agent

3. **Database اصلی**:
   - PostgreSQL/SQLite
   - برای ذخیره تاریخچه و metadata

---

## 🚀 Setup کامل

### مرحله 1: نصب و راه‌اندازی

```bash
# 1. نصب dependencies
pip install langflow fastapi uvicorn

# 2. راه‌اندازی Langflow
langflow run --host 0.0.0.0 --port 7860 &

# 3. راه‌اندازی FastAPI
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
```

### مرحله 2: ساخت Flows در Langflow

1. باز کردن `http://localhost:7860`
2. ساخت VAR-Lens Flow
3. ساخت Tactical Pulse Flow
4. Export هر دو Flow به JSON
5. ذخیره در `langflow_flows/`

### مرحله 3: تست

```bash
# تست VAR-Lens
curl -X POST http://localhost:8000/api/var-lens/explain \
  -H "Content-Type: application/json" \
  -d '{
    "decision_type": "offside",
    "description": "Player was offside",
    "language": "en"
  }'

# تست Tactical Pulse
curl -X POST http://localhost:8000/api/tactical-pulse/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "test_match",
    "minute": 65,
    "events": []
  }'
```

---

## 📊 مزایا و معایب

### مزایای استفاده از Langflow:

✅ **بصری و قابل فهم**: داوران می‌تونن workflow رو ببینن  
✅ **سریع‌تر**: نیازی به کد نویسی زیاد نیست  
✅ **قابل تغییر**: راحت می‌شه components رو عوض کرد  
✅ **Built-in Components**: خیلی از کارها آماده هست  
✅ **Demo عالی**: برای ارائه خیلی خوبه  

### معایب:

❌ **Learning Curve**: باید Langflow رو یاد بگیری  
❌ **محدودیت‌ها**: بعضی کارهای پیچیده سخت‌تره  
❌ **Debugging**: debug کردن سخت‌تر از Python خالص  

---

## 🎯 توصیه نهایی

### استراتژی پیشنهادی:

1. **Core Logic در Langflow** ✅
   - RAG pipeline
   - Agent workflows
   - LLM calls

2. **Preprocessing خارج از Langflow** ✅
   - پردازش اسناد با Docling
   - Data cleaning
   - Feature engineering

3. **API Layer در FastAPI** ✅
   - Authentication
   - Rate limiting
   - Error handling
   - Logging

4. **Frontend (اختیاری)** 
   - React dashboard
   - یا استفاده مستقیم از Langflow UI

---

## 📝 خلاصه

**سوال**: همه کار را در Langflow انجام می‌دهیم؟  
**جواب**: خیر، ولی بخش اصلی (agents و workflows) را در Langflow می‌سازیم.

**سوال**: چطوری بین اپ و Langflow ارتباط برقرار می‌کنیم؟  
**جواب**: از طریق HTTP API - FastAPI به Langflow request می‌فرسته و response می‌گیره.

**سوال**: Vector database را کجا می‌سازیم؟  
**جواب**: داخل Langflow با استفاده از FAISS Component.

---

**گام بعدی**: شروع ساخت اولین Flow در Langflow! 🚀