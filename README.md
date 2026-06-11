# FanPulse ⚽🤖

**AI-Powered Football Analysis for the 2026 FIFA World Cup**

FanPulse is an intelligent dual-agent system that helps fans understand and experience football matches through explainable AI. Built for the IBM Skills Build AI Builders Challenge (June 2026).

[![IBM Granite](https://img.shields.io/badge/IBM-Granite_4.1_8B-blue)](https://www.ibm.com/granite)
[![Docling](https://img.shields.io/badge/IBM-Docling-green)](https://github.com/DS4SD/docling)
[![Langflow](https://img.shields.io/badge/Langflow-Orchestration-purple)](https://www.langflow.org/)
[![IBM Bob](https://img.shields.io/badge/IBM-Bob-orange)](https://bob.ibm.com)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Overview

FanPulse combines two specialized AI agents with intelligent orchestration to provide comprehensive football analysis:

### 🔍 **VAR-Lens Agent**
Explains Video Assistant Referee (VAR) decisions using official FIFA rules and regulations.

**Features:**
- 📚 RAG-powered explanations from 7 FIFA/IFAB documents
- 🎯 658-vector FAISS knowledge base
- 🤖 IBM Granite 4.1 8B via Ollama
- 📖 Clear, rule-based explanations with source citations
- 🔄 Dynamic document ingestion for real-time updates

### ⚽ **Tactical Pulse Agent**
Analyzes tactical shifts, match dynamics, and team performance with AI insights.

**Features:**
- 📊 49,329 historical matches analyzed
- 🏆 336 teams, 198 tournaments
- 📈 Advanced statistical analysis
- 🎲 Match outcome predictions with AI-powered insights
- 🔄 Dynamic match data ingestion

### 🎭 **FanPulse Orchestrator**
Intelligent query routing system that directs questions to the appropriate agent.

**Features:**
- 🧠 Dual classification: keyword matching + LLM-based intent detection
- 🎯 Automatic agent selection based on query type
- 📊 Unified response formatting
- ⚡ Lazy agent initialization for performance
- 🔄 System status monitoring

---

## 🔧 IBM Technologies Integration

This project leverages multiple IBM technologies as required by the challenge:

### 1. **IBM Granite 4.1 8B** ⭐
- **Primary LLM** for both agents via Ollama
- Generates natural language explanations of VAR decisions
- Provides AI-powered tactical analysis insights
- Powers the orchestrator's intent classification
- 5.3 GB model running locally for fast inference

### 2. **Docling** (Document Processing)
- Converted 7 FIFA/IFAB PDF rulebooks to clean Markdown format
- Processed 450 KB of official football regulations
- Enabled efficient text extraction for RAG pipeline
- Output stored in `data/processed_documents/`
- Supports dynamic document ingestion

### 3. **Langflow** (Visual Orchestration)
- Created 3 complete workflow templates:
  - `fanpulse_main_flow.json` - Main orchestrator with routing
  - `var_lens_flow.json` - VAR-Lens RAG workflow
  - `tactical_pulse_flow.json` - Tactical analysis workflow
- Visual workflow builder for easy customization
- JSON flow definitions in `langflow_workflows/`
- Enables no-code/low-code agent deployment

### 4. **IBM Bob** (AI Coding Assistant)
- Used throughout development for code generation
- Assisted with debugging and optimization
- Helped create comprehensive documentation
- Accelerated development of 13,000+ lines of code

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FanPulse System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           FanPulse Orchestrator                      │  │
│  │  • Query Router (Keyword + LLM Classification)       │  │
│  │  • Response Handler (Unified Formatting)             │  │
│  │  • Lazy Agent Initialization                         │  │
│  └────────────────┬─────────────────┬───────────────────┘  │
│                   │                 │                       │
│  ┌────────────────▼──────┐   ┌─────▼──────────────────┐   │
│  │   VAR-Lens Agent      │   │  Tactical Pulse Agent  │   │
│  ├───────────────────────┤   ├────────────────────────┤   │
│  │ • RAG Engine          │   │ • Data Loader          │   │
│  │ • FAISS Vector Store  │   │ • Metrics Calculator   │   │
│  │ • 658 Vectors         │   │ • Match Analyzer       │   │
│  │ • 7 FIFA Documents    │   │ • 49K+ Matches         │   │
│  │ • Dynamic Ingestion   │   │ • Dynamic Ingestion    │   │
│  └───────────┬───────────┘   └────────┬───────────────┘   │
│              │                        │                    │
│              └────────────┬───────────┘                    │
│                           │                                │
│                 ┌─────────▼─────────┐                      │
│                 │  IBM Granite      │                      │
│                 │  4.1 8B (Ollama)  │                      │
│                 └───────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Ollama** (for IBM Granite 4.1 8B)
- **Git**
- **8GB+ RAM** (for running Granite model)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/babaksh/FanPulse.git
cd FanPulse

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-llm.txt

# 4. Install and setup Ollama
# See OLLAMA_SETUP.md for detailed instructions

# 5. Pull IBM Granite model
ollama pull granite4.1:8b

# 6. Build vector store
python scripts/build_var_lens_vectorstore.py

# 7. Test the system
python scripts/test_complete_system.py
```

### Expected Output

```
======================================================================
FanPulse Complete System Test
======================================================================

[PASS] Module Imports (8/8)
[PASS] Data Files (4/4)
[PASS] Ollama Connection
[PASS] VAR-Lens Agent
[PASS] Tactical Pulse Agent
[PASS] Orchestrator
[PASS] Dynamic Features

Total: 7/7 tests passed ✅
```

---

## 🎮 Usage Examples

### Using the Orchestrator (Recommended)

```python
from src.orchestrator.fanpulse_orchestrator import FanPulseOrchestrator

# Initialize orchestrator
orchestrator = FanPulseOrchestrator()

# Ask VAR-related questions (automatically routed to VAR-Lens)
result = orchestrator.query("What is the VAR protocol for offside decisions?")
print(result['answer'])
print(f"Agent used: {result['agent']}")

# Ask tactical questions (automatically routed to Tactical Pulse)
result = orchestrator.query("Analyze Brazil's recent performance")
print(result['answer'])

# Predict matches
prediction = orchestrator.predict_match("Brazil", "Argentina")
print(f"Prediction: {prediction['prediction']}")
print(f"Analysis: {prediction['analysis']}")

# Analyze teams
analysis = orchestrator.analyze_team("Germany")
print(f"Win Rate: {analysis['win_rate']}%")
print(f"Recent Form: {analysis['recent_form']}")
```

### Direct Agent Usage

#### VAR-Lens Agent

```python
from src.agents.var_lens.rag_engine import VARLensRAG

# Initialize
rag = VARLensRAG()
rag.setup()  # Loads vector store
rag.setup_qa_chain(provider="ollama", model_name="granite4.1:8b")

# Query
result = rag.query("Explain handball rules in the penalty area")
print(result['answer'])
print(f"Sources: {result['sources']}")
```

#### Tactical Pulse Agent

```python
from src.agents.tactical_pulse.match_analyzer import MatchAnalyzer

# Initialize
analyzer = MatchAnalyzer()

# Analyze team
analysis = analyzer.analyze_team("Spain", num_matches=10)
print(f"Win Rate: {analysis['statistics']['win_rate']:.1%}")
print(f"Goals Scored: {analysis['statistics']['goals_scored']}")

# Predict match
prediction = analyzer.predict_match("France", "England")
print(f"Predicted Winner: {prediction['prediction']['winner']}")
```

---

## 🎨 LangFlow Integration

FanPulse includes ready-to-use LangFlow workflows:

```bash
# 1. Install LangFlow
pip install langflow

# 2. Start LangFlow
langflow run

# 3. Import workflows
# Navigate to http://localhost:7860
# Import from: langflow_workflows/fanpulse_main_flow.json
```

**Available Workflows:**
- `fanpulse_main_flow.json` - Complete orchestrator with routing
- `var_lens_flow.json` - VAR-Lens RAG pipeline
- `tactical_pulse_flow.json` - Tactical analysis pipeline

See [`docs/LANGFLOW_SETUP.md`](docs/LANGFLOW_SETUP.md) for detailed instructions.

---

## 📚 Documentation

### Setup & Configuration
- **[Ollama Setup](OLLAMA_SETUP.md)** - Install and configure Ollama + Granite
- **[LangFlow Setup](docs/LANGFLOW_SETUP.md)** - Visual workflow integration
- **[Repository Structure](docs/REPOSITORY_STRUCTURE.md)** - Project organization

### Architecture & Design
- **[System Architecture](ARCHITECTURE.md)** - Complete system design
- **[Tactical Pulse Design](docs/tactical-pulse-design.md)** - Agent architecture
- **[VAR-Lens Setup](docs/var-lens-setup-guide.md)** - RAG implementation

### Scripts & Tools
- **[Scripts README](scripts/README.md)** - Available scripts and usage
- **[Demo Scenarios](docs/demo-scenarios.md)** - Example use cases

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.11+** - Primary language
- **LangChain** - RAG framework
- **FAISS** - Vector database (658 vectors)
- **Pandas** - Data processing (49K+ matches)
- **Ollama** - Local LLM inference

### IBM Technologies
- **IBM Granite 4.1 8B** - Primary LLM via Ollama
- **Docling** - Document processing (7 FIFA PDFs → Markdown)
- **Langflow** - Visual workflow orchestration (3 workflows)
- **IBM Bob** - AI coding assistant (13K+ lines generated)

### Key Libraries
- `langchain` - RAG pipeline
- `langchain-community` - Community integrations
- `sentence-transformers` - Embeddings (all-MiniLM-L6-v2)
- `faiss-cpu` - Vector similarity search
- `ollama` - Local LLM API

---

## 📊 Project Statistics

### Code & Documentation
- **Lines of Code**: ~13,000
- **Python Modules**: 20+
- **Documentation**: 10+ files (~4,000 lines)
- **LangFlow Workflows**: 3 complete flows

### Data & Models
- **FIFA Documents**: 7 (450 KB processed)
- **Vector Store**: 658 vectors (1.5 MB)
- **Match Dataset**: 49,329 matches (3.8 MB)
- **Teams**: 336
- **Tournaments**: 198
- **LLM**: Granite 4.1 8B (5.3 GB)

### Testing
- **System Tests**: 7/7 passing ✅
- **Component Tests**: All passing ✅
- **Integration Tests**: All passing ✅

---

## 🎯 IBM Challenge Criteria

### ✅ Technical Execution
- **IBM Granite 4.1 8B** as primary LLM via Ollama
- **Docling** for document processing (7 FIFA PDFs)
- **LangFlow** workflows for visual orchestration
- Functional RAG system with FAISS
- Comprehensive test coverage (7/7 tests passing)
- Production-ready architecture

### ✅ Innovation
- **Dual-agent architecture** with intelligent orchestration
- **Dynamic data ingestion** for both agents
- **Hybrid query routing** (keyword + LLM classification)
- **AI-powered insights** using Granite for analysis
- **Lazy initialization** for performance optimization

### ✅ Challenge Fit
- Addresses **fan understanding** of VAR decisions
- Provides **tactical explainability** for matches
- Enhances **trust and transparency** in officiating
- Improves **accessibility** through natural language
- Real-world applicability for World Cup 2026

### ✅ Implementation & Feasibility
- **Modular, extensible design** with clear separation of concerns
- **Scalable architecture** supporting multiple agents
- **Well-documented** with comprehensive guides
- **Easy to deploy** with simple setup process
- **Local-first** approach (no cloud dependencies)

---

## 📁 Project Structure

```
FanPulse/
├── src/
│   ├── agents/
│   │   ├── var_lens/
│   │   │   ├── rag_engine.py          # RAG implementation
│   │   │   └── llm_providers.py       # LLM abstraction
│   │   └── tactical_pulse/
│   │       ├── data_loader.py         # Match data loading
│   │       ├── metrics_calculator.py  # Statistical analysis
│   │       └── match_analyzer.py      # Team analysis
│   ├── orchestrator/
│   │   ├── fanpulse_orchestrator.py   # Main orchestrator
│   │   ├── query_router.py            # Query routing
│   │   └── response_handler.py        # Response formatting
│   └── api/
│       ├── main.py                    # FastAPI app
│       └── routes/                    # API endpoints
├── data/
│   ├── processed_documents/           # FIFA docs (Markdown)
│   ├── vector_stores/                 # FAISS indices
│   └── match_data/
│       └── results.csv                # 49K+ matches
├── scripts/
│   ├── build_var_lens_vectorstore.py  # Build vector store
│   ├── test_complete_system.py        # System validation
│   └── README.md                      # Scripts documentation
├── langflow_workflows/
│   ├── fanpulse_main_flow.json        # Main orchestrator
│   ├── var_lens_flow.json             # VAR-Lens workflow
│   ├── tactical_pulse_flow.json       # Tactical workflow
│   ├── README.md                      # Workflows overview
│   └── IMPORT_GUIDE.md                # Import instructions
├── docs/
│   ├── LANGFLOW_SETUP.md              # LangFlow guide
│   ├── REPOSITORY_STRUCTURE.md        # Project organization
│   ├── demo-scenarios.md              # Usage examples
│   ├── llm-setup-guide.md             # LLM configuration
│   ├── processed-documents-guide.md   # Document processing
│   ├── tactical-pulse-design.md       # Agent design
│   └── var-lens-setup-guide.md        # VAR-Lens setup
├── requirements.txt                   # Core dependencies
├── requirements-llm.txt               # LLM dependencies
├── .env.example                       # Environment template
├── ARCHITECTURE.md                    # System architecture
├── OLLAMA_SETUP.md                    # Ollama setup guide
├── LICENSE                            # MIT License
├── NOTICE                             # Attribution
└── README.md                          # This file
```

See [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md) for detailed explanation of public vs. private files.

---

## 🧪 Testing

### Quick System Test

```bash
# Complete system validation (7 tests)
python scripts/test_complete_system.py
```

**Expected Output:**
```
[PASS] Module Imports (8/8)
[PASS] Data Files (4/4)
[PASS] Ollama Connection
[PASS] VAR-Lens Agent
[PASS] Tactical Pulse Agent
[PASS] Orchestrator
[PASS] Dynamic Features

Total: 7/7 tests passed ✅
Time: ~15s
```

### Building Vector Store

```bash
# First time build
python scripts/build_var_lens_vectorstore.py

# Force rebuild
python scripts/build_var_lens_vectorstore.py --rebuild
```

---

## 🤝 Contributing

This project was built for the IBM Skills Build AI Builders Challenge (June 2026). While primarily a competition entry, contributions, issues, and feature requests are welcome!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python scripts/test_complete_system.py`
5. Submit a pull request

---

## 📝 License & Copyright

**Copyright (c) 2026 Babak Shahifar**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project was created specifically for the **IBM Skills Build AI Builders Challenge (June 2026)** and is the original work of Babak Shahifar. See [NOTICE](NOTICE) file for additional information.

---

## 🙏 Acknowledgments

- **IBM Skills Build** - For hosting the AI Builders Challenge
- **IBM Granite Team** - For the powerful Granite 4.1 8B model
- **Docling Team** - For excellent document processing capabilities
- **Langflow Community** - For visual AI workflow orchestration
- **Ollama Team** - For making local LLM inference accessible
- **FIFA/IFAB** - For official rules and regulations
- **Kaggle** - For the international football results dataset

---

## 👤 Author

**Babak Shahifar**
- GitHub: [@babaksh](https://github.com/babaksh)
- Project: [FanPulse](https://github.com/babaksh/FanPulse)
- Challenge: IBM Skills Build AI Builders Challenge (June 2026)

---

## 📞 Contact

For questions or feedback about this project:
- **GitHub Issues**: [Create an issue](https://github.com/babaksh/FanPulse/issues)
- **Challenge Platform**: [IBM Skills Build](https://ibmskillsbuildchallenge-hub.bemyapp.com/)

---

## 🎉 Built with ❤️ for the 2026 FIFA World Cup

**FanPulse** - Making football more accessible and understandable for fans worldwide through explainable AI.

### Key Features:
- 🔍 **Transparent VAR Explanations** - Understand referee decisions
- ⚽ **Tactical Insights** - Analyze team performance with AI
- 🎭 **Intelligent Routing** - Automatic query classification
- 🚀 **Easy Setup** - Local-first with Ollama
- 📊 **Comprehensive Data** - 49K+ matches, 7 FIFA documents
- 🤖 **Powered by IBM Granite** - State-of-the-art LLM

---

**Made with Bob** 🤖 | **IBM Skills Build AI Builders Challenge 2026** 🏆

*Last Updated: June 11, 2026*
