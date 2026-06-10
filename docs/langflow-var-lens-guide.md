# VAR-Lens Agent Construction Guide in Langflow

## 📌 Introduction

This guide shows step-by-step how to build the VAR-Lens Agent in Langflow.

---

## 🎯 Goal

Building an AI Agent that:
- Receives user questions about VAR decisions.
- Searches within FIFA rules.
- Returns accurate and documented answers.

---

## 🚀 Step 1: Setting up Langflow

### 1.1 Running Langflow

```bash
langflow run
```

### 1.2 Opening the UI

- Open your browser.
- Go to: `http://localhost:7860`
- You will see a page with a blank canvas.

### 1.3 Creating a New Flow

- Click on "New Flow".
- Name it: `VAR-Lens Agent`
- A blank canvas will open.

---

## 🧩 Step 2: Adding Components

### Component 1: File Loader (Loading files)

**Location in Langflow:** `Data > File`

**Settings:**
```
Component: File
Path: data/processed_documents/
File Types: .md
```
Recursive: true
```

**Explanation:** Loads all Markdown files from the folder.

---

### Component 2: Text Splitter (Splitting text)

**Location in Langflow:** `Processing > Text Splitter`

**Settings:**
```
Component: RecursiveCharacterTextSplitter
Chunk Size: 1000
Chunk Overlap: 200
Separators: ["\n\n", "\n", " ", ""]
```

**Explanation:** Splits long texts into 1000-character chunks with a 200-character overlap.

**Why Overlap?** To prevent loss of information between chunks.

---

### Component 3: Embeddings (Converting to Vector)

**Location in Langflow:** `Embeddings > HuggingFace Embeddings`

**Settings:**
```
Component: HuggingFace Embeddings
Model: sentence-transformers/all-MiniLM-L6-v2
```

**Explanation:** Converts each chunk into a vector (list of numbers) representing the meaning of the text.

**Example:**
```
"offside rule" → [0.23, -0.45, 0.67, ..., 0.12]  (384 numbers)
```

---

### Component 4: Vector Store (Storage)

**Location in Langflow:** `Vector Stores > FAISS`

**Settings:**
```
Component: FAISS
Index Name: fifa_rules
Persist Directory: data/vector_stores/
```

**Explanation:** Stores all vectors and performs fast semantic searching.

**How it works?**
1. When you run the flow for the first time, the vector store is created.
2. The second time, it uses the same vector store (faster).

---

### Component 5: Chat Input (User Input)

**Location in Langflow:** `Inputs > Chat Input`

**Settings:**
```
Component: Chat Input
Input Name: question
```

**Explanation:** Receives the user's question.

**Input Example:**
```
"Why was the goal disallowed for offside?"
```

---

### Component 6: Retriever (Searcher)

**Location in Langflow:** `Retrievers > Vector Store Retriever`

**Settings:**
```
Component: Vector Store Retriever
Vector Store: [Connect to FAISS]
Search Type: similarity
K: 4
Score Threshold: 0.7
```

**Explanation:** 
- Converts the user's question to a vector.
- Searches in the vector store.
- Returns the 4 most relevant chunks.

**Example:**
```
Input: "offside rule"
Output: 
  1. "Law 11 - Offside: A player is in an offside position if..."
  2. "VAR can review offside decisions when..."
  3. "The assistant referee signals offside by..."
  4. "Offside offence occurs when..."
```

---

### Component 7: Prompt Template (Prompt Template)

**Location in Langflow:** `Prompts > Prompt Template`

**Settings:**
```
Component: Prompt Template
Template:
"""
You are a VAR (Video Assistant Referee) expert explaining decisions to football fans.

Context from FIFA Laws of the Game:
{context}

User Question: {question}

Instructions:
1. Answer based ONLY on the context provided above
2. Cite the specific Law number when relevant
3. Explain in clear, simple language
4. If the context doesn't contain the answer, say "I don't have enough information"

Answer:
"""
```

**Explanation:** 
- `{context}`: Where the found chunks are placed.
- `{question}`: The user's question.

---

### Component 8: LLM (Language Model)

**Location in Langflow:** `Models > OpenAI` (Or IBM Granite if available)

**Settings:**
```
Component: OpenAI (Temporarily for testing)
Model: gpt-3.5-turbo
Temperature: 0.3
Max Tokens: 500
```

**Important Note:** Later we will replace this with IBM Granite.

**Explanation:** Receives the prompt and generates the response.

---

### Component 9: Chat Output (Output)

**Location in Langflow:** `Outputs > Chat Output`

**تنظیمات:**
```
Component: Chat Output
Output Name: answer
```

**توضیح:** جواب نهایی رو به کاربر نشون میده.

---

## 🔗 مرحله 3: اتصال Component ها

حالا باید component ها رو به هم وصل کنیم. در Langflow با drag کردن از یه component به component دیگه، اونها رو وصل می‌کنیم.

### نمودار اتصالات:

```
┌─────────────┐
│ File Loader │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Text Splitter│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Embeddings  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FAISS     │◄─────────┐
│Vector Store │          │
└──────┬──────┘          │
       │                 │
       │            ┌────┴────┐
       │            │Retriever│
       │            └────┬────┘
       │                 │
       │                 ▼
       │          ┌─────────────┐
       │          │   Prompt    │◄───┐
       │          │  Template   │    │
       │          └──────┬──────┘    │
       │                 │           │
       │                 ▼           │
       │          ┌─────────────┐    │
       │          │     LLM     │    │
       │          └──────┬──────┘    │
       │                 │           │
       │                 ▼           │
       │          ┌─────────────┐    │
       │          │Chat Output  │    │
       │          └─────────────┘    │
       │                             │
       └─────────────────────────────┘
                                     │
                              ┌──────┴──────┐
                              │ Chat Input  │
                              └─────────────┘
