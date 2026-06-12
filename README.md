# FanPulse ⚽🤖

**AI-Powered Football Analysis for FIFA World Cup 2026**

FanPulse helps fans understand VAR decisions and tactical changes during matches using explainable AI. Built with IBM Granite, Docling, LangFlow, and IBM Bob for the IBM Skills Build AI Builders Challenge (June 2026).

[![IBM Granite](https://img.shields.io/badge/IBM-Granite_4.1_8B-blue)](https://www.ibm.com/granite)
[![Docling](https://img.shields.io/badge/IBM-Docling-green)](https://github.com/DS4SD/docling)
[![Langflow](https://img.shields.io/badge/Langflow-Orchestration-purple)](https://www.langflow.org/)
[![IBM Bob](https://img.shields.io/badge/IBM-Bob_AI_Assistant-orange)](https://www.ibm.com/bob)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What is FanPulse?

Two specialized AI agents working together to enhance the football viewing experience:

### 🔍 VAR-Lens Agent
Explains Video Assistant Referee (VAR) decisions using official FIFA rules.
- 📚 658-vector knowledge base from 7 FIFA/IFAB documents
- 🤖 Powered by IBM Granite 4.1 8B via Ollama
- 📖 Clear explanations with source citations
- 🔄 RAG (Retrieval Augmented Generation) pipeline

### ⚽ Tactical Pulse Agent  
Analyzes team performance and tactical changes with real match data.
- 📊 49,329 historical matches + 20 World Cup 2022 matches
- 🎯 49 tactical columns: formations, possession, shots, passes, xG
- 🤖 AI-powered insights using IBM Granite
- 📈 Match predictions and team analysis

### 🎭 Smart Orchestrator
Routes your questions to the right agent automatically using keyword matching and LLM classification.

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Python 3.11+
python --version

# Install Ollama
# Windows: Download from https://ollama.com
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Install Dependencies
```bash
# Clone repository
git clone https://github.com/babaksh/FanPulse.git
cd FanPulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Setup IBM Granite
```bash
# Pull Granite model (5.3 GB)
ollama pull granite4.1:8b

# Verify installation
ollama list
```

### 4. Build Knowledge Base
```bash
# Build VAR-Lens vector store (658 vectors from FIFA documents)
python scripts/build_var_lens_vectorstore.py
```

### 5. Test System
```bash
# Run complete system test (should show 8/8 passing)
python scripts/test_complete_system.py
```

---

## 💻 Usage

### Option 1: LangFlow (Visual Workflows) - Recommended

```bash
# Start LangFlow
langflow run

# Open browser: http://localhost:7860
# Import: langflow_workflows/fanpulse_main_flow.json
```

**Try these queries:**
- "What is the offside rule?" → VAR-Lens explains with FIFA sources
- "Analyze Qatar's tactical approach" → Tactical Pulse with formation (5-3-2), possession (46%), shots (7.5)
- "Predict Qatar vs Ecuador" → Match preview with tactical matchup

📖 **Complete Guide:** [`langflow_workflows/LANGFLOW_GUIDE.md`](langflow_workflows/LANGFLOW_GUIDE.md)

### Option 2: Python API

```python
from src.orchestrator import FanPulseOrchestrator

# Initialize
orchestrator = FanPulseOrchestrator()

# Ask a question
result = orchestrator.process_query("What is VAR?")
print(result['answer'])
```

---

## 📊 Key Features

### Real Tactical Data Integration
- **49 columns** of tactical statistics from World Cup 2022
- Formations (4-3-3, 5-3-2, 4-4-2, etc.)
- Possession percentages
- Shot patterns (total, on target, inside/outside box)
- Pass accuracy and completion rates
- Defensive metrics (tackles, interceptions, blocks)
- Set pieces & discipline (corners, fouls, cards)
- Expected Goals (xG) and advanced metrics

### Intelligent Query Routing
- Keyword matching for fast classification
- LLM-based intent classification for complex queries
- Automatic agent selection
- Unified response formatting

### Dynamic Data Ingestion
- Add new FIFA documents on-the-fly
- Fetch live match data from API-Football
- Real-time knowledge base updates
- Automatic duplicate detection

---

## 🏗️ Project Structure

```
FanPulse/
├── src/                           # Source code
│   ├── agents/
│   │   ├── var_lens/              # VAR decision explanations
│   │   │   ├── rag_engine.py      # RAG pipeline with FAISS
│   │   │   └── llm_providers.py   # LLM abstraction layer
│   │   └── tactical_pulse/        # Match analysis
│   │       ├── data_loader.py     # Match data loading
│   │       ├── match_analyzer.py  # Team analysis & predictions
│   │       └── metrics_calculator.py  # Statistical calculations
│   └── orchestrator/              # Query routing & coordination
│       ├── fanpulse_orchestrator.py   # Main orchestrator
│       ├── query_router.py        # Smart routing logic
│       └── response_handler.py    # Response formatting
│
├── langflow_workflows/            # Visual workflow definitions
│   ├── fanpulse_main_flow.json    # Main orchestrator workflow
│   ├── var_lens_flow.json         # VAR-Lens workflow
│   ├── tactical_pulse_flow.json   # Tactical Pulse workflow
│   ├── LANGFLOW_GUIDE.md          # Complete guide (545 lines)
│   └── README.md
│
├── scripts/                       # Utility scripts
│   ├── build_var_lens_vectorstore.py  # Build FAISS vector store
│   ├── fetch_match_data.py        # Unified data fetching from API-Football
│   ├── test_complete_system.py    # System validation (8 tests)
│   └── README.md
│
├── data/                          # Data files (58.5 MB total - included in repo)
│   ├── raw_documents/             # 7 FIFA/IFAB PDFs (~15 MB)
│   ├── processed_documents/       # 7 FIFA/IFAB Markdown files (~5 MB)
│   ├── vector_stores/             # FAISS index - 658 vectors (~20 MB)
│   │   └── var_lens/              # VAR-Lens vector store
│   ├── match_data/                # Match datasets (~15 MB)
│   │   ├── results.csv            # 49,329 historical matches (1872-2024)
│   │   └── tactical_stats.csv     # 20 WC 2022 matches (49 columns)
│   └── temp_chunks/               # Temporary PDF chunks (~3 MB)
│
├── README.md                      # This file
├── ARCHITECTURE.md                # System architecture
├── LICENSE                        # MIT License
├── NOTICE                         # Third-party notices
└── requirements.txt               # Python dependencies
```

**Note:** All data files are included in the repository (58.5 MB total) for immediate testing and reproducibility. No API keys or data fetching required!

---

## 🔧 IBM Technologies Used

### ✅ IBM Granite 4.1 8B (Required)
- **Primary LLM** for both agents via Ollama
- Generates explanations and tactical insights
- Powers orchestrator's intent classification
- Temperature: 0.3 (VAR-Lens) / 0.7 (Tactical Pulse)

### ✅ Docling (Required)
- **Document Processing**: Converted 7 FIFA/IFAB PDFs to Markdown
- Processed 450 KB of official regulations
- Enabled efficient RAG pipeline with clean text extraction
- Preserved document structure and metadata

### ✅ LangFlow (Required)
- **Visual Orchestration**: 3 complete workflow templates
- No-code deployment option for demos
- Agent coordination and query routing
- Real-time testing and debugging

### ✅ IBM Bob (Required)
- **AI Coding Assistant** used throughout development
- Generated 13,000+ lines of Python code
- Created comprehensive documentation
- Assisted with architecture design and debugging

---

## 📈 System Validation

```bash
# Run complete system test
python scripts/test_complete_system.py
```

**Expected Output:**
```
✅ 1/8: Python imports
✅ 2/8: Data files exist
✅ 3/8: Ollama connection
✅ 4/8: Granite model available
✅ 5/8: VAR-Lens agent
✅ 6/8: Tactical Pulse agent
✅ 7/8: Orchestrator
✅ 8/8: Tactical Data Integration

All tests passed! ✅
```

---

## 🎬 Demo Scenarios

### Scenario 1: VAR Decision Explanation
```
Query: "Why was that goal disallowed for offside?"
Agent: VAR-Lens
Output: Detailed FIFA Law 11 explanation with source citations
```

### Scenario 2: Tactical Analysis
```
Query: "Analyze Qatar's tactical approach"
Agent: Tactical Pulse
Output: 
- Formation: 5-3-2
- Possession: 46%
- Shots: 7.5 per game
- AI insights on defensive strategy
```

### Scenario 3: Match Prediction
```
Query: "Predict Qatar vs Ecuador"
Agent: Tactical Pulse
Output:
- Score prediction with probabilities
- Tactical matchup analysis
- Formation battle breakdown
- Key player insights
```

---

## 🛠️ Advanced Features

### Fetch New Match Data
```bash
# Fetch World Cup 2022 matches
python scripts/fetch_match_data.py --world-cup-2022 --key-matches

# Fetch specific match
python scripts/fetch_match_data.py --fixture-id 855737

# Fetch national team matches
python scripts/fetch_match_data.py --team brazil --last 3
```

**Note:** Requires API-Football API key in `.env` file:
```bash
API_FOOTBALL_KEY=your_api_key_here
```

### Add New FIFA Documents
```python
from src.agents.var_lens import VARLensRAG

rag = VARLensRAG()
rag.add_documents(["path/to/new/document.pdf"])
rag.rebuild_index()
```

---

## 📚 Documentation

- **LangFlow Guide:** [`langflow_workflows/LANGFLOW_GUIDE.md`](langflow_workflows/LANGFLOW_GUIDE.md) - Complete workflow guide (545 lines)
- **Scripts Guide:** [`scripts/README.md`](scripts/README.md) - All utility scripts
- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md) - System design and data flow

---

## 🤝 Contributing

This project was built for the IBM Skills Build AI Builders Challenge (June 2026). Contributions welcome after challenge submission!

---

## 📄 License

MIT License - see [`LICENSE`](LICENSE) file for details.

---

## 🏆 IBM Challenge Submission

- **Challenge:** IBM Skills Build AI Builders Challenge (June 2026)
- **Theme:** FIFA World Cup 2026 - AI for Fan Understanding
- **Technologies:** IBM Granite, Docling, LangFlow, IBM Bob
- **Submission Deadline:** June 30, 2026, 11:59 PM ET
- **GitHub:** https://github.com/babaksh/FanPulse

---

**Made with ❤️ using IBM Bob** 🤖
