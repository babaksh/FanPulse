# FanPulse - System Architecture

## 🎯 Project Overview

**FanPulse** is an AI-powered platform that enhances the football viewing experience through two specialized agents:

1. **VAR-Lens Agent**: Explains VAR decisions using official FIFA documentation
2. **Tactical Pulse Agent**: Analyzes team performance and tactical changes with real match data

Built with IBM Granite, Docling, LangFlow, and IBM Bob for the IBM Skills Build AI Builders Challenge (June 2026).

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     FanPulse Platform                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           LangFlow Orchestration Layer               │  │
│  │ (Visual workflows & agent coordination)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                 │
│         ┌────────────────┴────────────────┐                │
│         │                                 │                │
│  ┌──────▼──────┐                  ┌───────▼──────┐         │
│  │  VAR-Lens   │                  │   Tactical   │         │
│  │   Agent     │                  │ Pulse Agent  │         │
│  └──────┬──────┘                  └───────┬──────┘         │
│         │                                 │                │
│  ┌──────▼─────────────────────────────────▼──────┐         │
│  │         Shared Services Layer                 │         │
│  │  • IBM Granite 4.1 8B (via Ollama)            │         │
│  │  • Query Router (Keyword + LLM)               │         │
│  │  • Response Handler (Unified formatting)      │         │
│  └───────────────────────────────────────────────┘         │
│                         │                                  │
│  ┌──────────────────────▼───────────────────────┐          │
│  │          Data Sources Layer                  │          │
│  │  • Docling (FIFA Rules Processing)           │          │
│  │  • FAISS Vector Store (658 vectors)          │          │
│  │  • Match Data (49,329 historical matches)    │          │
│  │  • Tactical Stats (20 WC 2022, 49 columns)   │          │
│  │  • API-Football (Live data ingestion)        │          │
│  └──────────────────────────────────────────────┘          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

**What's in GitHub:**

```
FanPulse/
│
├── src/                               # Source code
│   ├── agents/
│   │   ├── var_lens/                  # VAR-Lens Agent
│   │   │   ├── rag_engine.py          # RAG pipeline with FAISS
│   │   │   └── llm_providers.py       # LLM abstraction layer
│   │   └── tactical_pulse/            # Tactical Pulse Agent
│   │       ├── data_loader.py         # Match data loading
│   │       ├── match_analyzer.py      # Team analysis & predictions
│   │       └── metrics_calculator.py  # Statistical calculations
│   └── orchestrator/                  # Query Orchestration
│       ├── fanpulse_orchestrator.py   # Main orchestrator (436 lines)
│       ├── query_router.py            # Smart routing (224 lines)
│       └── response_handler.py        # Response formatting (341 lines)
│
├── langflow_workflows/                # LangFlow Workflows
│   ├── fanpulse_main_flow.json        # Main orchestrator workflow
│   ├── var_lens_flow.json             # VAR-Lens workflow
│   ├── tactical_pulse_flow.json       # Tactical Pulse workflow
│   ├── LANGFLOW_GUIDE.md              # Complete guide (545 lines)
│   └── README.md
│
├── scripts/                           # Utility Scripts
│   ├── build_var_lens_vectorstore.py  # Build FAISS vector store
│   ├── fetch_match_data.py            # Unified data fetching (569 lines)
│   ├── test_complete_system.py        # System validation (8 tests)
│   └── README.md
│
├── data/                              # Data Files
│   ├── raw_documents/                 # 7 FIFA/IFAB PDFs (original)
│   └── processed_documents/           # 7 FIFA/IFAB documents (Markdown)
│
├── README.md                          # Main documentation
├── ARCHITECTURE.md                    # This file
├── LICENSE                            # MIT License
├── NOTICE                             # Third-party notices
├── requirements.txt                   # Python dependencies
└── .gitignore                         # Git ignore rules
```

**What's NOT in GitHub (generated locally):**

```
data/
├── vector_stores/                     # FAISS index (built locally)
│   └── var_lens_faiss/
│       ├── index.faiss                # 658 vectors
│       └── index.pkl                  # Metadata
└── match_data/                        # CSV files (fetched locally)
    ├── results.csv                    # 49,329 historical matches
    └── tactical_stats.csv             # 20 WC 2022 matches (49 columns)
```

**Why not in GitHub?**
- **Vector stores**: Can be rebuilt using `scripts/build_var_lens_vectorstore.py`
- **Match data**: Can be fetched using `scripts/fetch_match_data.py` (requires API key)
- **Large files**: Keep repository size manageable

