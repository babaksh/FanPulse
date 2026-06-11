# FanPulse LangFlow Complete Guide

Complete guide for importing, configuring, and using FanPulse workflows in LangFlow.

---

## 📁 Workflow Files

### Main Workflows
- **`fanpulse_main_flow.json`** - Main orchestrator workflow that routes queries to appropriate agents
- **`var_lens_flow.json`** - VAR-Lens agent workflow for FIFA rules and VAR decisions
- **`tactical_pulse_flow.json`** - Tactical Pulse agent workflow for match analysis and predictions

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure Ollama is running
ollama list

# Verify Granite model is available
ollama list | grep granite

# Start LangFlow
langflow run
```

LangFlow will open at: **http://localhost:7860**

### 2. Import Workflow

**Option A: Main Orchestrator (Recommended for Demo)**
1. Open LangFlow UI at `http://localhost:7860`
2. Click **"Import"** button (top right)
3. Select: `langflow_workflows/fanpulse_main_flow.json`
4. Click **"Import"**

**What you get:**
- Query routing logic
- Both VAR-Lens and Tactical Pulse agents
- Unified response formatting
- Complete end-to-end workflow

**Option B: Individual Agents**
- Import `var_lens_flow.json` for VAR decision explanations
- Import `tactical_pulse_flow.json` for match analysis

---

## 🔧 Configuration

### Required Environment Variables
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=granite4.1:8b

# Data Paths
VECTOR_STORE_PATH=data/vector_stores/var_lens_faiss
MATCH_DATA_PATH=data/match_data/results.csv
TACTICAL_DATA_PATH=data/match_data/tactical_stats.csv
DOCS_PATH=data/processed_documents
```

### Verify Ollama Connection
In the **LLM node** (Ollama):
- **Base URL**: `http://localhost:11434`
- **Model**: `granite4.1:8b`
- **Temperature**: 0.3 (VAR-Lens) or 0.7 (Tactical Pulse)

**Test it:**
```bash
curl http://localhost:11434/api/tags
```

### Verify Data Paths

**For VAR-Lens Flow:**
- **Directory Loader**: `data/processed_documents`
- **Vector Store**: `data/vector_stores/var_lens_faiss`

**For Tactical Pulse Flow:**
- **Match Data**: `data/match_data/results.csv`
- **Tactical Data**: `data/match_data/tactical_stats.csv`

### Check Python Environment
The Python Function nodes need access to FanPulse code:
```python
import sys
sys.path.insert(0, 'd:/MyPythonProjects/FanPulse')
```
**Update this path** if your project is in a different location!

---

## 📊 Workflow Architecture

### Main Flow
```
User Query
    ↓
[Query Router]
    ↓
┌───────┴────────┐
│                │
VAR-Lens    Tactical Pulse
Agent          Agent
│                │
└───────┬────────┘
    ↓
[Response Handler]
    ↓
Unified Response
```

### VAR-Lens Flow
```
User Question
    ↓
[Document Loader] → FIFA Rules (Markdown)
    ↓
[Text Splitter] → Chunks
    ↓
[Embeddings] → Vectors
    ↓
[FAISS Store] → Vector Database
    ↓
[Retriever] ← User Query
    ↓
[Prompt Template] → Context + Question
    ↓
[LLM (Granite)] → Answer
    ↓
Response with Sources
```

### Tactical Pulse Flow
```
User Query
    ↓
[Query Parser] → Extract team names
    ↓
[Data Loader] → Match Database (49K+ matches)
    ↓
[Tactical Data Loader] → Tactical Stats (20 WC matches, 49 columns)
    ↓
[Metrics Calculator] → Statistics + Tactical Data
    ↓
[LLM (Granite)] → AI Insights with Tactical Analysis
    ↓
Analysis + Predictions with Formation/Possession/Shots
```

---

## 🎯 Tactical Data Integration

### What's New
FanPulse integrates **real tactical match data** from World Cup 2022 matches with **49 columns** including:
- Formations (e.g., 4-3-3, 5-3-2)
- Possession %
- Shots (total, on target, off target, blocked, inside/outside box)
- Expected Goals (xG)
- Passes (total, accuracy %)
- Defensive stats (tackles, interceptions, clearances)
- Set pieces (corners, offsides)
- Discipline (fouls, yellow/red cards)
- Goalkeeping (saves)

### Before vs After

**Before Integration:**
```
Win Rate: 45%
Goals: 10
Form: WWLDL

AI: "Brazil has an attacking style" ← Imaginary!
```

**After Integration:**
```
Win Rate: 45%
Goals: 10
Form: WWLDL
Formation: 4-3-3
Possession: 58%
Shots: 12.5 per match
Pass Accuracy: 85%

AI: "Brazil uses 4-3-3 with 58% possession and 12.5 shots" ← Real!
```

### Available Tactical Metrics
- **Formation Analysis**: Most common formation, tactical flexibility
- **Possession Analysis**: Average %, possession-based vs counter-attacking
- **Attacking Metrics**: Shots per match, shots on target %, xG, shot quality
- **Passing Metrics**: Total passes, pass accuracy %, build-up play style
- **Defensive Metrics**: Tackles, interceptions, clearances, defensive solidity
- **Set Pieces**: Corners won, offside trap effectiveness
- **Discipline**: Fouls committed, yellow/red cards, aggressive play style

---

## 🧪 Testing & Demo Scenarios

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

### Test Tactical Pulse Flow

**Input Examples:**
```
Analyze Qatar's performance
Predict Qatar vs Ecuador
Show me statistics for Germany
What formation does Ecuador use?
```

**Expected Output:**
- Team statistics (win rate, form, etc.)
- Tactical data (formation, possession, shots)
- Match predictions with probabilities
- AI-generated tactical insights

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

