# LangFlow Import Guide for FanPulse

## 🎯 Quick Start

### Step 1: Start LangFlow
```bash
# Make sure Ollama is running first
ollama list

# Start LangFlow
langflow run
```

LangFlow will open at: **http://localhost:7860**

---

## 📥 Importing Workflows

### Option A: Import Main Orchestrator (Recommended for Demo)

1. Open LangFlow UI at `http://localhost:7860`
2. Click **"New Project"** or **"Import"** button (top right)
3. Select: `langflow_workflows/fanpulse_main_flow.json`
4. Click **"Import"**
5. The complete orchestration flow will load

**What you get:**
- Query routing logic
- Both VAR-Lens and Tactical Pulse agents
- Unified response formatting
- Complete end-to-end workflow

---

### Option B: Import Individual Agents

#### VAR-Lens Agent
1. Click **"Import"**
2. Select: `langflow_workflows/var_lens_flow.json`
3. This loads the VAR decision explanation agent

#### Tactical Pulse Agent
1. Click **"Import"**
2. Select: `langflow_workflows/tactical_pulse_flow.json`
3. This loads the match analysis agent

---

## 🔧 Configuration After Import

### 1. Verify Ollama Connection

In the **LLM node** (Ollama):
- **Base URL**: `http://localhost:11434`
- **Model**: `granite4.1:8b`
- **Temperature**: 0.3 (VAR-Lens) or 0.7 (Tactical Pulse)

**Test it:**
```bash
curl http://localhost:11434/api/tags
```

### 2. Verify Data Paths

#### For VAR-Lens Flow:
- **Directory Loader**: `data/processed_documents`
- **Vector Store**: `data/vector_stores/var_lens_faiss`

#### For Tactical Pulse Flow:
- **Match Data**: `data/match_data/results.csv`

### 3. Check Python Environment

The Python Function nodes need access to FanPulse code:

```python
import sys
sys.path.insert(0, 'd:/MyPythonProjects/FanPulse')
```

**Update this path** if your project is in a different location!

---

## 🧪 Testing the Workflows

### Test VAR-Lens Flow

**Input Examples:**
```
What is the offside rule?
Explain VAR decision process
What are the handball rules?
When can a referee use VAR?
```

**Expected Output:**
- Detailed explanation based on FIFA documents
- Rule references
- Clear, accurate answers

---

### Test Tactical Pulse Flow

**Input Examples:**
```
Analyze Brazil's performance
Predict Brazil vs Argentina
Show me statistics for Germany
```

**Expected Output:**
- Team statistics (win rate, form, etc.)
- Match predictions with probabilities
- AI-generated tactical insights

---

### Test Main Orchestrator

**Input Examples:**
```
What is the offside rule?           → Routes to VAR-Lens
Predict Brazil vs Argentina         → Routes to Tactical Pulse
Explain penalty kick rules          → Routes to VAR-Lens
Analyze Germany's recent form       → Routes to Tactical Pulse
```

**Expected Output:**
- Automatic routing to correct agent
- Unified response format
- Routing metadata (agent, confidence)

---

## 🎨 Visual Flow Overview

### Main Orchestrator Flow
```
┌─────────────┐
│ Chat Input  │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│  Query Router   │
│  (Python Func)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
┌────────┐ ┌──────────────┐
│VAR-Lens│ │Tactical Pulse│
│SubFlow │ │   SubFlow    │
└────┬───┘ └──────┬───────┘
     │            │
     └─────┬──────┘
           ↓
    ┌──────────────┐
    │   Response   │
    │   Formatter  │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ Chat Output  │
    └──────────────┘
```

---

## 🐛 Troubleshooting

### Issue 1: "Module not found" error in Python Function

**Solution:**
```python
# Add at the top of Python Function nodes
import sys
sys.path.insert(0, 'YOUR_PROJECT_PATH')
```

### Issue 2: Ollama not responding

**Check:**
```bash
# Is Ollama running?
ollama list

# Is the model available?
ollama list | grep granite

# Test the API
curl http://localhost:11434/api/tags
```

### Issue 3: Vector store not found

**Solution:**
```bash
# Make sure vector store exists
ls data/vector_stores/var_lens_faiss

# If not, create it
python scripts/process_documents.py
```

### Issue 4: Match data not loading

**Check:**
```bash
# Verify file exists
ls data/match_data/results.csv

# Check file size (should be ~5MB)
du -h data/match_data/results.csv
```

---

## 🎬 Demo Workflow

### For IBM Challenge Demo:

1. **Start Services:**
   ```bash
   ollama serve
   langflow run
   ```

2. **Import Main Flow:**
   - Import `fanpulse_main_flow.json`

3. **Test Scenarios:**
   
   **Scenario 1: VAR Question**
   ```
   Input: "What is the offside rule in soccer?"
   Expected: Detailed FIFA rule explanation
   ```

   **Scenario 2: Match Prediction**
   ```
   Input: "Predict Brazil vs Argentina"
   Expected: Win probabilities + AI analysis
   ```

   **Scenario 3: Team Analysis**
   ```
   Input: "Analyze Germany's performance"
   Expected: Statistics + tactical insights
   ```

4. **Show Visual Flow:**
   - Zoom out to show complete architecture
   - Highlight routing logic
   - Show data flow through nodes

5. **Explain Key Features:**
   - IBM Granite 4.1 8B integration
   - Docling document processing
   - Dynamic data ingestion
   - Dual-agent architecture

---

## 📊 Performance Tips

### For Faster Response Times:

1. **Pre-load Vector Store:**
   ```python
   # In VAR-Lens flow, load vector store at startup
   vector_store = FAISS.load_local("data/vector_stores/var_lens_faiss")
   ```

2. **Cache Match Data:**
   ```python
   # In Tactical Pulse flow, cache DataFrame
   @lru_cache(maxsize=1)
   def load_matches():
       return pd.read_csv("data/match_data/results.csv")
   ```

3. **Adjust LLM Settings:**
   - Lower `num_predict` for faster responses
   - Increase `temperature` for more creative answers

---

## 🔗 Next Steps

After successful import:

1. ✅ Test all three workflows
2. ✅ Customize prompts if needed
3. ✅ Add your own test cases
4. ✅ Prepare demo scenarios
5. ✅ Record demo video

---

## 📚 Additional Resources

- **Main Documentation**: `README.md`
- **Architecture**: `ARCHITECTURE.md`
- **Demo Scenarios**: `docs/demo-scenarios.md`
- **API Reference**: `docs/langflow-integration-guide.md`

---

## 💡 Tips for Demo

1. **Start with Simple Queries:**
   - "What is VAR?" → Shows VAR-Lens
   - "Analyze Brazil" → Shows Tactical Pulse

2. **Show Routing Logic:**
   - Explain how keywords determine agent selection
   - Show confidence levels

3. **Highlight IBM Technologies:**
   - IBM Granite 4.1 8B for LLM
   - Docling for document processing
   - LangFlow for orchestration

4. **Demonstrate Dynamic Data:**
   - Show how new matches can be added
   - Show how new VAR reports can be ingested

---

**Ready to Demo! 🚀**

For questions or issues, refer to the main documentation or GitHub repository.