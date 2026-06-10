# FanPulse ⚽🤖

**AI-Powered Football Analysis for the 2026 FIFA World Cup**

FanPulse is an intelligent dual-agent system that helps fans understand and experience football matches through explainable AI. Built for the IBM Skills Build AI Builders Challenge.

[![IBM Granite](https://img.shields.io/badge/IBM-Granite-blue)](https://www.ibm.com/granite)
[![Docling](https://img.shields.io/badge/IBM-Docling-green)](https://github.com/DS4SD/docling)
[![Langflow](https://img.shields.io/badge/Langflow-Orchestration-purple)](https://www.langflow.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow)](https://www.python.org/)

---

## 🎯 Overview

FanPulse combines two specialized AI agents to provide comprehensive football analysis:

### 🔍 **VAR-Lens Agent**
Explains Video Assistant Referee (VAR) decisions using official FIFA rules and regulations.

**Features:**
- 📚 RAG-powered explanations from 7 FIFA/IFAB documents
- 🎯 658-vector FAISS knowledge base
- 🤖 Multi-provider LLM support (IBM Granite, OpenAI, HuggingFace)
- 📖 Clear, rule-based explanations for fans

### ⚽ **Tactical Pulse Agent**
Analyzes tactical shifts, match dynamics, and team performance.

**Features:**
- 📊 49,329 historical matches analyzed
- 🏆 336 teams, 198 tournaments
- 📈 10 advanced metrics (xG, form, momentum, predictions)
- 🎲 Match outcome predictions with probabilities

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FanPulse                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   VAR-Lens       │         │  Tactical Pulse  │          │
│  │   Agent          │         │  Agent           │          │
│  ├──────────────────┤         ├──────────────────┤          │
│  │ • RAG Engine     │         │ • Data Loader    │          │
│  │ • FAISS Store    │         │ • Metrics Calc   │          │
│  │ • FIFA Docs      │         │ • Match Analyzer │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │                                     │
│              ┌─────────▼─────────┐                           │
│              │  LLM Factory      │                           │
│              │  (5 Providers)    │                           │
│              └─────────┬─────────┘                           │
│                        │                                     │
│              ┌─────────▼─────────┐                           │
│              │  IBM Granite      │                           │
│              │  OpenAI / HF      │                           │
│              └───────────────────┘                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/FanPulse.git
cd FanPulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-llm.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Add your API keys to `.env`:

```bash
# IBM Granite (Recommended for challenge)
IBM_WATSONX_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here

# Or OpenAI (For quick testing)
OPENAI_API_KEY=sk-your_key_here

# Or HuggingFace (Free alternative)
HUGGINGFACE_API_KEY=hf_your_token_here
```

### Running Tests

```bash
# Test VAR-Lens document retrieval
python scripts/test_var_lens_rag.py

# Test Tactical Pulse data loading
python scripts/test_data_loader.py

# Test metrics calculation
python src/agents/tactical_pulse/metrics_calculator.py

# Test match analysis
python scripts/test_match_analyzer.py

# Test with LLM (requires API key)
python scripts/test_var_lens_with_llm.py
```

### Running the API

```bash
# Start FastAPI server
uvicorn src.api.main:app --reload

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## 📚 Documentation

- **[Setup Guide](docs/var-lens-setup-guide.md)** - Complete setup instructions
- **[LLM Setup](docs/llm-setup-guide.md)** - Configure LLM providers
- **[API Documentation](src/api/README.md)** - REST API reference
- **[Langflow Guide](docs/langflow-quick-start.md)** - Visual workflow setup
- **[Tactical Pulse Design](docs/tactical-pulse-design.md)** - Architecture details

---

## 🎮 Usage Examples

### VAR-Lens: Explain VAR Decisions

```python
from src.agents.var_lens.rag_engine import VARLensRAG

# Initialize
rag = VARLensRAG()
rag.load_vector_store()

# Create QA chain with IBM Granite
rag.create_qa_chain(provider="ibm_granite")

# Ask questions
result = rag.query("What is the VAR protocol for offside decisions?")
print(result['answer'])
```

### Tactical Pulse: Analyze Matches

```python
from src.agents.tactical_pulse.match_analyzer import MatchAnalyzer

# Initialize
analyzer = MatchAnalyzer()

# Analyze team
analysis = analyzer.analyze_team("Brazil", num_matches=10)
print(f"Form: {analysis['form']['form_string']}")
print(f"Win Rate: {analysis['statistics']['win_rate']:.1%}")

# Predict match
prediction = analyzer.predict_match("Brazil", "Argentina")
print(f"Prediction: {prediction['prediction']['predicted_score']}")
print(f"Home Win: {prediction['prediction']['home_win_probability']}%")
```

### Using the API

```bash
# VAR-Lens query
curl -X POST "http://localhost:8000/api/var-lens/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is VAR?"}'

# Match prediction
curl -X POST "http://localhost:8000/api/tactical-pulse/predict" \
  -H "Content-Type: application/json" \
  -d '{"team1": "Brazil", "team2": "Argentina"}'
```

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.11+** - Primary language
- **LangChain** - RAG framework
- **FAISS** - Vector database
- **FastAPI** - REST API
- **Pandas** - Data processing

### IBM Technologies
- **IBM Granite** - Large Language Model
- **Docling** - Document processing
- **Langflow** - Visual orchestration
- **IBM Bob** - AI-powered coding assistant for developers

### LLM Providers
- IBM Granite (watsonx.ai)
- OpenAI (GPT-4, GPT-3.5)
- HuggingFace (Mistral, Llama)
- Anthropic Claude
- Google Gemini

---

## 📊 Project Statistics

- **Lines of Code**: ~10,800
- **Python Modules**: 15
- **Test Scripts**: 9
- **Documentation**: 9 files (~3,600 lines)
- **Tests Passing**: 18/18 ✅
- **FIFA Documents**: 7 (450 KB)
- **Vector Store**: 658 vectors
- **Match Dataset**: 49,329 matches
- **Teams**: 336
- **Tournaments**: 198

---

## 🎯 Challenge Criteria

### ✅ Technical Execution
- Functional RAG system with FAISS
- Multi-provider LLM architecture
- Comprehensive test coverage
- Production-ready API

### ✅ Innovation
- Dual-agent system (VAR + Tactical)
- Multi-provider LLM factory
- Advanced football metrics
- Natural language insights

### ✅ Challenge Fit
- Addresses fan understanding
- Explains VAR decisions
- Analyzes tactical shifts
- Real-world applicability

### ✅ Implementation & Feasibility
- Modular, extensible design
- Scalable architecture
- Well-documented
- Easy to deploy

---

## 📁 Project Structure

```
FanPulse/
├── src/
│   ├── agents/
│   │   ├── var_lens/
│   │   │   ├── rag_engine.py          # RAG implementation
│   │   │   └── llm_providers.py       # Multi-provider LLM
│   │   └── tactical_pulse/
│   │       ├── data_loader.py         # Match data loading
│   │       ├── metrics_calculator.py  # Advanced metrics
│   │       └── match_analyzer.py      # Match analysis
│   └── api/
│       ├── main.py                    # FastAPI app
│       └── routes/
│           ├── var_lens.py            # VAR endpoints
│           └── tactical_pulse.py      # Tactical endpoints
├── data/
│   ├── processed_documents/           # FIFA docs (Markdown)
│   ├── vector_stores/                 # FAISS indices
│   └── match_data/                    # Football dataset
├── scripts/
│   ├── test_var_lens_rag.py          # VAR tests
│   ├── test_data_loader.py           # Data tests
│   ├── test_match_analyzer.py        # Analysis tests
│   └── test_var_lens_with_llm.py     # LLM tests
├── docs/
│   ├── var-lens-setup-guide.md       # Setup guide
│   ├── llm-setup-guide.md            # LLM configuration
│   ├── tactical-pulse-design.md      # Architecture
│   └── langflow-quick-start.md       # Langflow guide
├── langflow_flows/
│   └── var_lens_agent_template.json  # Langflow template
├── requirements.txt                   # Core dependencies
├── requirements-llm.txt               # LLM dependencies
├── .env.example                       # Environment template
└── README.md                          # This file
```

---

## 🧪 Testing

All components have comprehensive test coverage:

```bash
# Run all tests
python scripts/test_var_lens_rag.py      # ✅ 3/3 tests
python scripts/test_data_loader.py       # ✅ 6/6 tests
python scripts/test_match_analyzer.py    # ✅ 5/5 tests
python src/agents/tactical_pulse/metrics_calculator.py  # ✅ 4/4 tests
```

**Total: 18/18 tests passing** ✅

---

## 🤝 Contributing

This project was built for the IBM Skills Build AI Builders Challenge. Contributions, issues, and feature requests are welcome!

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **IBM Skills Build** - For hosting the challenge
- **IBM Granite Team** - For the powerful LLM
- **Docling Team** - For document processing
- **Langflow Community** - For visual orchestration
- **FIFA/IFAB** - For official rules and regulations

---

## 📧 Contact

For questions or feedback about this project:
- GitHub Issues: [Create an issue](https://github.com/yourusername/FanPulse/issues)
- Challenge Platform: [IBM Skills Build](https://ibmskillsbuildchallenge-hub.bemyapp.com/)

---

## 🎉 Built with ❤️ for the 2026 FIFA World Cup

**FanPulse** - Making football more accessible and understandable for fans worldwide through AI.

---

*Last Updated: June 2026*
