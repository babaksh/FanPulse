# Tactical Pulse Agent - Design Document

## Overview

The **Tactical Pulse Agent** is the second core component of FanPulse, designed to analyze tactical shifts, match dynamics, and team performance using AI and match data analytics.

## Purpose

While VAR-Lens focuses on explaining referee decisions, Tactical Pulse helps fans understand:
- **Tactical Changes**: Formation shifts, substitution impacts
- **Match Momentum**: Which team is dominating and why
- **Performance Analysis**: Player and team statistics
- **Predictive Insights**: Likely outcomes based on current trends

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Tactical Pulse Agent                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Match      │  │   Tactical   │  │  Performance │       │
│  │   Data       │  │   Analysis   │  │   Metrics    │       │
│  │   Loader     │  │   Engine     │  │   Calculator │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   IBM Bob       │                       │
│                   │   Integration   │                       │
│                   └────────┬────────┘                       │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   LLM (Granite) │                       │
│                   │   Explanation   │                       │
│                   └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Match Data Loader
**Purpose**: Load and preprocess match data from various sources

**Data Sources**:
- Historical match results (CSV dataset - 49,016 matches)
- Live match statistics (API integration)
- Team formations and lineups
- Player statistics

**Key Functions**:
```python
- load_match_data(match_id)
- get_team_stats(team_name, season)
- get_player_stats(player_name)
- get_head_to_head(team1, team2)
```

### 2. Tactical Analysis Engine
**Purpose**: Analyze tactical patterns and identify key moments

**Analysis Types**:
- **Formation Analysis**: Detect formation changes (4-4-2 → 4-3-3)
- **Momentum Shifts**: Identify when momentum changes
- **Pressure Zones**: Where teams are applying pressure
- **Substitution Impact**: Effect of player changes

**Key Functions**:
```python
- analyze_formation(match_data)
- detect_momentum_shift(timeline)
- calculate_possession_zones(events)
- evaluate_substitution_impact(sub_event)
```

### 3. Performance Metrics Calculator
**Purpose**: Calculate advanced statistics and metrics

**Metrics**:
- **xG (Expected Goals)**: Goal-scoring probability
- **Pass Completion Rate**: Accuracy by zone
- **Pressing Intensity**: High/medium/low press
- **Defensive Line Height**: High/low block
- **Transition Speed**: Counter-attack effectiveness

**Key Functions**:
```python
- calculate_xg(shots)
- analyze_passing_network(passes)
- measure_pressing_intensity(events)
- evaluate_defensive_shape(positions)
```

### 4. IBM Bob Integration
**Purpose**: IBM Bob is an AI-powered coding assistant that helps developers write better code

**Note**: IBM Bob is a development tool (similar to GitHub Copilot) that assists with:
- Code generation and completion
- Bug detection and fixes
- Code optimization suggestions
- Documentation generation

**For FanPulse**: We use traditional data science libraries (Pandas, NumPy, Scikit-learn) for:
- Match outcome prediction
- Player performance forecasting
- Tactical pattern recognition
- Historical trend analysis

### 5. LLM Explanation Layer
**Purpose**: Generate natural language explanations

**Explanation Types**:
- "Why did the team switch to 3-5-2?"
- "What caused the momentum shift in minute 67?"
- "How effective was the high press?"
- "What's the impact of this substitution?"

## Data Flow

```
1. User Query
   ↓
2. Parse Intent (tactical question vs. performance question)
   ↓
3. Load Relevant Match Data
   ↓
4. Perform Analysis (formations, metrics, patterns)
   ↓
5. IBM Bob Processing (predictions, insights)
   ↓
6. LLM Generation (natural language explanation)
   ↓
7. Return Response with visualizations
```

## Key Features

### 1. Real-Time Analysis
- Live match commentary
- Minute-by-minute tactical updates
- Momentum tracking
- Key moment identification

### 2. Historical Context
- Head-to-head records
- Team form analysis
- Player performance trends
- Tactical evolution over time

### 3. Predictive Insights
- Match outcome probabilities
- Goal-scoring likelihood
- Substitution recommendations
- Tactical adjustment suggestions

### 4. Educational Content
- Tactical concept explanations
- Formation guides
- Strategy breakdowns
- Performance metric definitions

## Example Queries

### Tactical Questions
```
Q: "Why did Brazil switch to a 4-3-3 formation?"
A: Brazil switched to 4-3-3 in the 58th minute to:
   - Add width with wingers (Neymar, Raphinha)
   - Control midfield with 3 CMs
   - Counter Argentina's 4-4-2 press
   Impact: Possession increased from 48% to 61%
```

### Performance Questions
```
Q: "How is Messi performing compared to his average?"
A: Messi's current performance:
   - Passes: 47/52 (90%) vs. avg 85%
   - Key passes: 6 vs. avg 4.2
   - Dribbles: 8/11 (73%) vs. avg 68%
   - xG contribution: 1.8 vs. avg 1.3
   Rating: Above average performance
```

