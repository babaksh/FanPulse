# FanPulse Demo Scenarios

This document provides comprehensive demo scenarios for showcasing FanPulse's capabilities during the IBM Skills Build AI Builders Challenge.

---

## 🎯 Demo Overview

FanPulse demonstrates two complementary AI agents working together to enhance fan understanding of football matches:

1. **VAR-Lens**: Explains referee decisions using FIFA rules
2. **Tactical Pulse**: Analyzes match dynamics and predictions

---

## 📋 Demo Scenario 1: VAR Decision Explanation

### Context
During a World Cup match, a goal is disallowed due to offside. Fans are confused about the decision.

### User Query
> "Why was that goal disallowed? The player looked onside to me."

### VAR-Lens Response

**Step 1: Document Retrieval**
```
Retrieving relevant FIFA/IFAB rules...
✓ Found 3 relevant documents
  - Law 11: Offside
  - VAR Protocol
  - Offside Position Definition
```

**Step 2: LLM Analysis**
```
According to FIFA Law 11, a player is in an offside position if:

1. Any part of their head, body, or feet is in the opponents' half
2. Any part of their head, body, or feet is nearer to the opponents' 
   goal line than both the ball and the second-last opponent

In this case, VAR detected that the attacking player's shoulder was 
0.3 meters ahead of the last defender when the pass was made.

Key Points:
• Arms don't count for offside
• The decision is made at the moment the ball is played
• VAR uses calibrated lines for precision
• The decision was correct according to Law 11.2

Source: FIFA Laws of the Game 2024/25, Law 11
```

**Demo Value:**
- ✅ Clear explanation based on official rules
- ✅ Specific measurements (0.3m)
- ✅ Educational content for fans
- ✅ Source attribution

---

## 📋 Demo Scenario 2: Match Prediction

### Context
Fans want to know the likely outcome of an upcoming World Cup match.

### User Query
> "Who will win: Brazil vs Argentina?"

### Tactical Pulse Response

**Step 1: Data Analysis**
```
Analyzing recent form and statistics...

Brazil (Last 10 matches):
  Form: W-L-W-D-L-W-L-L-W-L
  Win Rate: 40%
  Goals: 15 scored, 12 conceded
  Form Score: 40/100

Argentina (Last 10 matches):
  Form: W-W-W-D-W-L-W-W-D-W
  Win Rate: 70%
  Goals: 22 scored, 8 conceded
  Form Score: 73/100
```

**Step 2: Head-to-Head Analysis**
```
Brazil vs Argentina (Last 5 matches):
  Record: 1W-1D-3L (Brazil perspective)
  Goals: 4-9
  Argentina has won 60% of recent encounters
```

**Step 3: Prediction**
```
Match Prediction: Brazil 1.2 - 1.8 Argentina

Win Probabilities:
  Brazil Win:    28.5%
  Draw:          23.0%
  Argentina Win: 48.5%

Key Factors:
• Argentina's superior recent form (73 vs 40)
• Better head-to-head record
• Stronger defensive record (0.8 vs 1.2 goals conceded/match)
• Home advantage for Brazil (+10%) already factored in

Confidence: Medium (based on 10-match sample)
```

**Demo Value:**
- ✅ Data-driven predictions
- ✅ Multiple factors considered
- ✅ Transparent methodology
- ✅ Confidence levels provided

---

## 📋 Demo Scenario 3: Tactical Analysis

### Context
During a match, a team changes formation. Fans want to understand why.

### User Query
> "Why did France switch to a 4-3-3 formation in the 58th minute?"

### Tactical Pulse Response

**Step 1: Context Analysis**
```
Match Context (Minute 58):
  Score: France 0-1 Germany
  Possession: France 45%, Germany 55%
  Shots: France 3, Germany 7
  Momentum: Shifting to Germany (62%)
```

