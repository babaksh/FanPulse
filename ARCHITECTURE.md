# FanPulse - System Architecture

## 🎯 Project Name: **FanPulse**
> Feel the Football Pulse - Intelligent Game Understanding with AI

---

## 📋 Project Summary

**FanPulse** is an AI-powered platform that offers two intelligent agents to enhance the football viewing experience:

1. **VAR-Lens Agent**: Transparently explains VAR decisions using official FIFA documentation.
2. **Tactical Pulse Agent**: A real-time analyst of tactical changes and game momentum.

---

## 🏗️ General Architecture (Modular Architecture)

```
┌────────────────────────────────────────────────────────────┐
│                     FanPulse Platform                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Langflow Orchestration Layer               │  │
│  │ (Workflow management & communication between agents) │  │
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
│  │  • IBM Granite (NLG)                          │         │
│  │  • Context Forge (Context Management)         │         │
│  │  • Data Processing Pipeline                   │         │
│  └───────────────────────────────────────────────┘         │
│                         │                                  │
│  ┌──────────────────────▼───────────────────────┐          │
│  │          Data Sources Layer                  │          │
│  │  • Docling (FIFA Rules Processing)           │          │
│  │  • IBM Bob (Match Data Analytics)            │          │
│  │  • Static Datasets (Historical Data)         │          │
│  │  • Live Data API (Real-time Feed)            │          │
│  └──────────────────────────────────────────────┘          │
│                                                            │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │   API Layer (FastAPI/Flask)     │
        │   • REST Endpoints              │
        │   • WebSocket (optional)        │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │   Frontend (Optional - Phase 2) │
        │   • React Dashboard             │
        │   • Real-time Visualization     │
        └─────────────────────────────────┘
```

---

## 🔧 Implementation Strategy (2 Phases)

### **Phase 1: Core Backend + Langflow Demo** ⭐ (Priority)
- Full implementation of backend and agents
- Use Langflow UI for workflow demonstration
- Testing with static data and live data simulation
- **Advantage**: Faster, focus on AI and logic, stronger demo
- **Output**: A fully functional system demonstrable via Langflow

### **Phase 2: Frontend Dashboard** (Optional)
- If time permits, we will add a React dashboard
- **Advantage**: Better UX, more attractive for presentation
- **Note**: The project is complete and evaluable even without the frontend

---

## 📦 Project Structure (Modular)

```
FanPulse/
│
├── README.md                          # Main project documentation
├── ARCHITECTURE.md                    # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Sample environment variables
├── .gitignore
│
├── docs/                              # Supplementary documentation
│   ├── setup.md                       # Installation guide
│   ├── api-reference.md               # API documentation
│   └── demo-guide.md                  # Demo guide
│
├── data/                              # Datasets
│   ├── fifa_rules/                    # FIFA Rules (PDF/JSON)
│   ├── match_data/                    # Match Data
│   │   ├── historical/                # Historical data
│   │   └── sample_live/               # Sample live data for testing
│   └── processed/                     # Processed data
│
├── src/                               # Main source code
│   │
│   ├── agents/                        # Core Agents
│   │   ├── __init__.py
│   │   ├── var_lens/                  # VAR-Lens Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Main agent logic
│   │   │   ├── rule_retriever.py      # Rule retrieval
│   │   │   └── explainer.py           # Explanation generation
│   │   │
│   │   └── tactical_pulse/            # Tactical Pulse Agent
│   │       ├── __init__.py
│   │       ├── agent.py               # Main agent logic
│   │       ├── pattern_detector.py    # Tactical pattern detection
│   │       └── momentum_analyzer.py   # Momentum analysis
│   │
│   ├── services/                      # Shared Services
│   │   ├── __init__.py
│   │   ├── granite_service.py         # IBM Granite integration
│   │   ├── docling_service.py         # Docling integration
│   │   ├── bob_service.py             # IBM Bob integration
│   │   ├── context_forge_service.py   # Context Forge integration
│   │   └── data_processor.py          # Data processing
│   │
│   ├── orchestration/                 # Langflow workflows
│   │   ├── __init__.py
│   │   ├── var_lens_flow.json         # Workflow for VAR-Lens
│   │   ├── tactical_pulse_flow.json   # Workflow for Tactical Pulse
│   │   └── main_orchestrator.json     # Main orchestrator
│   │
│   ├── api/                           # API Layer
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── routes/
│   │   │   ├── var_lens.py
│   │   │   └── tactical_pulse.py
│   │   └── models/                    # Pydantic models
│   │       ├── var_request.py
│   │       └── tactical_request.py
│   │
│   ├── utils/                         # Utilities
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration
│   │   ├── logger.py                  # Logging
│   │   └── validators.py              # Validation
│   │
│   └── frontend/                      # Frontend (Phase 2 - Optional)
│       ├── package.json
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── App.jsx
│       └── public/
│
├── tests/                             # Tests
│   ├── test_var_lens.py
│   ├── test_tactical_pulse.py
│   └── test_integration.py
│
├── notebooks/                         # Jupyter notebooks for analysis
│   ├── data_exploration.ipynb
│   └── model_testing.ipynb
│
└── deployment/                        # Deployment files
    ├── docker-compose.yml
    ├── Dockerfile
    └── kubernetes/
```

