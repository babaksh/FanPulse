# FanPulse ⚽🤖

**AI-Powered Football Analysis for FIFA World Cup 2026**

An intelligent multi-agent system that demystifies VAR decisions and provides tactical insights using explainable AI. Built with IBM Granite, Docling, and LangFlow for the IBM Skills Build AI Builders Challenge.

[![IBM Bob](https://img.shields.io/badge/Built_with-IBM_Bob-052FAD)](https://www.ibm.com/products/watsonx-code-assistant)
[![IBM Granite](https://img.shields.io/badge/IBM-Granite-blue)](https://www.ibm.com/granite)
[![Docling](https://img.shields.io/badge/IBM-Docling-green)](https://github.com/DS4SD/docling)
[![Langflow](https://img.shields.io/badge/Langflow-Multi--Agent-purple)](https://www.langflow.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 The Problem I'm Solving

### VAR Confusion & Tactical Complexity

Football fans worldwide face two major challenges during FIFA World Cup 2026:

1. **VAR Decision Confusion** 😕
   - "Why was that goal disallowed?"
   - "Was that really a penalty?"
   - "What's the actual offside rule?"
   - Complex referee decisions lack clear explanations for fans

2. **Tactical Understanding Gap** 📊
   - "How does Brazil actually play?"
   - "Who would win: Argentina vs France?"
   - "What are Germany's weaknesses?"
   - Fans want deeper insights beyond just scores and standings

**The Impact:**
- Frustrated fans questioning referee decisions
- Missed opportunities to appreciate tactical brilliance
- Reduced engagement with the beautiful game
- Barriers to understanding modern football

---

## 💡 My AI Solution

### FanPulse: Three Specialized AI Agents Working Together

```
User Question → Orchestrator → Right Agent → Expert Answer
```

#### 🎭 **FanPulse Orchestrator**
Smart coordinator that understands your question and routes it automatically:
- 🧠 Analyzes intent (VAR rules vs tactical analysis)
- 🔀 Routes to the right specialist
- ⚡ Calls multiple agents in parallel when needed
- 🎨 Combines results into unified answers

#### 🔍 **VAR-Lens Agent** 
Your personal VAR expert explaining referee decisions:
- 📚 **658-vector knowledge base** from 7 official FIFA/IFAB documents
- 🎯 Real match incidents database (World Cup 2026)
- 📖 Clear explanations with source citations
- 🤖 Powered by IBM Granite for natural language understanding

#### ⚽ **Tactical Pulse Agent**
Your tactical analyst providing performance insights:
- 📊 **49,000+ historical matches** (1872-2026)
- 🏆 **65 World Cup 2022 matches** with detailed tactical data
- ⚽ **FIFA World Cup 2026** live tournament data
- 🎯 Advanced metrics: possession, xG, shots, passes, formations
- 🤖 AI-powered insights using IBM Granite

---

## 🚀 My Technical Approach

### Multi-Agent Architecture with Tool-Agent Separation

```
┌─────────────────────────────────────────┐
│  User: "What are handball rules and    │
│         how does Brazil play?"          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Orchestrator (IBM Granite)             │
│  - Detects 2 intents: VAR + Tactical   │
│  - Routes to both agents in parallel    │
└─────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌──────────────────┐   ┌──────────────────┐
│  VAR-Lens Agent  │   │ Tactical Pulse   │
│  (IBM Granite)   │   │ Agent (Granite)  │
└──────────────────┘   └──────────────────┘
        ↓                       ↓
┌──────────────────┐   ┌──────────────────┐
│  Tools (JSON)    │   │  Tools (JSON)    │
│  - query_fifa_   │   │  - analyze_team  │
│    documents     │   │  - compare_teams │
│  - query_referee_│   │  - get_tactical_ │
│    decisions     │   │    data          │
└──────────────────┘   └──────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Combined Response:                     │
│  1. Handball rules explained            │
│  2. Brazil's tactical analysis          │
└─────────────────────────────────────────┘
```

### Key Technical Components

#### 1. **IBM watsonx Code Assistant (Bob)** (Development Tool)
- AI-powered coding assistant used throughout development
- Accelerated component creation and debugging
- Generated boilerplate code for tools and agents
- Provided code suggestions and best practices
- Enhanced productivity and code quality

#### 2. **IBM Granite LLM** (Core AI Engine)
- Powers all 3 agents with natural language understanding
- Temperature: 0.2 for precise tool calling
- Supports both local (Ollama) and cloud deployment
- Generates human-friendly explanations from structured data

#### 3. **IBM Docling** (Document Processing)
- Converted 7 FIFA/IFAB PDFs to clean Markdown
- Preserved structure and metadata
- Enabled efficient RAG pipeline
- High-quality text extraction for vector embeddings

#### 4. **RAG Pipeline** (Knowledge Retrieval)
- FAISS vector store with 658 embeddings
- Semantic search for relevant FIFA rules
- Source citation for transparency
- Real-time document retrieval

#### 5. **LangFlow** (Visual Orchestration)
- No-code multi-agent workflow
- Real-time testing and debugging
- Agent coordination and parallel execution
- Production-ready deployment

#### 6. **Tool-Agent Separation Pattern**
```python
# Tools: Pure functions returning JSON
def analyze_team(team_name: str) -> dict:
    """Returns raw JSON data"""
    return {
        "team": "Brazil",
        "matches": 1031,
        "win_rate": 67.2,
        "goals_scored": 2323
    }

# Agents: Interpret and format for humans
"""
## 🎯 Brazil - Tactical Profile

Brazil's impressive 67.2% win rate across 1,031 
international matches reveals a team built on 
attacking excellence, with 2,323 goals scored...
"""
```

**Benefits:**
- ✅ Reusable tools across agents
- ✅ Testable pure functions
- ✅ Flexible formatting per agent
- ✅ Maintainable codebase

---

## 🌟 Why This Matters for Football & World Cup

### 1. **Democratizing VAR Understanding** 🎥
- **Before**: Fans confused by referee decisions, relying on biased commentary
- **After**: Instant access to official FIFA rules with clear explanations
- **Impact**: Reduced controversy, increased trust in officiating

### 2. **Elevating Tactical Appreciation** 📊
- **Before**: Casual fans only see scores, miss tactical brilliance
- **After**: AI-powered insights reveal playing styles, strengths, weaknesses
- **Impact**: Deeper engagement, appreciation for the beautiful game

### 3. **Bridging the Knowledge Gap** 🌉
- **Before**: Complex football concepts accessible only to experts
- **After**: Natural language AI makes analysis accessible to everyone
- **Impact**: More informed fans, richer discussions

### 4. **Real-Time World Cup Companion** ⚡
- **Before**: Wait for post-match analysis from pundits
- **After**: Instant answers during live matches
- **Impact**: Enhanced viewing experience, immediate understanding

### 5. **Explainable AI for Sports** 🔍
- **Before**: Black-box AI predictions without reasoning
- **After**: Every answer cites official sources and data
- **Impact**: Trust, transparency, educational value

### Real-World Use Cases

**During a Match:**
```
Fan: "Why was that goal disallowed?"
FanPulse: [Explains offside rule + shows exact incident from database]
Result: Fan understands decision, continues enjoying match
```

**Pre-Match Analysis:**
```
Fan: "Who will win: Argentina vs France?"
FanPulse: [Head-to-head stats + tactical matchup analysis]
Result: Fan has informed prediction, deeper match appreciation
```

**Learning the Game:**
```
Fan: "What is VAR and how does it work?"
FanPulse: [Official FIFA protocol + real examples]
Result: Fan becomes more knowledgeable about modern football
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Ollama (for local IBM Granite)
- LangFlow Desktop

### Installation

```bash
# 1. Clone repository
git clone https://github.com/babaksh/FanPulse.git
cd FanPulse

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama and pull IBM Granite
# Download from: https://ollama.com
ollama pull granite4.1:8b

# 5. Install LangFlow Desktop
# Download from: https://www.langflow.org/
```

### Setup in LangFlow

1. **Import Workflow**
   - Open LangFlow Desktop
   - Import: `langflow_workflows/FanPulse Multi-Agent.json`

2. **Update File Paths** ⚠️
   - Open each custom component
   - Replace `d:/MyPythonProjects/FanPulse/` with your actual path
   - Components to update:
     - `query_fifa_docs_tool.py`
     - `query_referee_decisions_tool.py`
     - `analyze_team_tool.py`
     - `compare_teams_tool.py`
     - `get_tactical_data_tool.py`
     - `get_team_stats_tool.py`
     - `query_csv_tool.py`
     - `read_schema_tool.py`

3. **Configure IBM Granite**
   - Select "Ollama" → "granite4.1:8b" in each agent
   - Or configure IBM Granite Cloud API

4. **Run!**
   - Click "Run" button
   - Start asking questions

---

## 💻 Usage Examples

### Simple Questions

#### VAR Rule Explanation
```
Q: "What is the offside rule?"

Agent: VAR-Lens
Tools: query_fifa_documents("offside rule")

Response:
## 📋 Offside Rule (Law 11)

### Overview
A player is in an offside position if they are nearer to 
the opponent's goal line than both the ball and the 
second-last opponent when the ball is played to them...

### 📚 Source
Official FIFA/IFAB Documents (Laws of the Game 2026/27)
```

#### Team Analysis
```
Q: "Analyze Brazil's performance"

Agent: Tactical Pulse
Tools: analyze_team("Brazil")

Response:
## 🎯 Brazil - Tactical Profile

Brazil's impressive 67.2% win rate across 1,031 matches 
reveals a team built on attacking excellence...

### 📊 Performance Analysis
- **Matches**: 1,031
- **Win Rate**: 67.2%
- **Goals Scored**: 2,323
- **Goal Difference**: +1,124

### ⚽ Tactical Identity
Brazil's 4-2-3-1 formation emphasizes possession-based 
build-up with creative attacking midfielders...
```

### Real Match Incident

```
Q: "What happened at minute 67 in Belgium vs Iran?"

Agent: VAR-Lens
Tools: 
  1. query_referee_decisions(home_team="Belgium", away_team="Iran")
  2. query_fifa_documents("handball rules")

Response:
## 🎥 Referee Decision: Belgium vs Iran - Minute 67

### 📋 What Happened
**Incident Details:**
- **Player**: Mehdi Taremi
- **Team**: Iran (Away)
- **Decision Type**: Penalty
- **Reason**: Handball in penalty area

### 🎥 VAR Review Process
**Initial On-Field Decision**: Play on
**VAR Check**: Possible handball
**Final Decision**: Penalty awarded to Belgium
**Outcome**: Overturned ✗

### 📖 The Official Rule Applied
According to FIFA Law 12, it is an offence if a player 
"touches the ball with their hand/arm when it has made 
their body unnaturally bigger"...

### 📚 Sources
Referee Decisions Database + Official FIFA/IFAB Documents
```

### Combined Questions (Multi-Agent)

```
Q: "What are handball rules and compare Germany vs France?"

Orchestrator: Detects 2 intents → Calls both agents in parallel

Agent 1: VAR-Lens
Tools: query_fifa_documents("handball rules")

Agent 2: Tactical Pulse  
Tools: compare_teams("Germany", "France")

Response:
## 📋 Handball Rules According to FIFA (Law 12)
[Full handball rule explanation...]

---

## ⚖️ Germany vs France - Tactical Head-to-Head

### 📊 Historical Record
**Total meetings:** 35
- **Germany wins:** 11
- **France wins:** 16
- **Draws:** 8

### 🎯 Tactical Matchup
Germany's possession-based approach (58% avg) clashes 
with France's counter-attacking style...

### 💡 Prediction
France holds a slight edge due to recent form and 
psychological advantage from 16 wins vs 11...
```

### Complex Tactical Question

```
Q: "Show me all World Cup 2026 matches where teams had 
    over 65% possession but lost"

Agent: Tactical Pulse
Tools: 
  1. read_schema() → Get column names
  2. query_csv(
       query_mode="custom",
       table="tactical_data",
       custom_filter="(home_possession > 65) & (home_score < away_score) | 
                      (away_possession > 65) & (away_score < home_score)"
     )

Response:
## 📊 High Possession Defeats - WC 2026

### 📈 What This Reveals
3 matches where dominant possession didn't translate to victory:

1. **Spain 1-2 Morocco** (June 15, 2026)
   - Spain: 68% possession, 18 shots
   - Morocco: 2 goals from 6 shots (33% conversion)
   - **Insight**: Clinical finishing beats possession

2. **Germany 0-1 Japan** (June 18, 2026)
   - Germany: 71% possession, 22 shots
   - Japan: 1 goal from 4 shots (25% conversion)
   - **Insight**: Counter-attacking masterclass

3. **Netherlands 2-3 Argentina** (June 21, 2026)
   - Netherlands: 66% possession, 20 shots
   - Argentina: 3 goals from 9 shots (33% conversion)
   - **Insight**: Efficiency over dominance

### 💡 Key Tactical Insights
- Possession ≠ Goals
- Shot conversion matters more than shot volume
- Counter-attacking remains effective against possession teams

### 📚 Source
Tournament Tactical Database (WC 2026)
```

---

## 📁 Project Structure

```
FanPulse/
├── langflow_components/                   # LangFlow custom components
│   ├── fanpulse_orchestrator.py           # Main orchestrator agent
│   ├── var_lens_agent.py                  # VAR rules expert agent
│   ├── tactical_pulse_agent.py            # Tactical analysis agent
│   ├── query_fifa_docs_tool.py            # FIFA documents RAG tool
│   ├── query_referee_decisions_tool.py    # Match incidents tool
│   ├── analyze_team_tool.py               # Team analysis tool
│   ├── compare_teams_tool.py              # Head-to-head comparison tool
│   ├── get_tactical_data_tool.py          # Tournament tactical data tool
│   ├── get_team_stats_tool.py             # Quick stats tool
│   ├── query_csv_tool.py                  # Custom CSV queries tool
│   └── read_schema_tool.py                # Data schema reader tool
│
├── langflow_workflows/                    # Workflow definitions & prompts
│   ├── ORCHESTRATOR_SYSTEM_PROMPT.md      # Orchestrator instructions
│   ├── VAR_LENS_SYSTEM_PROMPT.md          # VAR-Lens agent instructions
│   └── TACTICAL_PULSE_SYSTEM_PROMPT.md    # Tactical Pulse instructions
│
├── scripts/                               # Utility scripts
│   ├── var_lens_setup/                    # VAR-Lens setup scripts
│       ├── build_var_lens_vectorstore.py  # Build FAISS vector store
│       ├── process_documents.py           # Process PDFs with Docling
│       └── README.md                      # Setup documentation
│   
│
├── data/                                  # Data files
│   ├── raw_documents/                     # 7 FIFA/IFAB PDFs
│   ├── processed_documents/               # 7 Markdown files (Docling output)
│   ├── vector_stores/                     # FAISS index
│   │   └── var_lens/                      # 658 vectors, 1.01 MB
│   ├── match_data/                        # Match datasets
│   │   ├── results.csv                    # 49,000+ historical matches
│   │   ├── tactical_data.csv              # WC 2022 + WC 2026 tactical stats
│   │   ├── data_schema.json               # Complete data structure
│   │   └── README.md                      # Data documentation
│   └── referee_decisions/                 # Match-specific referee decisions
│       └── WC_2026-06-*.json              # World Cup 2026 matches
│
├── README.md                              # This file
├── LICENSE                                # MIT License
└── requirements.txt                       # Python dependencies
```

---

## 🔧 Available Tools

### VAR-Lens Tools

#### 1. query_fifa_documents
Search official FIFA/IFAB documents for rules and protocols.
```python
query_fifa_documents(question="handball rules")
# Returns: Relevant rule excerpts with source citations
```

#### 2. query_referee_decisions
Get VAR-reviewable decisions from World Cup 2026 matches.
```python
query_referee_decisions(
    home_team="Belgium",
    away_team="Iran",
    var_only=True  # Optional: filter only VAR-reviewed
)
# Returns: Match incidents with decision details
```

### Tactical Pulse Tools

#### 3. analyze_team
Comprehensive team profile (historical + tactical).
```python
analyze_team(team_name="Brazil")
# Returns: Complete team analysis with stats and insights
```

#### 4. compare_teams
Head-to-head comparison of exactly two teams.
```python
compare_teams(team1="Germany", team2="France")
# Returns: H2H record, tactical matchup, prediction
```

#### 5. get_tactical_data
Detailed tactical stats for one team.
```python
get_tactical_data(
    team_name="Spain",
    tournament_prefix="WC_2026"  # Optional
)
# Returns: Possession, shots, passes, formations
```

#### 6. get_team_stats
Quick statistical overview for one team.
```python
get_team_stats(team_name="Argentina")
# Returns: Matches, wins, goals, form
```

#### 7. query_csv
Flexible CSV querying with Simple and Custom modes.
```python
# Simple mode
query_csv(
    query_mode="simple",
    table="tactical_data",
    team_filter="Brazil",
    min_possession=60
)

# Custom mode (requires read_schema first)
query_csv(
    query_mode="custom",
    table="tactical_data",
    custom_filter="(home_possession > 65) & (home_score < away_score)"
)
```

#### 8. read_schema
Get complete data schema before custom queries.
```python
read_schema()
# Returns: Tables, columns, data types, formats, examples
```

---

## 🔒 Security & Safety

### Prompt Injection Prevention
- ✅ Input validation rejects malicious prompts
- ✅ Scope enforcement (football-only)
- ✅ System instruction protection

### Data Protection
- ✅ No file paths or schemas exposed
- ✅ No API keys or credentials revealed
- ✅ Output validation before delivery

### Domain Restriction
- ✅ Football-only scope
- ✅ Polite redirection for off-topic questions
- ✅ No opinions or controversial topics

---

## 📚 Setup Vector Database


### Process Documents
```bash
python scripts/var_lens_setup/process_documents.py
```

### Build Vector Store
```bash
python scripts/var_lens_setup/build_var_lens_vectorstore.py
```

---

## 📄 License

MIT License - see [`LICENSE`](LICENSE) file for details.

---

**Made with ❤️ for IBM AI Builders Challenge**