**Step 2: Formation Analysis**
```
Formation Change: 4-4-2 → 4-3-3

Tactical Reasons:
1. Add Width
   • Deployed wingers (Mbappé, Dembélé) to stretch defense
   • Create 1v1 opportunities on flanks
   
2. Control Midfield
   • Added third central midfielder
   • Better ball retention and progression
   
3. Counter Germany's Press
   • 4-4-2 was being overrun in midfield
   • 4-3-3 provides better passing options

Expected Impact:
• Increased possession (target: 55%+)
• More shots from wide areas
• Better defensive balance
```

**Step 3: Outcome Analysis**
```
Impact (Minutes 58-75):
  Possession: 45% → 58% ✓
  Shots: 3 → 9 ✓
  Goals: 0 → 2 ✓
  Momentum: Shifted to France (68%)

Result: Formation change was highly effective
```

**Demo Value:**
- ✅ Real-time tactical insights
- ✅ Before/after comparison
- ✅ Educational for casual fans
- ✅ Data-backed analysis

---

## 📋 Demo Scenario 4: Combined Analysis

### Context
A controversial VAR decision affects match momentum. Fans want complete context.

### User Query
> "That VAR penalty decision changed everything. Was it correct? How did it affect the game?"

### Combined Response (VAR-Lens + Tactical Pulse)

**VAR-Lens Analysis:**
```
VAR Decision: Penalty Awarded

Rule Applied: Law 12 - Fouls and Misconduct
Incident: Handball in penalty area

According to Law 12.1:
"It is an offence if a player deliberately touches the ball with 
their hand/arm when it has made their body unnaturally bigger."

VAR Review Process:
1. On-field referee missed the incident
2. VAR detected potential handball
3. Referee reviewed on monitor
4. Clear and obvious error confirmed
5. Penalty awarded

Decision: CORRECT ✓
The defender's arm was in an unnatural position and made contact 
with the ball, preventing a goal-scoring opportunity.

Source: FIFA Laws of the Game, Law 12.1
```

**Tactical Pulse Analysis:**
```
Match Impact Analysis:

Before Penalty (Minute 67):
  Score: 1-1
  Momentum: Balanced (52% home)
  xG: Home 1.2, Away 1.1
  
After Penalty (Minute 68-90):
  Score: 2-1 (Home wins)
  Momentum: Shifted to Home (78%)
  xG: Home 2.4, Away 1.3

Key Changes:
• Home team gained psychological advantage
• Away team forced to attack, leaving gaps
• Home team controlled tempo
• 3 additional goal-scoring chances created

Conclusion: The penalty was a turning point that shifted 
momentum decisively in favor of the home team.
```

**Demo Value:**
- ✅ Combines rule explanation with tactical impact
- ✅ Shows agent collaboration
- ✅ Comprehensive fan understanding
- ✅ Demonstrates system integration

---

## 📋 Demo Scenario 5: Historical Analysis

### Context
Fans want context for an upcoming rivalry match.

### User Query
> "What's the history between Spain and Italy in major tournaments?"

### Tactical Pulse Response

**Step 1: Historical Data**
```
Spain vs Italy - Tournament History

Total Matches: 15
  Spain Wins: 8 (53%)
  Draws: 4 (27%)
  Italy Wins: 3 (20%)

Goals: Spain 18 - 12 Italy

Recent Form (Last 5):
  2024 UEFA Euro: Spain 1-0 Italy
  2023 Nations League: Spain 2-1 Italy
  2021 Euro Semi: Italy 1-1 Spain (Italy won on penalties)
  2021 Nations League: Italy 1-2 Spain
  2020 Friendly: Spain 1-1 Italy
```

**Step 2: Key Statistics**
```
Tournament Performance:
  World Cup: 2 meetings (1W-1D-0L Spain)
  UEFA Euro: 8 meetings (4W-2D-2L Spain)
  Nations League: 5 meetings (3W-1D-1L Spain)

Notable Matches:
• 2012 Euro Final: Spain 4-0 Italy (Dominant victory)
• 2021 Euro Semi: Italy 1-1 Spain (4-2 pens) (Dramatic)
• 2008 Euro QF: Spain 0-0 Italy (4-2 pens) (Tense)

Trends:
• Spain has dominated recent encounters (80% unbeaten)
• Matches are typically low-scoring (avg 2.0 goals)
• Often decided by fine margins
```

