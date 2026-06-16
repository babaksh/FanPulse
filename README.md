# FanPulse ⚽🤖

**AI-Powered Football Analysis for FIFA World Cup 2026**

FanPulse is a multi-agent AI system that helps football fans understand VAR decisions and analyze team performance using explainable AI. Built with IBM Granite, Docling, and LangFlow for the IBM Skills Build AI Builders Challenge (June 2026).

[![IBM Granite](https://img.shields.io/badge/IBM-Granite_3.1_8B-blue)](https://www.ibm.com/granite)
[![Docling](https://img.shields.io/badge/IBM-Docling-green)](https://github.com/DS4SD/docling)
[![Langflow](https://img.shields.io/badge/Langflow-Multi--Agent-purple)](https://www.langflow.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What is FanPulse?

A **multi-agent AI system** with three specialized components working together:

### 🎭 FanPulse Orchestrator
Intelligent coordinator that routes questions to the right agent automatically.
- 🧠 Analyzes user intent (VAR rules vs tactical analysis)
- 🔀 Routes to appropriate specialized agent
- ⚡ Executes agents in parallel when needed
- 🎨 Synthesizes results into unified responses

### 🔍 VAR-Lens Agent
Explains Video Assistant Referee (VAR) decisions using official FIFA rules.
- 📚 **658-vector knowledge base** from 7 FIFA/IFAB documents
- 🤖 Powered by **IBM Granite** (local or cloud)
- 📖 Clear explanations with **source citations**
- 🔄 **RAG pipeline** with FAISS vector store
- 🎯 **Match-specific decisions** database for real incidents

### ⚽ Tactical Pulse Agent  
Analyzes team performance and provides tactical insights with real match data.
- 📊 **49,000+ historical matches** (1872-2026)
- 🏆 **65 World Cup 2022 matches** with detailed tactical data
- 🎯 Advanced metrics: possession, xG, shots, passes, formations
- 🤖 **AI-powered insights** using **IBM Granite**

---

## 🏗️ System Architecture

FanPulse follows the **Tool-Agent separation pattern** - an industry-standard architecture:

```
User Question
    ↓
┌─────────────────────────────────────────┐
│  Orchestrator (LLM + Routing Logic)     │
│  - Analyzes intent                      │
│  - Selects appropriate agent(s)         │
│  - Coordinates execution                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Agents (LLM + System Prompts)          │
│  ├─ VAR-Lens: Rules interpretation     │
│  └─ Tactical Pulse: Performance analysis│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Tools (Pure Functions → JSON)          │
│  - query_fifa_documents                 │
│  - query_referee_decisions              │
│  - analyze_team                         │
│  - compare_teams                        │
│  - get_tactical_data                    │
│  - get_team_stats                       │
│  - query_csv                            │
└─────────────────────────────────────────┘
    ↓
Formatted Response → User
```

### Key Architecture Principles

1. **Separation of Concerns**: Tools return raw JSON data, agents interpret and format
2. **Reusability**: Same tools can be used by multiple agents
3. **Testability**: Tools are pure functions with predictable outputs
4. **Flexibility**: Same data, different formatting per agent
5. **Maintainability**: Clear separation between data retrieval and presentation

This architecture follows **LangChain best practices** and is similar to **OpenAI Function Calling** and **Anthropic Tool Use** patterns.

---

## 🚀 Quick Start

### 1. Install Prerequisites

**Python 3.11+**
```bash
python --version
```

**Ollama (for local IBM Granite)**
```bash
# Windows: Download from https://ollama.com
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Pull IBM Granite model (5.3 GB)
ollama pull granite4.1:8b
```

**IBM Tools**
```bash
# Clone repository
git clone https://github.com/babaksh/FanPulse.git
cd FanPulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install IBM Docling and other dependencies
pip install -r requirements.txt
```

### 2. Install LangFlow Desktop

Download and install LangFlow Desktop from [langflow.org](https://www.langflow.org/)

### 3. Setup in LangFlow

1. **Open LangFlow Desktop**

2. **Import Workflow**
   - Click "Import" or "New Flow"
   - Select: `langflow_workflows/FanPulse Multi-Agent.json`

3. **Configure IBM Granite Model**
   - Open each agent component (Orchestrator, VAR-Lens, Tactical Pulse)
   - In "Language Model" field, select your IBM Granite deployment:
     - **Local**: Select "Ollama" → "granite4.1:8b"
     - **Cloud**: Configure IBM Granite Cloud API credentials

4. **Data Setup** (Choose one option)

   **Option A: Use Pre-built Data** (Recommended - Ready to use!)
   
   All data is included in the repository:
   - ✅ `data/vector_stores/` - VAR-Lens FAISS index (658 vectors)
   - ✅ `data/match_data/` - Historical matches & tactical stats
   - ✅ `data/referee_decisions/` - Match-specific incidents
   
   No additional setup needed - just import and run!

   **Option B: Rebuild from Source** (Optional)
   ```bash
   # Rebuild VAR-Lens vector store from FIFA documents
   python scripts/var_lens_setup/build_var_lens_vectorstore.py
   ```

5. **Run the Workflow**
   - Click "Run" or "Play" button in LangFlow
   - Start asking questions!

**Note**: All model configuration, agent setup, and orchestration is done within LangFlow Desktop. No manual CLI setup required.

---

## 💻 Usage Examples

### VAR Decision Explanation
```
Query: "What is the offside rule?"
Agent: VAR-Lens
Output: Detailed FIFA Law 11 explanation with source citations
```

### Tactical Analysis
```
Query: "Analyze Brazil's performance"
Agent: Tactical Pulse
Output: 
- Win rate, goals, form analysis
- AI insights on playing style
- Strengths and weaknesses
```

### Match-Specific Incident
```
Query: "What happened at minute 67 in Brazil vs Argentina?"
Agent: VAR-Lens (uses both tools)
Output:
- Specific referee decision details
- Official FIFA rule explanation
- Combined analysis
```

### Match Prediction
```
Query: "Predict Argentina vs France"
Agent: Tactical Pulse
Output:
- Head-to-head comparison
- Tactical matchup analysis
- Performance-based prediction
```

---

## 📁 Project Structure

```
FanPulse/
├── langflow_components/              # LangFlow custom components
│   ├── fanpulse_orchestrator.py      # Main orchestrator agent
│   ├── var_lens_agent.py             # VAR rules expert agent
│   ├── tactical_pulse_agent.py       # Tactical analysis agent
│   ├── query_fifa_docs_tool.py       # FIFA documents RAG tool
│   ├── query_referee_decisions_tool.py  # Match incidents tool
│   ├── analyze_team_tool.py          # Team analysis tool
│   ├── compare_teams_tool.py         # Head-to-head comparison tool
│   ├── get_tactical_data_tool.py     # Tournament tactical data tool
│   ├── get_team_stats_tool.py        # Quick stats tool
│   └── query_csv_tool.py             # Custom CSV queries tool
│
├── langflow_workflows/               # Workflow definitions & prompts
│   ├── FanPulse Multi-Agent.json     # Complete multi-agent workflow
│   ├── ORCHESTRATOR_SYSTEM_PROMPT.md # Orchestrator instructions
│   ├── VAR_LENS_SYSTEM_PROMPT.md     # VAR-Lens agent instructions
│   ├── TACTICAL_PULSE_SYSTEM_PROMPT.md  # Tactical Pulse instructions
│   ├── COMPLETE_WORKFLOW_SETUP.md    # Setup guide
│   ├── DATA_SCHEMA_GUIDE_V3.md       # Data structure reference
│   └── DATA_SCHEMA_GUIDE_V2.md       # Legacy data guide
│
├── scripts/                          # Utility scripts
│   ├── var_lens_setup/               # VAR-Lens setup scripts
│   │   ├── build_var_lens_vectorstore.py  # Build FAISS vector store
│   │   ├── process_documents.py      # Process PDFs with Docling
│   │   ├── add_referee_decision.py   # Add match incidents
│   │   └── README.md                 # Setup documentation
│   └── update_live_matches_v2.py     # Live match data updater
│
├── data/                             # Data files
│   ├── raw_documents/                # 7 FIFA/IFAB PDFs
│   ├── processed_documents/          # 7 Markdown files (Docling output)
│   ├── vector_stores/                # FAISS index
│   │   └── var_lens/                 # 658 vectors, 1.01 MB
│   ├── match_data/                   # Match datasets
│   │   ├── results.csv               # 49,000+ historical matches
│   │   └── tactical_stats.csv        # 65 WC 2022 matches with tactics
│   ├── referee_decisions/            # Match-specific referee decisions
│   │   ├── WC2026_2026_06_15_Brazil_Argentina.json
│   │   └── README.md
│   ├── data_schema.json              # Complete data structure
│   └── cache/                        # Cached data (soccerdata)
│
├── README.md                         # This file
├── LICENSE                           # MIT License
└── requirements.txt                  # Python dependencies
```

---

## 🔧 IBM Technologies Used

### ✅ IBM Granite (Required)
- **Primary LLM** for all agents
- Generates explanations and tactical insights
- Powers orchestrator's intent classification
- Temperature: 0.2 (precise tool calling)

**Deployment Options:**
- **Local**: IBM Granite 4.1 8B via Ollama (tested ✅)
- **Cloud**: IBM Granite Cloud API (tested ✅)

**Usage in Components:**
```python
# All agents use Granite via LangFlow's model configuration
# Supports both local (Ollama) and cloud (IBM API) deployment
# Temperature: 0.2 for precise tool calling
# Max tokens: 1500 (VAR-Lens), 2000 (Tactical Pulse), 2500 (Orchestrator)
```

### ✅ IBM Docling (Required)
- **Document Processing**: Converted 7 FIFA/IFAB PDFs to Markdown
- Processed official regulations and protocols
- Enabled efficient RAG pipeline with clean text extraction
- Preserved document structure and metadata

**Processed Documents:**
1. Laws of the Game 2026/27
2. Video Assistant Referee (VAR) Protocol
3. Changes to the Laws of the Game 2026/27
4. FIFA World Cup 2026 Regulations
5. Off-field Treatment and Assessment Protocol
6. Throw-in and Goal-kick Countdown Protocol
7. Time-limited Substitution Protocol

**Processing Script:**
```bash
python scripts/var_lens_setup/process_documents.py
```

### ✅ LangFlow (Required)
- **Visual Orchestration**: Complete multi-agent workflow
- No-code deployment option for demos
- Agent coordination and query routing
- Real-time testing and debugging

**Workflow:**
- Import: `langflow_workflows/FanPulse Multi-Agent.json`
- 3 agents + 7 tools + system prompts
- Automatic parallel execution when needed

---

## 🎯 Key Features

### 1. Multi-Agent Architecture
- **Orchestrator**: Routes queries intelligently
- **VAR-Lens**: Explains rules with official sources
- **Tactical Pulse**: Analyzes performance with data

### 2. Dual Data Sources (VAR-Lens)
- **General Rules**: 658 vectors from FIFA/IFAB documents
- **Match Incidents**: Referee decisions database for specific matches

### 3. Comprehensive Tactical Data
- **Historical**: 49,000+ matches (1872-2026)
- **Tournament**: 65 WC 2022 matches with detailed tactics
- **Metrics**: Possession, xG, shots, passes, formations

### 4. Explainable AI
- **Source Citations**: Every answer references official documents
- **Transparent Reasoning**: Clear explanation of analysis
- **Human-Centered**: Accessible language for all fans

### 5. Tool-Agent Separation
- **Tools**: Pure functions returning JSON data
- **Agents**: Interpret data and format responses
- **Benefits**: Reusable, testable, maintainable

---

## 📊 Data Sources

### VAR-Lens Data
1. **FIFA/IFAB Documents** (658 vectors)
   - Laws of the Game 2026/27
   - VAR Protocol (IFAB)
   - FIFA World Cup 2026 Regulations
   - Changes to Laws 2026/27
   - Treatment protocols (3 documents)

2. **Referee Decisions Database**
   - Match-specific incidents
   - VAR review details
   - Decision reasoning
   - Example: `data/referee_decisions/WC2026_2026_06_15_Brazil_Argentina.json`

### Tactical Pulse Data
1. **results.csv** (~49,000 matches)
   - Date, teams, scores
   - Tournament, venue
   - Historical trends (1872-2026)

2. **tactical_stats.csv** (65 WC 2022 matches)
   - Possession, shots, passes
   - Expected Goals (xG)
   - Formations, defensive metrics
   - Prefix system: WC2022_*, WC2026_*

3. **data_schema.json**
   - Complete data structure
   - Column descriptions
   - Data types and formats

---

## 🧪 Testing

### Build Vector Store
```bash
python scripts/var_lens_setup/build_var_lens_vectorstore.py
```

### Process Documents
```bash
python scripts/var_lens_setup/process_documents.py
```

### Add Referee Decision
```bash
python scripts/var_lens_setup/add_referee_decision.py
```

---

## 📚 Documentation

### Setup Guides
- [`scripts/var_lens_setup/README.md`](scripts/var_lens_setup/README.md) - VAR-Lens setup
- [`langflow_workflows/COMPLETE_WORKFLOW_SETUP.md`](langflow_workflows/COMPLETE_WORKFLOW_SETUP.md) - Workflow setup

### System Prompts
- [`langflow_workflows/ORCHESTRATOR_SYSTEM_PROMPT.md`](langflow_workflows/ORCHESTRATOR_SYSTEM_PROMPT.md) - Orchestrator instructions
- [`langflow_workflows/VAR_LENS_SYSTEM_PROMPT.md`](langflow_workflows/VAR_LENS_SYSTEM_PROMPT.md) - VAR-Lens instructions
- [`langflow_workflows/TACTICAL_PULSE_SYSTEM_PROMPT.md`](langflow_workflows/TACTICAL_PULSE_SYSTEM_PROMPT.md) - Tactical Pulse instructions

### Data References
- [`data/data_schema.json`](data/data_schema.json) - Complete data structure
- [`langflow_workflows/DATA_SCHEMA_GUIDE_V3.md`](langflow_workflows/DATA_SCHEMA_GUIDE_V3.md) - Data guide
- [`data/referee_decisions/README.md`](data/referee_decisions/README.md) - Referee decisions format

---

## 🎯 Challenge Alignment

### Technical Execution ✅
- Effective use of **IBM Granite** for all agents (local & cloud)
- **Docling** for document processing (7 PDFs → Markdown)
- **LangFlow** for visual multi-agent orchestration
- Functional and well-structured solution
- Complete testing and validation

### Innovation ✅
- **Multi-agent architecture** with intelligent routing
- **Tool-Agent separation** following industry best practices
- **Dual data sources** for VAR-Lens (general + specific)
- **RAG pipeline** with 658-vector knowledge base
- **Real tactical data** integration (65 WC 2022 matches)
- **Explainable AI** with source citations

### Challenge Fit ✅
- **VAR transparency**: Explains referee decisions with FIFA rules
- **Tactical understanding**: Analyzes team performance and strategies
- **Fan engagement**: Makes complex football concepts accessible
- **Real-world application**: Ready for World Cup 2026

### Implementation & Feasibility ✅
- **Flexible Deployment**: Works with local Ollama or IBM Granite Cloud
- **Scalable**: Modular architecture for easy expansion
- **Reproducible**: All data and code included
- **Production-ready**: Comprehensive documentation

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
- **Technologies:** IBM Granite, Docling, LangFlow
- **Submission Deadline:** June 30, 2026, 11:59 PM ET
- **GitHub:** https://github.com/babaksh/FanPulse

### Judging Criteria Alignment

| Criterion | Implementation | Evidence |
|-----------|----------------|----------|
| **Technical Execution** | IBM Granite + Docling + LangFlow | Multi-agent system, local & cloud ready |
| **Innovation** | Tool-Agent separation + Dual data sources | 658 vectors + match incidents database |
| **Challenge Fit** | VAR transparency + Tactical insights | Real FIFA rules + WC 2022 data |
| **Feasibility** | Local deployment, modular design | Complete documentation, reproducible |

---

**Made with ❤️ for FIFA World Cup 2026** ⚽🤖