### Momentum Questions
```
Q: "When did the momentum shift?"
A: Momentum shifted at minute 67:
   - Event: France's equalizer (1-1)
   - Before: England 68% possession, 0.8 xG
   - After: France 58% possession, 1.2 xG
   - Tactical change: France pressed higher
```

## Technology Stack

### Data Processing
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Scikit-learn**: ML models for predictions

### Data Science Tools
- **Pandas & NumPy**: Data analysis
- **Scikit-learn**: Predictive models
- **Matplotlib/Plotly**: Data visualization

### LLM Integration
- **IBM Granite**: Natural language generation
- **LangChain**: Orchestration
- **Custom prompts**: Tactical explanations

### Visualization
- **Matplotlib/Plotly**: Charts and graphs
- **Pitch visualization**: Formation diagrams
- **Heatmaps**: Pressure zones, pass networks

## Implementation Plan

### Phase 1: Data Foundation
- [x] Load match dataset (49,329 matches)
- [x] Create data models (DataLoader, MetricsCalculator, MatchAnalyzer)
- [x] Build data access layer
- [x] Implement basic statistics

### Phase 2: Analysis Engine
- [x] Formation detection algorithms
- [x] Momentum calculation (10 metrics)
- [x] Performance metrics (xG, form, predictions)
- [x] Pattern recognition

### Phase 3: Predictive Models
- [x] Match prediction algorithm
- [x] Form calculation
- [x] Head-to-head analysis
- [x] Test predictions (18/18 tests passing)

### Phase 4: LLM Integration
- [x] Design tactical prompts
- [x] Integrate with Granite (multi-provider support)
- [x] Create explanation templates
- [x] Test responses

### Phase 5: Production Ready
- [x] Comprehensive testing
- [x] Documentation
- [x] GitHub repository
- [x] Ready for deployment

## API Endpoints

### Match Analysis
```
POST /api/tactical-pulse/analyze-match
Body: { "match_id": "12345", "minute": 67 }
Response: Tactical analysis with insights
```

### Formation Analysis
```
POST /api/tactical-pulse/analyze-formation
Body: { "match_id": "12345", "team": "Brazil" }
Response: Formation details and effectiveness
```

### Momentum Tracking
```
POST /api/tactical-pulse/momentum
Body: { "match_id": "12345" }
Response: Momentum timeline with key events
```

### Performance Metrics
```
POST /api/tactical-pulse/player-stats
Body: { "player_name": "Messi", "match_id": "12345" }
Response: Detailed player statistics
```

### Predictions
```
POST /api/tactical-pulse/predict
Body: { "team1": "Brazil", "team2": "Argentina" }
Response: Match prediction with probabilities
```

## Integration with VAR-Lens

The two agents work together:

```
User: "Was that offside call correct, and how did it affect the game?"

VAR-Lens Response:
"Yes, the offside was correct. Player was 0.3m ahead of the last defender
when the pass was made. According to Law 11..."

Tactical Pulse Response:
"This offside call stopped Brazil's counter-attack momentum. Before this:
- Brazil had 3 dangerous attacks in 5 minutes
- Momentum score: 72% Brazil
After the call:
- Argentina regained possession
- Momentum shifted to 58% Argentina
- Brazil's high line became more cautious"
```

## Success Metrics

### Technical
- Response time < 2 seconds
- Prediction accuracy > 70%
- Data processing < 500ms
- LLM generation < 1 second

### User Experience
- Clear, understandable explanations
- Accurate tactical insights
- Relevant historical context
- Actionable predictions

### Challenge Criteria
- ✅ Uses IBM Granite (LLM for natural language generation)
- ✅ Uses IBM Docling (document processing)
- ✅ Uses Langflow (visual orchestration)
- ✅ Addresses fan understanding
- ✅ Demonstrates explainable AI
- ✅ Real-world applicability

## Deployment Steps

1. **Set up environment**
   - Install dependencies
   - Configure API keys
   - Build vector stores

2. **Test all components**
   - Run test scripts (18/18 passing)
   - Verify LLM integration
   - Check data loading

3. **Deploy to cloud**
   - Choose platform (AWS/Azure/GCP)
   - Set up CI/CD
   - Configure monitoring

4. **Integration testing**
   - End-to-end tests
   - Performance testing
   - Load testing

5. **Go live**
   - Monitor metrics
   - Gather feedback
   - Iterate improvements

## Resources

- Match dataset: `data/match_data/results.csv`
- IBM Bob notebooks: `notebooks/`
- Analysis code: `src/agents/tactical_pulse/`
- API routes: `src/api/routes/tactical_pulse.py`
- Langflow template: `langflow_flows/tactical_pulse_agent.json`