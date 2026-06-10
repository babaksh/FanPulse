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
│                    Tactical Pulse Agent                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Match      │  │   Tactical   │  │  Performance │      │
│  │   Data       │  │   Analysis   │  │   Metrics    │      │
│  │   Loader     │  │   Engine     │  │   Calculator │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   IBM Bob       │                        │
│                   │   Integration   │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   LLM (Granite) │                        │
│                   │   Explanation   │                        │
│                   └─────────────────┘                        │
│                                                               │
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
**Purpose**: Use IBM Bob for data science and predictive analytics

**Use Cases**:
- Match outcome prediction
- Player performance forecasting
- Tactical pattern recognition
- Historical trend analysis

**Integration Points**:
```python
- predict_match_outcome(team1, team2, context)
- analyze_historical_patterns(team, opponent)
- forecast_player_performance(player, conditions)
- identify_tactical_trends(matches)
```

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

### IBM Bob Integration
- **Jupyter Notebooks**: Analysis workflows
- **IBM Bob API**: Predictive analytics
- **Data visualization**: Match insights

### LLM Integration
- **IBM Granite**: Natural language generation
- **LangChain**: Orchestration
- **Custom prompts**: Tactical explanations

### Visualization
- **Matplotlib/Plotly**: Charts and graphs
- **Pitch visualization**: Formation diagrams
- **Heatmaps**: Pressure zones, pass networks

## Implementation Plan

### Phase 1: Data Foundation (Current)
- [x] Load match dataset (49,016 matches)
- [ ] Create data models
- [ ] Build data access layer
- [ ] Implement basic statistics

### Phase 2: Analysis Engine
- [ ] Formation detection
- [ ] Momentum calculation
- [ ] Performance metrics
- [ ] Pattern recognition

### Phase 3: IBM Bob Integration
- [ ] Set up Bob environment
- [ ] Create prediction models
- [ ] Integrate with analysis engine
- [ ] Test predictions

### Phase 4: LLM Integration
- [ ] Design tactical prompts
- [ ] Integrate with Granite
- [ ] Create explanation templates
- [ ] Test responses

### Phase 5: Langflow Orchestration
- [ ] Design Tactical Pulse flow
- [ ] Connect all components
- [ ] Test end-to-end
- [ ] Optimize performance

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
- ✅ Uses IBM Granite (LLM)
- ✅ Uses IBM Bob (data science)
- ✅ Addresses fan understanding
- ✅ Demonstrates explainable AI
- ✅ Real-world applicability

## Next Steps

1. **Implement Data Models** (1-2 hours)
   - Match, Team, Player classes
   - Statistics aggregation
   - Data validation

2. **Build Analysis Engine** (3-4 hours)
   - Formation detection algorithms
   - Momentum calculation
   - Performance metrics

3. **Integrate IBM Bob** (2-3 hours)
   - Set up notebooks
   - Create prediction models
   - API integration

4. **Create Langflow Flow** (1-2 hours)
   - Design workflow
   - Connect components
   - Test integration

5. **End-to-End Testing** (1-2 hours)
   - Test all features
   - Validate predictions
   - Optimize performance

**Total Estimated Time**: 8-13 hours

## Resources

- Match dataset: `data/match_data/results.csv`
- IBM Bob notebooks: `notebooks/`
- Analysis code: `src/agents/tactical_pulse/`
- API routes: `src/api/routes/tactical_pulse.py`
- Langflow template: `langflow_flows/tactical_pulse_agent.json`