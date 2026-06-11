# LangFlow Setup Guide for FanPulse

## 🎯 Overview

This guide shows you how to set up and use FanPulse with LangFlow for the IBM Skills Build AI Builders Challenge demo.

---

## 📋 Prerequisites

### 1. Install LangFlow
```bash
pip install langflow
```

### 2. Verify Ollama is Running
```bash
# Check Ollama status
ollama list

# Should see granite4.1:8b in the list
# If not, pull it:
ollama pull granite4.1:8b
```

### 3. Verify Data Files Exist
```bash
# Check FIFA documents (should have 7 .md files)
ls data/processed_documents/

# Check match data (should be ~5MB)
ls -lh data/match_data/results.csv

# Check vector store (should exist)
ls data/vector_stores/var_lens_faiss/
```

---

## 🚀 Starting LangFlow

### Step 1: Start Ollama
```bash
# Windows
ollama serve

# Linux/Mac
ollama serve
```

### Step 2: Start LangFlow
```bash
langflow run
```

LangFlow will start at: **http://localhost:7860**

---

## 📥 Importing FanPulse Workflows

### Option 1: Import Main Orchestrator (Recommended)

1. Open browser: `http://localhost:7860`
2. Click **"New Project"** or **"Import"**
3. Navigate to: `langflow_workflows/`
4. Select: **`fanpulse_main_flow.json`**
5. Click **"Import"**

**This gives you:**
- Complete orchestration system
- Automatic query routing
- Both VAR-Lens and Tactical Pulse agents
- Unified response formatting

---

### Option 2: Import Individual Agents

#### VAR-Lens Agent Only
- Import: `langflow_workflows/var_lens_flow.json`
- Use for: VAR decision explanations

#### Tactical Pulse Agent Only
- Import: `langflow_workflows/tactical_pulse_flow.json`
- Use for: Match analysis and predictions

---

## ⚙️ Configuration

### 1. Update File Paths (if needed)

If your project is not in `d:/MyPythonProjects/FanPulse`, update paths in Python Function nodes:

```python
# Change this line:
sys.path.insert(0, 'd:/MyPythonProjects/FanPulse')

# To your actual path:
sys.path.insert(0, 'YOUR_PROJECT_PATH')
```

### 2. Verify Ollama Connection

In LLM nodes, check:
- **Base URL**: `http://localhost:11434`
- **Model**: `granite4.1:8b`

Test connection:
```bash
curl http://localhost:11434/api/tags
```

---

## 🧪 Testing the Workflows

### Test 1: VAR Question
```
Input: "What is the offside rule in soccer?"
Expected: Detailed FIFA rule explanation with sources
```

### Test 2: Match Prediction
```
Input: "Predict Brazil vs Argentina"
Expected: Win probabilities + AI tactical analysis
```

### Test 3: Team Analysis
```
Input: "Analyze Germany's performance"
Expected: Statistics + form + AI insights
```

---

## 🎬 Demo Workflow

### For IBM Challenge Presentation:

#### 1. Preparation (5 minutes before)
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start LangFlow
langflow run

# Browser: Open http://localhost:7860
# Import: fanpulse_main_flow.json
```

#### 2. Demo Script (3 minutes)

**Introduction (30 seconds):**
> "FanPulse is a dual-agent AI system for World Cup 2026 analysis, powered by IBM Granite and orchestrated through LangFlow."

**Show Architecture (30 seconds):**
- Zoom out to show complete flow
- Highlight: Query Router → Agents → Response Handler
- Point out: IBM Granite 4.1 8B nodes

**Demo 1: VAR Decision (60 seconds):**
```
Input: "What is the offside rule?"
```
- Show routing to VAR-Lens
- Highlight: Docling-processed FIFA documents
- Show: FAISS vector store retrieval
- Display: Answer with rule references

**Demo 2: Match Prediction (60 seconds):**
```
Input: "Predict Brazil vs Argentina"
```
- Show routing to Tactical Pulse
- Highlight: 49K+ historical matches
- Show: Statistical analysis
- Display: Win probabilities + AI insights

**Conclusion (30 seconds):**
> "FanPulse demonstrates IBM technologies: Granite for LLM, Docling for documents, LangFlow for orchestration, with dynamic data ingestion for real-time updates."

---

## 🔧 Troubleshooting

### Issue: "Module not found" in Python Function

**Solution:**
```python
# Add at top of Python Function nodes:
import sys
sys.path.insert(0, 'd:/MyPythonProjects/FanPulse')
```

### Issue: Ollama not responding

**Check:**
```bash
# Is Ollama running?
curl http://localhost:11434/api/tags

# Is model available?
ollama list | grep granite

# Restart if needed
ollama serve
```

### Issue: Vector store not found

**Solution:**
```bash
# Verify it exists
ls data/vector_stores/var_lens_faiss/

# If missing, recreate it
python scripts/process_documents.py
```

### Issue: Match data not loading

**Check:**
```bash
# File exists?
ls data/match_data/results.csv

# File size correct? (should be ~5MB)
du -h data/match_data/results.csv
```

---

## 📊 Performance Tips

### For Faster Demo:

1. **Pre-load Vector Store:**
   - Start LangFlow before demo
   - Run one test query to warm up

2. **Reduce LLM Tokens:**
   - In Ollama nodes: `num_predict: 500` (instead of 1000)
   - Faster responses, still good quality

3. **Use Cached Data:**
   - Match data loads once, then cached
   - Vector store stays in memory

---

## 🎯 Key Features to Highlight

### 1. IBM Technologies
- ✅ **IBM Granite 4.1 8B**: LLM for both agents
- ✅ **Docling**: FIFA document processing
- ✅ **LangFlow**: Visual orchestration

### 2. Architecture
- ✅ **Dual-Agent System**: Specialized agents
- ✅ **Query Routing**: Intelligent classification
- ✅ **Unified Responses**: Consistent formatting

### 3. Data
- ✅ **Static Data**: 49K+ historical matches, FIFA rules
- ✅ **Dynamic Data**: Real-time ingestion capability
- ✅ **Vector Store**: 662 vectors from FIFA documents

### 4. Scalability
- ✅ **Modular Design**: Easy to extend
- ✅ **API Ready**: Can add FastAPI endpoints
- ✅ **Production Ready**: Error handling, logging

---

## 📚 Additional Resources

- **Complete Import Guide**: `langflow_workflows/IMPORT_GUIDE.md`
- **Workflow README**: `langflow_workflows/README.md`
- **Main Documentation**: `README.md`
- **Architecture**: `ARCHITECTURE.md`

---

## ✅ Pre-Demo Checklist

- [ ] Ollama running with Granite 4.1 8B
- [ ] LangFlow running at localhost:7860
- [ ] Main flow imported successfully
- [ ] Test query 1 works (VAR question)
- [ ] Test query 2 works (Match prediction)
- [ ] All paths configured correctly
- [ ] Demo script prepared
- [ ] Backup plan ready (screenshots/video)

---

**Ready for Demo! 🚀**

For detailed troubleshooting, see `langflow_workflows/IMPORT_GUIDE.md`