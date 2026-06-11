# FanPulse LangFlow Workflows

This directory contains LangFlow workflow definitions for the FanPulse system.

## 📁 Files

### Main Workflows
- **`fanpulse_main_flow.json`** - Main orchestrator workflow that routes queries to appropriate agents
- **`var_lens_flow.json`** - VAR-Lens agent workflow for FIFA rules and VAR decisions
- **`tactical_pulse_flow.json`** - Tactical Pulse agent workflow for match analysis and predictions

### Supporting Files
- **`README.md`** - This file
- **`IMPORT_GUIDE.md`** - Step-by-step guide to import workflows into LangFlow

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
[Metrics Calculator] → Statistics
    ↓
[LLM (Granite)] → AI Insights
    ↓
Analysis + Predictions
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

### Example 2: Team Analysis
```
Input: "Analyze Brazil's recent performance"
Flow: Main → Tactical Pulse
Output: Statistics, form, and AI insights
```

### Example 3: Match Prediction
```
Input: "Predict Brazil vs Argentina"
Flow: Main → Tactical Pulse
Output: Win probabilities and match preview
```

## 🎯 Demo Scenarios

See `docs/demo-scenarios.md` for complete demo scripts and test cases.

## 🔗 Related Documentation

- **Architecture**: `ARCHITECTURE.md`
- **Setup Guide**: `docs/langflow-integration-guide.md`
- **API Documentation**: `README.md`

## 🐛 Troubleshooting

### Issue: Workflow won't import
**Solution**: Ensure you're using LangFlow version 1.0.0 or higher

### Issue: LLM not responding
**Solution**: Check Ollama is running: `ollama list`

### Issue: Vector store not found
**Solution**: Run data processing: `python scripts/process_documents.py`

## 📞 Support

For issues or questions:
- GitHub: https://github.com/babaksh/FanPulse
- Documentation: `docs/`