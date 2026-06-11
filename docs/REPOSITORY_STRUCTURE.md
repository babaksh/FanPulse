# FanPulse Repository Structure

This document explains which files are included in the public GitHub repository and which are kept local for development.

## 📦 Public Repository Files

These files are committed to GitHub and visible to IBM Challenge reviewers and other users.

### Core Application Code
```
src/
├── agents/
│   ├── var_lens/
│   │   ├── rag_engine.py          # VAR-Lens RAG implementation
│   │   └── llm_providers.py       # LLM provider abstraction
│   └── tactical_pulse/
│       ├── data_loader.py         # Match data loading
│       ├── match_analyzer.py      # Team analysis
│       └── metrics_calculator.py  # Statistical calculations
├── orchestrator/
│   ├── fanpulse_orchestrator.py   # Main orchestrator
│   ├── query_router.py            # Intelligent query routing
│   └── response_handler.py        # Response formatting
└── api/
    ├── main.py                    # FastAPI application
    └── routes/                    # API endpoints
```

### Essential Scripts
```
scripts/
├── build_var_lens_vectorstore.py  # Build vector store
├── test_complete_system.py        # System validation
└── README.md                      # Scripts documentation
```

### LangFlow Workflows
```
langflow_workflows/
├── fanpulse_main_flow.json        # Main orchestrator workflow
├── var_lens_flow.json             # VAR-Lens workflow
├── tactical_pulse_flow.json       # Tactical Pulse workflow
├── README.md                      # Workflows overview
└── IMPORT_GUIDE.md                # Import instructions
```

### Documentation
```
docs/
├── LANGFLOW_SETUP.md              # LangFlow setup guide
├── demo-scenarios.md              # Demo scenarios
├── llm-setup-guide.md             # LLM setup guide
├── processed-documents-guide.md   # Document processing guide
├── tactical-pulse-design.md       # Tactical Pulse design
├── var-lens-setup-guide.md        # VAR-Lens setup guide
└── REPOSITORY_STRUCTURE.md        # This file
```

### Data Files (Processed)
```
data/
├── processed_documents/           # Processed FIFA documents (7 files)
│   ├── *.md                       # Markdown versions
│   └── processing_summary.json   # Processing metadata
└── match_data/
    └── results.csv                # Historical match data (49K+ matches)
```

### Configuration & Setup
```
.env.example                       # Environment variables template
.gitignore                         # Git ignore rules
requirements.txt                   # Python dependencies
requirements-llm.txt               # LLM-specific dependencies
pyrightconfig.json                 # Python type checking config
```

### Project Documentation
```
README.md                          # Main project documentation
ARCHITECTURE.md                    # System architecture
LICENSE                            # MIT License
NOTICE                             # Attribution notices
OLLAMA_SETUP.md                    # Ollama setup guide
```

---

## 🔒 Local Development Files (Not in GitHub)

These files are excluded via `.gitignore` and kept local for development purposes.

### Development & Test Scripts
```
scripts/
├── test_*.py                      # All test scripts (12 files)
├── process_*.py                   # Document processing scripts (6 files)
├── check_*.py                     # Setup validation scripts (2 files)
├── demo_*.py                      # Demo practice scripts (2 files)
├── show_llm_info.py              # LLM information display
├── quick_test_ollama.py          # Quick Ollama test
└── monitor_processing.py         # Processing monitor
```

### Personal Documentation
```
docs/
├── PERSIAN_GUIDE.md              # Persian language guide
├── OLLAMA_SETUP_FA.md            # Persian Ollama setup
├── DEMO_GUIDE_FA.md              # Persian demo guide
├── docling-workflow.md           # Docling workflow notes
├── langflow-integration-guide.md # LangFlow integration notes
├── langflow-var-lens-guide.md    # VAR-Lens LangFlow guide
└── langflow-quick-start.md       # LangFlow quick start
```

### Generated Data
```
data/
├── vector_stores/                # FAISS vector stores (can be rebuilt)
├── temp_chunks/                  # Temporary PDF chunks
└── raw_documents/                # Original PDF files
```

### Environment & IDE
```
venv/                             # Python virtual environment
.vscode/                          # VS Code settings
.env                              # Environment variables (secrets)
*.log                             # Log files
__pycache__/                      # Python cache
*.pyc                             # Compiled Python files
```

---

## 🎯 Why This Structure?

### Public Files Include:
✅ **Core functionality** - Everything needed to run FanPulse
✅ **Documentation** - Setup guides and architecture
✅ **Workflows** - LangFlow integration files
✅ **Essential scripts** - Build and test utilities
✅ **Processed data** - Ready-to-use documents and match data

### Local Files Exclude:
❌ **Development tools** - Test scripts and utilities
❌ **Personal notes** - Persian guides and workflow notes
❌ **Generated data** - Vector stores (can be rebuilt)
❌ **Secrets** - API keys and environment variables
❌ **IDE settings** - Personal development preferences

---

## 📊 Repository Statistics

### Public Repository:
- **Source Code:** ~13,000 lines
- **Documentation:** ~3,000 lines
- **Scripts:** 2 essential scripts
- **Workflows:** 3 LangFlow JSON files
- **Data:** 7 processed documents + 49K matches

### Local Development:
- **Test Scripts:** 12 files
- **Processing Scripts:** 6 files
- **Personal Docs:** 7 files
- **Generated Data:** Vector stores + temp files

---

## 🚀 For New Users

To get started with FanPulse:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/babaksh/FanPulse.git
   cd FanPulse
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-llm.txt
   ```

3. **Setup Ollama:**
   ```bash
   # Follow OLLAMA_SETUP.md
   ollama pull granite4.1:8b
   ```

4. **Build vector store:**
   ```bash
   python scripts/build_var_lens_vectorstore.py
   ```

5. **Test system:**
   ```bash
   python scripts/test_complete_system.py
   ```

All necessary files are included in the public repository!

---

## 🔐 Security Notes

- **No API keys** are committed to the repository
- **No personal data** is included
- **No credentials** are stored in code
- Use `.env.example` as template for your `.env` file

---

## 📞 Questions?

For questions about the repository structure or missing files:
- Check `README.md` for setup instructions
- Review `ARCHITECTURE.md` for system design
- See `docs/LANGFLOW_SETUP.md` for LangFlow integration

---

**Made with Bob** 🤖