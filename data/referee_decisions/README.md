# Referee Decisions Database

This directory contains referee decisions and VAR reviews from matches for the VAR-Lens agent.

## 📁 Structure

Each match has its own JSON file:
```
WC2026_2026_06_15_Brazil_Argentina.json
```

## 📋 File Format

```json
{
  "match_id": "WC2026_2026_06_15_Brazil_Argentina",
  "match_info": {
    "home_team": "Brazil",
    "away_team": "Argentina",
    "date": "2026-06-15",
    "tournament": "FIFA World Cup 2026",
    "venue": "MetLife Stadium",
    "city": "New York"
  },
  "referee_decisions": [
    {
      "minute": 67,
      "type": "goal_disallowed",
      "description": "Neymar goal cancelled for offside",
      "timestamp": "2026-06-15T16:07:00",
      "var_decision": {
        "reason": "offside",
        "review_duration": "2:15",
        "referee": "Pierluigi Collina",
        "details": "Neymar was 0.5 meters ahead...",
        "camera_angles": ["main", "behind_goal", "var_line"],
        "final_decision": "goal_cancelled"
      }
    }
  ]
}
```

## 🎯 Decision Types

- `goal_disallowed` - Goal cancelled by VAR
- `goal_allowed` - Goal confirmed by VAR
- `penalty_given` - Penalty awarded after VAR review
- `penalty_not_given` - Penalty denied after VAR review
- `red_card` - Red card given/upgraded by VAR
- `yellow_card` - Yellow card given/upgraded by VAR
- `offside` - Offside decision
- `handball` - Handball incident
- `foul` - Foul reviewed by VAR
- `other` - Other VAR-reviewable incident

## ➕ Adding Referee Decisions

### Method 1: Interactive Script
```bash
python scripts/add_referee_decision.py
```

Follow the prompts to add decision details.

### Method 2: Programmatic
```python
from scripts.add_referee_decision import add_referee_decision

add_referee_decision(
    match_id="WC2026_2026_06_15_Brazil_Argentina",
    minute=67,
    event_type="goal_disallowed",
    description="Neymar goal cancelled for offside",
    var_decision={
        "reason": "offside",
        "review_duration": "2:15",
        "referee": "Pierluigi Collina",
        "details": "Neymar was 0.5m ahead of last defender",
        "final_decision": "goal_cancelled"
    },
    match_info={
        "home_team": "Brazil",
        "away_team": "Argentina",
        "date": "2026-06-15",
        "tournament": "FIFA World Cup 2026"
    }
)
```

### Method 3: Manual JSON
Create a new JSON file following the format above.

## 🔍 Querying Referee Decisions

### In LangFlow
The `query_referee_decisions` tool is available in VAR-Lens agent:

```python
# Query all decisions for a match
query_referee_decisions("WC2026_2026_06_15_Brazil_Argentina")

# Query specific minute
query_referee_decisions("WC2026_2026_06_15_Brazil_Argentina", minute=67)
```

### Example Queries
- "What happened at minute 67 in Brazil vs Argentina?"
- "Why was the goal disallowed?"
- "Explain the penalty decision in minute 23"
- "What referee decisions were made in this match?"

## 🎯 How VAR-Lens Uses This

1. **User asks match-specific question**
   - "What happened at minute 67?"

2. **VAR-Lens uses query_referee_decisions**
   - Gets decision details from database

3. **VAR-Lens uses query_fifa_documents**
   - Gets relevant official rules

4. **VAR-Lens combines both**
   - Decision details + Official rule = Complete explanation

## 📊 Current Database

- **Total Matches**: 1
- **Total Decisions**: 3
- **Tournaments**: FIFA World Cup 2026

### Available Matches
- `WC2026_2026_06_15_Brazil_Argentina` (3 decisions)

## 🚀 Future Enhancements

- [ ] Real-time decision streaming from live matches
- [ ] Automatic decision extraction from match reports
- [ ] Timeline visualization
- [ ] Statistical analysis of referee decisions and VAR reviews
- [ ] Multi-language support

## 📝 Notes

- Decisions are sorted by minute automatically
- Each decision has a timestamp for tracking
- VAR reviews include review duration and camera angles
- Match info is stored once per match file

---

**Made with Bob**