# FanPulse LangFlow Workflows

This directory contains LangFlow workflow definitions for the FanPulse system.

## 📁 Files

### Main Workflows
- **`fanpulse_main_flow.json`** - Main orchestrator workflow that routes queries to appropriate agents
- **`var_lens_flow.json`** - VAR-Lens agent workflow for FIFA rules and VAR decisions
- **`tactical_pulse_flow.json`** - Tactical Pulse agent workflow for match analysis and predictions

### Documentation
- **`README.md`** - This file (quick overview)
- **`LANGFLOW_GUIDE.md`** - Complete guide with import instructions, configuration, testing, and demo scenarios

## 🚀 Quick Start

### 1. Start LangFlow
```bash
langflow run
```

### 2. Open LangFlow UI
Navigate to: `http://localhost:7860`

### 3. Import Workflow
1. Click "Import" button (top right)
2. Select one of the JSON files from this directory
3. The workflow will load with all components configured

## 📊 Workflow Overview

### Main Flow Architecture
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
[Tactical Data Loader] → Tactical Stats (20 World Cup matches)
    ↓
[Metrics Calculator] → Statistics + Tactical Data
    ↓
[LLM (Granite)] → AI Insights with Tactical Analysis
    ↓
Analysis + Predictions with Formation/Possession/Shots
```

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

### LangFlow Settings
- **LLM Provider**: Ollama
- **Model**: IBM Granite 4.1 8B
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **Chunk Size**: 1000
- **Chunk Overlap**: 200

## 📝 Usage Examples

### Example 1: VAR Decision Query
```
Input: "What is the offside rule in soccer?"
Flow: Main → VAR-Lens
Output: Detailed explanation with FIFA rule references
```

### Example 2: Team Analysis with Tactical Data
```
Input: "Analyze Qatar's recent performance"
Flow: Main → Tactical Pulse
Output: Statistics, form, tactical data (formation, possession, shots), and AI insights

Sample Output:
- Win Rate: 20%
- Formation: 5-3-2 (defensive)
- Possession: 46% (balanced)
- Shots: 7.5 per match
- AI Analysis: "Qatar uses a defensive 5-3-2 formation..."
```

### Example 3: Match Prediction with Tactical Preview
```
Input: "Predict Qatar vs Ecuador"
Flow: Main → Tactical Pulse
Output: Win probabilities, tactical matchup, and AI match preview

Sample Output:
- Predicted Score: 0-2
- Formations: Qatar 5-3-2 vs Ecuador 4-4-2
- Tactical Battle: Defensive vs Balanced
- AI Preview: "Qatar's defensive setup will face Ecuador's balanced approach..."
```

## 📚 Complete Documentation

For detailed instructions on:
- Importing workflows into LangFlow
- Configuration and setup
- Testing scenarios
- Demo workflows
- Real-time match scenarios
- Tactical data integration
- Troubleshooting

**See:** [`LANGFLOW_GUIDE.md`](LANGFLOW_GUIDE.md) - Complete 545-line guide with everything you need

## 🔗 Related Documentation

- **Architecture**: `ARCHITECTURE.md`
- **Setup Guide**: `README.md`
- **Scripts Guide**: `scripts/README.md`

## 📞 Support

For issues or questions:
- GitHub: https://github.com/babaksh/FanPulse
- Complete Guide: [`LANGFLOW_GUIDE.md`](LANGFLOW_GUIDE.md)