## 🎬 Real-Time Match Scenarios

### Scenario 1: Live VAR Decision

**Context:** Brazil vs Argentina (67th minute) - Goal disallowed after VAR review

**User Query:**
```
"The referee just disallowed Brazil's goal in the 67th minute after VAR review. 
The player looked onside to me. Can you explain why this decision was made?"
```

**Expected Response:**
```
According to FIFA Law 11, a player is in an offside position if any part of their 
head, body, or feet is in the opponents' half (excluding the halfway line) and 
closer to the opponents' goal line than both the ball and the second-last opponent.

In this case, VAR determined that the Brazilian player's shoulder was ahead of 
the last defender when the pass was made, placing them in an offside position. 
Even though it may have appeared close in real-time, the VAR technology provides 
precise measurements to ensure accurate decisions.

Source: Laws of the Game 2026/27, Law 11 - Offside
```

### Scenario 2: Tactical Formation Change

**Context:** Germany vs France (Half-time) - Germany switches from 4-3-3 to 4-4-2

**User Query:**
```
"Germany just changed their formation from 4-3-3 to 4-4-2 at half-time. 
They're losing 1-0. What does this tactical change mean?"
```

**Expected Response:**
```
Germany's switch from 4-3-3 to 4-4-2 indicates a more defensive and compact approach:

**Formation Analysis:**
- **4-3-3 (First Half):** Attacking formation with width, 3 forwards
- **4-4-2 (Second Half):** More balanced, 4 midfielders for control

**Strategic Implications:**
1. **Defensive Solidity:** Extra midfielder provides better coverage
2. **Counter-Attack Focus:** Two strikers can exploit French high line
3. **Midfield Control:** 4 midfielders can win back possession more effectively

**Historical Context:**
Based on 49,329 historical matches, teams trailing 1-0 at half-time who switch 
to 4-4-2 have a 34% chance of equalizing or winning.

**Prediction:** This tactical adjustment suggests Germany is prioritizing 
defensive stability while maintaining counter-attacking threat.
```

### Scenario 3: Team Analysis with Tactical Data

**User Query:**
```
"Analyze Qatar's tactical approach"
```

**Expected Output:**
```
📊 Team Performance Analysis with Tactical Data

Team: Qatar
Matches Analyzed: 2

Key Statistics:
- Win Rate: 0%
- Recent Form: LL (Score: 0/100)
- Goals Scored: 0
- Goals Conceded: 4

Tactical Statistics:
- Most Used Formation: 5-3-2
- Average Possession: 46%
- Average Shots: 7.5 per match
- Average Pass Accuracy: 81%

AI Tactical Insights:
Qatar employs a defensive 5-3-2 formation with 46% possession, indicating 
a counter-attacking style. With 7.5 shots per match and 81% pass accuracy, 
they prioritize defensive solidity over attacking dominance...
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
python scripts/build_var_lens_vectorstore.py
```

### Issue 4: Match data not loading
**Check:**
```bash
# Verify files exist
ls data/match_data/results.csv
ls data/match_data/tactical_stats.csv

# Check file sizes
du -h data/match_data/*.csv
```

### Issue 5: Slow responses
**Solution:** Check Ollama is running and Granite model is loaded

### Issue 6: Wrong agent selected
**Solution:** Refine query with more specific keywords

---

## 🎬 Demo Workflow for IBM Challenge

### 1. Start Services
```bash
ollama serve
langflow run
```

### 2. Import Main Flow
- Import `fanpulse_main_flow.json`

### 3. Test Scenarios

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

### 4. Show Visual Flow
- Zoom out to show complete architecture
- Highlight routing logic
- Show data flow through nodes

### 5. Explain Key Features
- IBM Granite 4.1 8B integration
- Docling document processing
- Dynamic data ingestion
- Dual-agent architecture
- Real tactical data (49 columns)

---

## 📊 Performance Tips

### For Faster Response Times

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

## 🎯 Success Metrics

A successful demo should show:
- ✅ Query routing accuracy: >90%
- ✅ Response time: <2 seconds
- ✅ Answer relevance: High (based on correct agent selection)
- ✅ Source citations: Present for VAR queries
- ✅ AI insights: Present for tactical queries
- ✅ Tactical data: Real formations, possession, shots

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
   - Show real tactical data integration

5. **Emphasize Real-Time Capability:**
   - Instant responses during live matches
   - Intelligent routing
   - Explainable AI with rule-based explanations

---

## 🧪 Testing Checklist

### Before Demo:
- [ ] Ollama running (`ollama list`)
- [ ] Granite model available (`ollama list | grep granite`)
- [ ] LangFlow started (`langflow run`)
- [ ] Main flow imported
- [ ] Test query: "What is VAR?" (should work)
- [ ] Vector store exists
- [ ] Match data files exist

### During Demo:
- [ ] Show VAR decision scenario
- [ ] Show tactical change scenario
- [ ] Show complex query scenario
- [ ] Highlight routing logic
- [ ] Show response time
- [ ] Demonstrate source citations
- [ ] Show tactical data integration

---

## 📚 Additional Resources

- **Main Documentation**: `README.md`
- **Architecture**: `ARCHITECTURE.md`
- **API Reference**: `docs/langflow-integration-guide.md`
- **Scripts Guide**: `scripts/README.md`

---

**Ready to Demo! 🚀**

This demonstrates FanPulse's ability to provide instant, intelligent analysis 
during live World Cup matches, enhancing fan understanding and engagement with 
real tactical data and AI-powered insights.

For questions or issues:
- GitHub: https://github.com/babaksh/FanPulse
- Documentation: `docs/`