---

## 🔄 Data Flow

### VAR-Lens Agent Flow:
```
User Query (VAR Decision) 
    → Query Router (Keyword/LLM classification)
    → VAR-Lens Agent
    → Document Retrieval (FAISS similarity search)
    → Context Assembly (Top-k relevant chunks)
    → IBM Granite 4.1 8B (Generate explanation)
    → Response Handler (Format with sources)
    → User (Clear explanation with FIFA citations)
```

### Tactical Pulse Agent Flow:
```
User Query (Team/Match Analysis)
    → Query Router (Keyword/LLM classification)
    → Tactical Pulse Agent
    → Data Loader (Load match data + tactical stats)
    → Metrics Calculator (Compute statistics)
    → IBM Granite 4.1 8B (Generate AI insights)
    → Response Handler (Format with metrics)
    → User (Analysis with formations, possession, shots, AI insights)
```

### Orchestrator Flow:
```
User Query
    → Query Router
        ├─ Keyword Matching (Fast classification)
        └─ LLM Classification (Complex queries)
    → Agent Selection (VAR-Lens or Tactical Pulse)
    → Agent Execution
    → Response Handler (Unified formatting)
    → User (Consistent response structure)
```

---

## 🧩 Component Details

### 1. VAR-Lens Agent

**Purpose:** Explain VAR decisions using official FIFA rules

**Components:**
- **RAG Engine** (`rag_engine.py`):
  - Document loading from processed Markdown files
  - Text splitting with RecursiveCharacterTextSplitter
  - HuggingFace embeddings (all-MiniLM-L6-v2)
  - FAISS vector store for similarity search
  - RAG chain with IBM Granite

- **LLM Providers** (`llm_providers.py`):
  - Abstraction layer for multiple LLM providers
  - Supports: Ollama, IBM Granite, OpenAI, HuggingFace
  - Easy provider switching

**Data:**
- 7 FIFA/IFAB documents processed with Docling
- 658 vectors in FAISS index (built locally)
- Chunk size: 1000 characters, overlap: 200

**Key Features:**
- Source citation for transparency
- Multilingual support (via Granite)
- Dynamic document ingestion
- Efficient similarity search

---

### 2. Tactical Pulse Agent

**Purpose:** Analyze team performance and predict match outcomes

**Components:**
- **Data Loader** (`data_loader.py`):
  - Loads historical match data (49,329 matches)
  - Loads tactical statistics (20 WC 2022 matches, 49 columns)
  - Filters by team, date, tournament
  - Dynamic data ingestion from API-Football

- **Match Analyzer** (`match_analyzer.py`):
  - Team performance analysis
  - Match predictions
  - AI-powered insights generation
  - Formation and tactical analysis

- **Metrics Calculator** (`metrics_calculator.py`):
  - Win/loss/draw statistics
  - Goals scored/conceded
  - Form calculation
  - Head-to-head analysis

**Data (fetched locally):**
- **Historical Matches:** 49,329 matches (1872-2024)
- **Tactical Stats:** 20 World Cup 2022 matches with 49 columns:
  - Formations (home/away)
  - Possession percentages
  - Shots (total, on target, inside/outside box)
  - Passes (total, accuracy, key passes)
  - Expected Goals (xG)
  - Defensive metrics (tackles, interceptions, blocks)
  - Discipline (fouls, cards)
  - Set pieces (corners, offsides)

**Key Features:**
- Comprehensive tactical analysis
- AI-generated insights
- Match predictions with probabilities
- Real-time data integration

---

### 3. Orchestrator

**Purpose:** Route queries to appropriate agents and coordinate responses

**Components:**
- **FanPulse Orchestrator** (`fanpulse_orchestrator.py`):
  - Main coordination logic
  - Agent initialization (lazy loading)
  - Query processing pipeline
  - System status monitoring

- **Query Router** (`query_router.py`):
  - Keyword-based classification (fast)
  - LLM-based classification (accurate)
  - 60+ keywords for routing
  - Confidence scoring

- **Response Handler** (`response_handler.py`):
  - Unified response formatting
  - Error handling
  - Metadata enrichment
  - Display formatting

**Routing Logic:**
- **VAR-Lens Keywords:** var, referee, offside, penalty, handball, foul, rule, law, protocol
- **Tactical Pulse Keywords:** predict, statistics, performance, formation, possession, shots, tactical, analysis

**Fallback:** Defaults to Tactical Pulse if uncertain