---

## 🔄 Data Flow

### VAR-Lens Agent Flow:
```
User Input (VAR Decision) 
    → Langflow Orchestrator
    → VAR-Lens Agent
    → Docling (Retrieve relevant rules)
    → Context Forge (Context management)
    → IBM Granite (Generate explanation in simple language)
    → Response (Multilingual explanation)
```

### Tactical Pulse Agent Flow:
```
Match Data (Live/Static)
    → Langflow Orchestrator
    → Tactical Pulse Agent
    → IBM Bob (Statistical analysis)
    → Pattern Detection (Tactical changes detection)
    → Context Forge (Context integration)
    → IBM Granite (Generate analytical report)
    → Response (Analysis + data visualization)
```

---

## 🛠️ Used Technologies

### Core IBM Technologies:
- **IBM Granite**: Language model for NLG and explanation generation.
- **Docling**: Processing and extracting information from FIFA documents.
- **Langflow**: Orchestration and workflow management.
- **Context Forge**: Context management and data integration.
- **IBM Bob**: Data analysis and data science workflows.

### Supporting Technologies:
- **Python 3.10+**: Core language.
- **FastAPI**: API framework.
- **Pydantic**: Data validation.
- **SQLite/PostgreSQL**: Data storage (Optional).
- **React** (Phase 2): Frontend framework
- **Docker**: Containerization

---

## 🎯 Key Features

### VAR-Lens Agent:
✅ Explanation of VAR decisions based on official laws.  
✅ Multilingual support (English, Persian, Arabic, Spanish).  
✅ Displaying the exact relevant section of the law.  
✅ History of similar decisions.  

### Tactical Pulse Agent:
✅ Real-time tactical changes detection.  
✅ Momentum and game pressure analysis.  
✅ Goal probability prediction.  
✅ Tactical data visualization.  

---

## 📊 Success Criteria (Aligned with Judging Criteria)

### 1. Technical Execution (30%)
- ✅ Using 5 IBM tools (Granite, Docling, Langflow, Context Forge, Bob).
- ✅ Modular and extensible architecture.
- ✅ Clean and documented code.

### 2. Innovation (25%)
- ✅ Combining two agents for comprehensive coverage.
- ✅ Creative use of Docling for rule processing.
- ✅ Explainable AI approach.

### 3. Challenge Fit (25%)
- ✅ Covering 2 main areas: Trust & Transparency + Understanding.
- ✅ Relevant to World Cup and fan experience.
- ✅ Solving real problems.

### 4. Implementation & Feasibility (20%)
- ✅ Executable and testable.
- ✅ Scalable.
- ✅ Usable in the real world.

---

## 🚀 Development Roadmap

### Week 1: Setup & Foundation
- [ ] Set up development environment.
- [ ] Install and test IBM tools.
- [ ] Collect and process datasets.
- [ ] Build project structure.

### Week 2: Agent Development
- [ ] Implement VAR-Lens Agent.
- [ ] Implement Tactical Pulse Agent.
- [ ] Integrate with IBM services.

### Week 3: Orchestration & Integration
- [ ] Build Langflow workflows.
- [ ] Develop API layer.
- [ ] Integration testing.

### Week 4: Testing & Documentation
- [ ] Full system testing.
- [ ] Documentation.
- [ ] Prepare demo.
- [ ] (Optional) Frontend development.

---

## 💡 Important Notes

1. **Priority on Phase 1**: Focus on backend and Langflow demo.
2. **Modular Design**: Each agent is independent and extensible.
3. **Documentation**: Detailed documentation for judges.
4. **Demo-Ready**: Ready for demo from day one.
5. **Scalable**: Extensible for more features.

---

## 📝 Conclusion

This architecture allows us to:
- ✅ Start quickly (with Phase 1).
- ✅ Utilize all IBM tools.
- ✅ Have a strong and practical demo.
- ✅ Add a frontend if needed in Phase 2.
- ✅ Score well across all judging criteria.

**Recommendation**: Start with Phase 1 and, if time permits, add the frontend in Phase 2.