**Step 3: Prediction**
```
Next Match Prediction:

Based on:
• Spain's recent dominance (4W-1D in last 5)
• Current form scores (Spain 68, Italy 54)
• Historical tournament success

Predicted Outcome:
  Spain Win: 45%
  Draw: 30%
  Italy Win: 25%

Most Likely Score: Spain 1-0 Italy
(Tight, tactical match with Spain edging it)
```

**Demo Value:**
- ✅ Rich historical context
- ✅ Pattern identification
- ✅ Forward-looking prediction
- ✅ Engaging storytelling

---

## 🎬 Live Demo Script

### Setup (5 minutes)
1. Open FanPulse application
2. Show system architecture diagram
3. Explain dual-agent concept
4. Highlight IBM technologies used

### Demo Flow (15 minutes)

**Part 1: VAR-Lens (5 min)**
- Show offside decision scenario
- Demonstrate document retrieval
- Explain LLM reasoning
- Show source attribution

**Part 2: Tactical Pulse (5 min)**
- Show match prediction
- Demonstrate data analysis
- Explain metrics calculation
- Show probability breakdown

**Part 3: Integration (5 min)**
- Show combined analysis scenario
- Demonstrate agent collaboration
- Highlight real-world value
- Show API endpoints

### Q&A (5 minutes)
- Technical implementation
- Scalability considerations
- Future enhancements
- Challenge alignment

---

## 📊 Key Metrics to Highlight

### Technical Metrics
- **Response Time**: < 2 seconds
- **Accuracy**: Based on official FIFA rules
- **Data Coverage**: 49,329 matches, 336 teams
- **Vector Store**: 658 embeddings from 7 documents

### User Experience Metrics
- **Clarity**: Rule-based explanations
- **Transparency**: Source attribution
- **Accessibility**: Natural language interface
- **Educational**: Helps fans learn the game

### Innovation Metrics
- **Multi-Provider LLM**: 5 providers supported
- **Dual-Agent System**: Complementary capabilities
- **Modular Design**: Easy to extend
- **Production-Ready**: Comprehensive testing

---

## 🎯 Challenge Alignment

### Technical Execution ✅
- Functional RAG system
- Multi-provider architecture
- Comprehensive testing
- Production-ready code

### Innovation ✅
- Dual-agent approach
- Advanced football metrics
- Natural language insights
- Extensible design

### Challenge Fit ✅
- Addresses fan understanding
- Explains VAR decisions
- Analyzes tactical shifts
- Real-world applicability

### Implementation ✅
- Scalable architecture
- Well-documented
- Easy to deploy
- Maintainable codebase

---

## 🚀 Next Steps After Demo

1. **Deployment**: Deploy to cloud platform
2. **Integration**: Connect to live match data
3. **Enhancement**: Add more metrics and visualizations
4. **Expansion**: Support more languages and tournaments
5. **Mobile**: Create mobile app interface

---

## 📝 Demo Checklist

Before the demo:
- [x] Test all scenarios (18/18 tests passing)
- [x] Verify API keys are set (.env.example provided)
- [x] Check all services are running
- [ ] Prepare backup slides
- [ ] Test internet connection

During the demo:
- [ ] Explain problem statement
- [ ] Show architecture diagram
- [ ] Run live scenarios
- [ ] Highlight IBM technologies (Granite, Docling, Langflow)
- [ ] Answer questions confidently

After the demo:
- [ ] Gather feedback
- [ ] Note improvement areas
- [ ] Follow up on questions
- [x] Share documentation (9 comprehensive guides)
- [ ] Submit to challenge

---

*Demo scenarios designed for IBM Skills Build AI Builders Challenge - June 2026*