---

## 🔧 IBM Technologies Integration

### IBM Granite 4.1 8B
- **Deployment:** Via Ollama (local inference)
- **Model Size:** 5.3 GB
- **Usage:**
  - VAR-Lens: Generate rule explanations (temperature: 0.3)
  - Tactical Pulse: Generate tactical insights (temperature: 0.7)
  - Orchestrator: Intent classification (temperature: 0.3)

### Docling
- **Purpose:** Convert FIFA PDFs to clean Markdown
- **Process:**
  1. PDF ingestion (7 FIFA/IFAB documents)
  2. Layout analysis
  3. Text extraction
  4. Markdown conversion
  5. Metadata preservation
- **Output:** 7 Markdown files in `data/processed_documents/`

### LangFlow
- **Purpose:** Visual workflow orchestration
- **Workflows:**
  1. `fanpulse_main_flow.json` - Complete orchestration
  2. `var_lens_flow.json` - Rule explanations
  3. `tactical_pulse_flow.json` - Match analysis
- **Benefits:**
  - No-code deployment
  - Visual debugging
  - Easy testing

### IBM Bob
- **Purpose:** AI coding assistant
- **Contributions:**
  - 13,000+ lines of Python code
  - Complete documentation
  - Architecture design
  - Debugging assistance

---

## 📊 Data Pipeline

### Document Processing (VAR-Lens)
```
FIFA PDFs (in repo: data/raw_documents/)
    → Docling (PDF to Markdown)
    → Processed Markdown (in repo: data/processed_documents/)
    → Text Splitting (1000 chars, 200 overlap)
    → HuggingFace Embeddings (all-MiniLM-L6-v2)
    → FAISS Vector Store (built locally: data/vector_stores/)
    → Ready for RAG queries
```

### Match Data Pipeline (Tactical Pulse)
```
API-Football (requires API key)
    → fetch_match_data.py (Rate-limited fetching)
    → Data Validation & Cleaning
    → CSV Storage (local: data/match_data/)
    → Data Loader (Pandas DataFrame)
    → Metrics Calculator
    → Ready for analysis
```

---

## 🧪 Testing Strategy

### System Validation (8 Tests)
1. **Module Imports:** Verify all Python modules load correctly
2. **Data Files:** Check existence of required data files
3. **Ollama Connection:** Test Ollama API connectivity
4. **Granite Model:** Verify Granite 4.1 8B availability
5. **VAR-Lens Agent:** Test RAG pipeline and query processing
6. **Tactical Pulse Agent:** Test team analysis functionality
7. **Orchestrator:** Test query routing and coordination
8. **Tactical Data Integration:** Test 49-column tactical data

**Run Tests:**
```bash
python scripts/test_complete_system.py
```

---

## 🚀 Deployment Options

### Option 1: LangFlow (Recommended for Demo)
- Visual interface at `http://localhost:7860`
- Import workflows from `langflow_workflows/`
- No-code deployment
- Real-time testing
- Easy debugging

### Option 2: Python API
- Direct Python integration
- Programmatic access
- Custom workflows
- Production deployment

### Option 3: Command Line
- Quick testing
- Batch processing
- Automation scripts

---

## 🔐 Security & Privacy

- **API Keys:** Stored in `.env` file (not in repository)
- **Local Inference:** Granite runs locally via Ollama (no data sent to cloud)
- **Data Privacy:** All match data and documents stored locally
- **Open Source:** MIT License, transparent codebase

---

## 📈 Performance Metrics

- **VAR-Lens Query Time:** ~2-5 seconds (including LLM generation)
- **Tactical Pulse Query Time:** ~1-3 seconds (without AI insights)
- **Vector Store Size:** 658 vectors, ~5 MB (built locally)
- **Match Data Size:** 49,329 matches, ~15 MB (fetched locally)
- **Tactical Data Size:** 20 matches, 49 columns, ~50 KB (fetched locally)

---

## 🔮 Future Enhancements

1. **Real-time Data Streaming:** Live match data integration
2. **Multi-language Support:** Expand beyond English
3. **Player-level Analysis:** Individual player statistics
4. **Video Integration:** Link to match highlights
5. **Mobile App:** iOS/Android deployment
6. **Advanced Predictions:** ML models for match outcomes

---

## 🤝 Contributing

This project was built for the IBM Skills Build AI Builders Challenge (June 2026). Contributions welcome after challenge submission!

---

**Made with ❤️ using IBM Bob** 🤖