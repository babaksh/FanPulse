# FanPulse Scripts

This directory contains utility scripts for building, testing, and managing the FanPulse system.

## 🚀 Essential Scripts (Public)

### System Setup & Building

**`build_var_lens_vectorstore.py`**
- Builds the FAISS vector store from processed FIFA documents
- Usage: `python scripts/build_var_lens_vectorstore.py [--rebuild]`
- Required for VAR-Lens agent to function
- Creates 658 vectors from 7 FIFA/IFAB documents

**`test_complete_system.py`**
- Comprehensive end-to-end system validation
- Tests all components: imports, data files, Ollama, agents, orchestrator
- Usage: `python scripts/test_complete_system.py`
- Should show 7/7 tests passing when system is ready

---

## 🔧 Development Scripts (Local Only)

These scripts are used during development and are not included in the public repository (see `.gitignore`).

### Testing Scripts

- `test_ai_insights.py` - Tests AI-powered insights generation
- `test_data_loader.py` - Tests match data loading functionality
- `test_docling.py` - Tests Docling document processing
- `test_dynamic_tactical_pulse.py` - Tests dynamic match data ingestion
- `test_dynamic_var_lens.py` - Tests dynamic document ingestion
- `test_match_analyzer.py` - Tests match analysis functionality
- `test_orchestrator.py` - Tests query routing and orchestration
- `test_var_lens_rag.py` - Tests VAR-Lens RAG engine
- `test_var_lens_with_llm.py` - Tests VAR-Lens with LLM integration

### Setup & Configuration

- `check_api_keys.py` - Validates API keys and environment variables
- `check_setup.py` - Checks system setup and dependencies

### Ollama Testing

- `test_ollama_connection.py` - Tests Ollama API connectivity
- `quick_test_ollama.py` - Quick Ollama functionality test
- `show_llm_info.py` - Displays LLM model information
- `demo_ollama_usage.py` - Demonstrates Ollama usage

### Document Processing

- `process_fifa_docs.py` - Main document processing script
- `process_fifa_docs_simple.py` - Simplified document processing
- `process_fifa_docs_smart.py` - Smart document processing with chunking
- `process_large_pdf.py` - Handles large PDF files
- `process_var_protocol_only.py` - Processes only VAR protocol document
- `monitor_processing.py` - Monitors document processing progress

### Demo & Practice

- `demo_scenarios.py` - Interactive demo script for practicing presentations
  - 4 demo scenarios: VAR-Lens, Tactical Pulse, Predictions, Orchestrator
  - Menu-driven interface for easy testing
  - Formatted output for clear results

---

## 📋 Usage Examples

### Building Vector Store
```bash
# First time build
python scripts/build_var_lens_vectorstore.py

# Force rebuild
python scripts/build_var_lens_vectorstore.py --rebuild
```

### Testing System
```bash
# Complete system test
python scripts/test_complete_system.py

# Expected output: 7/7 tests passing
```

### Practice Demo (Local Only)
```bash
# Interactive demo scenarios
python scripts/demo_scenarios.py

# Select scenarios from menu:
# 1. VAR-Lens (Rules & Transparency)
# 2. Tactical Pulse (Team Analysis)
# 3. Match Prediction with AI
# 4. Orchestrator (Intelligent Routing)
# 5. Run All Scenarios
```

---

## 🔐 Security Note

All test scripts and development utilities are excluded from the public repository via `.gitignore` to:
- Keep the repository clean and focused
- Protect any local configurations or API keys
- Maintain professional presentation for IBM Challenge submission

---

## 📚 Related Documentation

- **System Architecture:** `ARCHITECTURE.md`
- **Setup Guide:** `README.md`
- **LangFlow Setup:** `docs/LANGFLOW_SETUP.md`
- **Ollama Setup:** `OLLAMA_SETUP.md`

---

## 🎯 For IBM Challenge Reviewers

The essential scripts for running FanPulse are:
1. `build_var_lens_vectorstore.py` - Build the knowledge base
2. `test_complete_system.py` - Validate system readiness

All other functionality is accessible through:
- Python API: `src/orchestrator/fanpulse_orchestrator.py`
- LangFlow workflows: `langflow_workflows/`
- FastAPI endpoints: `src/api/main.py`

---

**Made with Bob** 🤖