```

### اتصالات دقیق:

1. **File Loader → Text Splitter**
   - Output: `documents`
   - Input: `documents`

2. **Text Splitter → Embeddings**
   - Output: `chunks`
   - Input: `texts`

3. **Embeddings → FAISS**
   - Output: `embeddings`
   - Input: `embeddings`

4. **Text Splitter → FAISS**
   - Output: `chunks`
   - Input: `documents`

5. **FAISS → Retriever**
   - Output: `vector_store`
   - Input: `vector_store`

6. **Chat Input → Retriever**
   - Output: `question`
   - Input: `query`

7. **Retriever → Prompt Template**
   - Output: `documents`
   - Input: `context`

8. **Chat Input → Prompt Template**
   - Output: `question`
   - Input: `question`

9. **Prompt Template → LLM**
   - Output: `prompt`
   - Input: `prompt`

10. **LLM → Chat Output**
    - Output: `response`
    - Input: `message`

---

## ✅ مرحله 4: Build و Test

### 4.1 Build کردن Flow

1. روی دکمه "Build" کلیک کن (گوشه بالا راست)
2. Langflow شروع می‌کنه به:
   - Load کردن فایل‌ها
   - Split کردن متن‌ها
   - ساخت embeddings
   - ساخت vector store
3. این فرآیند ~2-3 دقیقه طول می‌کشه

### 4.2 تست کردن

وقتی build تموم شد، می‌تونی تست کنی:

**تست 1:**
```
Input: "What is VAR?"
Expected: توضیح VAR از قوانین FIFA
```

**تست 2:**
```
Input: "Can VAR review a yellow card?"
Expected: توضیح اینکه VAR چه موقع می‌تونه کارت زرد رو review کنه
```

**تست 3:**
```
Input: "Why was the goal disallowed for offside?"
Expected: توضیح قانون آفساید و نقش VAR
```

---

## 💾 مرحله 5: Export کردن Flow

1. روی منوی "..." کلیک کن
2. "Export" رو انتخاب کن
3. فایل JSON ذخیره میشه
4. این فایل رو در `langflow_flows/var_lens_flow.json` ذخیره کن

---

## 🔧 مرحله 6: تنظیمات پیشرفته

### استفاده از IBM Granite

اگه IBM Granite در Langflow موجود باشه:

```
Component: IBM Granite
Model: granite-13b-chat-v2
API Key: [از IBM Cloud]
Temperature: 0.3
Max Tokens: 500
```

### بهینه‌سازی Retriever

برای نتایج بهتر:

```
K: 6 (به جای 4)
Score Threshold: 0.65 (به جای 0.7)
Search Type: mmr (به جای similarity)
```

MMR = Maximum Marginal Relevance (تنوع بیشتر در نتایج)

---

## 🐛 عیب‌یابی

### مشکل 1: Vector Store ساخته نمیشه

**راه حل:**
- مطمئن شو path فایل‌ها درسته
- مطمئن شو فایل‌های .md موجودن
- Build رو دوباره run کن

### مشکل 2: جواب‌ها نامرتبط هستن

**راه حل:**
- K رو افزایش بده (مثلاً 6)
- Score Threshold رو کم کن (مثلاً 0.6)
- Chunk Size رو تغییر بده (مثلاً 1500)

### مشکل 3: خطای API Key

**راه حل:**
- API Key رو در `.env` ذخیره کن
- در Langflow settings، API Key رو set کن

---

## 📊 معیارهای موفقیت

Agent خوب کار می‌کنه اگه:

✅ به سوالات VAR جواب دقیق بده
✅ از قوانین FIFA استناد کنه
✅ وقتی نمی‌دونه، بگه "نمی‌دونم"
✅ جواب‌ها واضح و قابل فهم باشن
✅ زمان پاسخ < 3 ثانیه

---

## 🎓 نکات مهم

1. **Vector Store فقط یک بار ساخته میشه**
   - بار اول: ~2-3 دقیقه
   - بارهای بعد: ~5 ثانیه

2. **Embeddings مهم هستن**
   - Model خوب = نتایج بهتر
   - `all-MiniLM-L6-v2` برای شروع خوبه
   - بعداً می‌تونیم model بهتر استفاده کنیم

3. **Prompt Engineering**
   - Prompt خوب = جواب بهتر
   - باید واضح و مشخص باشه
   - باید به LLM بگیم چطور جواب بده

4. **Testing مهمه**
   - حتماً با سوالات مختلف تست کن
   - Edge case ها رو چک کن
   - جواب‌های نادرست رو یادداشت کن

---

## 🚀 مرحله بعدی

بعد از اینکه Flow در Langflow کار کرد:

1. Export کردن Flow به JSON
2. ساخت FastAPI endpoint
3. اتصال Frontend به Backend
4. تست کامل سیستم

---

## 📚 منابع

- Langflow Docs: https://docs.langflow.org
- FAISS: https://github.com/facebookresearch/faiss
- HuggingFace Embeddings: https://huggingface.co/sentence-transformers
- IBM Granite: https://www.ibm.com/granite

---

**آماده‌ای شروع کنیم؟** 🚀