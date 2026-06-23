# Match Data Directory

## Overview

This directory contains the core match data for FanPulse football analytics, providing both historical match results and detailed tactical statistics.

## Files

### 1. `results.csv`
**Historical Match Results Database**

- **Coverage**: 1872-2026 (154 years)
- **Total Matches**: ~49,000 international matches
- **Match Types**: All competitions (World Cups, Euros, Copa América, friendlies, qualifiers, etc.)
- **Update Frequency**: Daily (live matches added in real-time)

**Columns**:
- `date`: Match date (YYYY-MM-DD)
- `home_team`, `away_team`: Team names
- `home_score`, `away_score`: Final scores
- `tournament`: Competition name
- `city`, `country`: Venue information
- `neutral`: Neutral venue flag (TRUE/FALSE)

**Use Cases**:
- Historical head-to-head records
- Win rates and goal statistics
- Recent form calculation (last 5-10 matches)
- Tournament participation history
- Long-term performance trends

**Limitations**:
- NO tactical details (possession, shots, passes, formations)
- NO player-level data
- NO referee information

---

### 2. `tactical_data.csv`
**Detailed Tactical Statistics from WhoScored**

- **Coverage**: 2026-onwards (6 matches as of June 2026, growing)
- **Data Source**: WhoScored.com via Playwright scraper
- **Metrics**: 41 tactical statistics per match
- **Update Method**: Manual addition via scraping script

**Key Metrics**:
- **Formations**: Home/away tactical systems (e.g., 4-3-3, 4-2-3-1)
- **Possession**: Average possession percentage
- **Shots**: Total shots, shots on target, shot accuracy
- **Passing**: Total passes, pass accuracy, key passes
- **Defending**: Tackles won, interceptions, clearances
- **Physical**: Aerial duels won, average age
- **Intensity Metrics**: Attacking intensity, defensive intensity

**Match ID Format**: `{PREFIX}_{YEAR}_{YYYY-MM-DD}_{HOME_TEAM}_{AWAY_TEAM}`
- Example: `WC_2026_2026-06-13_BRAZIL_MOROCCO`

**Use Cases**:
- In-depth tactical analysis (formations, possession, pressing)
- Shot quality and finishing efficiency assessment
- Passing patterns and ball retention analysis
- Defensive effectiveness measurement
- Playing style identification (possession vs direct)
- Formation matchup analysis

**Limitations**:
- Limited historical coverage (only manually scraped matches)
- Requires WhoScored data availability
- NO player-level statistics (team aggregates only)
- NO xG (expected goals) data

---

### 3. `data_schema.json`
**Complete Schema Reference for AI Agents**

- **Purpose**: Canonical schema reference for LangFlow agents
- **Content**: 
  - Detailed column definitions with types and examples
  - Calculated metrics formulas and interpretations
  - Query examples and best practices
  - Common mistakes to avoid
  - Agent reading guide

**Target Audience**: AI agents (LLMs) that need to understand data structure before querying

---

## Quick Start

### Python Examples

#### Get team statistics from results:
```python
import pandas as pd

# Load results
df = pd.read_csv('data/match_data/results.csv')
df['date'] = pd.to_datetime(df['date'])

# Get all Brazil matches
brazil = df[(df['home_team']=='Brazil') | (df['away_team']=='Brazil')]

# Recent form (last 10 matches)
recent = brazil.sort_values('date', ascending=False).head(10)

# Head-to-head
h2h = df[
    ((df['home_team']=='Brazil') & (df['away_team']=='Argentina')) |
    ((df['home_team']=='Argentina') & (df['away_team']=='Brazil'))
]
```

#### Get tactical data:
```python
import pandas as pd

# Load tactical data
df = pd.read_csv('data/match_data/tactical_data.csv')

# World Cup 2026 matches
wc2026 = df[df['match_id'].str.startswith('WC_2026')]

# High possession teams (>60%)
high_possession = df[
    (df['home_possession'] > 60) | (df['away_possession'] > 60)
]

# Efficient finishers (shot accuracy >40%)
efficient = df[
    (df['home_shot_accuracy'] > 40) | (df['away_shot_accuracy'] > 40)
]
```

---

## Match ID Prefixes

Match IDs use prefixes to identify competition types:

| Prefix | Tournament | Example |
|--------|-----------|---------|
| `WC_` | FIFA World Cup | `WC_2026-06-15_BRAZIL_ARGENTINA` |
| `EURO_` | UEFA Euro | `EURO_2024-07-14_SPAIN_ENGLAND` |
| `COPA_` | Copa América | `COPA_2024-07-14_ARGENTINA_COLOMBIA` |
| `FRIENDLY_` | Friendly | `FRIENDLY_2024-03-21_BRAZIL_SPAIN` |
| `AFCON_` | African Cup of Nations | `AFCON_2024-02-11_IVORY_COAST_NIGERIA` |
| `AFC_` | AFC Asian Cup | `AFC_2024-02-10_QATAR_JORDAN` |
| `GOLD_` | CONCACAF Gold Cup | `GOLD_2023-07-16_MEXICO_PANAMA` |
| `UNL_` | UEFA Nations League | `UNL_2024-10-14_SPAIN_DENMARK` |
| `OTHER_` | Qualifiers & Others | `OTHER_2023-11-16_ARGENTINA_URUGUAY` |

**Usage**: Filter by prefix to get specific tournament matches
```python
# World Cup matches only
world_cup = df[df['match_id'].str.startswith('WC_')]

# World Cup 2026 specifically
wc2026 = df[df['match_id'].str.startswith('WC_2026')]
```

---

## Data Quality

### results.csv
- **Source**: Historical football database (soccerdata library)
- **Accuracy**: High - official match records
- **Completeness**: All international matches since 1872
- **Update Method**: Automated daily updates

### tactical_data.csv
- **Source**: WhoScored.com (professional statistics provider)
- **Accuracy**: High - minute-by-minute data aggregated
- **Completeness**: All 41 metrics for every match in dataset
- **Update Method**: Manual scraping via Playwright automation

---

## Important Notes

### ⚠️ Data Availability
- **results.csv** has ALL matches (1872-2026)
- **tactical_data.csv** only has manually scraped matches
- Always check if a match exists in tactical_data.csv before claiming tactical data availability

### ⚠️ Calculated Metrics
Some metrics in tactical_data.csv are calculated:
- `shot_accuracy` = (shots_on_target / shots_total) × 100
- `pass_accuracy` = (passes_accurate / passes_total) × 100
- `tackle_success` = (tackles_won / tackles_total) × 100
- `attacking_intensity` = shots_total + key_passes
- `defensive_intensity` = tackles_won + interceptions + clearances

### ⚠️ Common Mistakes
1. ❌ Assuming tactical_data.csv has all matches from results.csv
   - ✅ Only manually scraped matches are in tactical_data.csv
2. ❌ Using results.csv for tactical details
   - ✅ Use tactical_data.csv for formations, possession, etc.
3. ❌ Fabricating tactical statistics when match not found
   - ✅ Acknowledge limitation clearly

---

## Related Directories

- **`data/referee_decisions/`**: VAR-reviewable decisions (goals, penalties, red cards)
- **`data/processed_documents/`**: FIFA/IFAB rules and regulations
- **`data/vector_stores/`**: FAISS vector stores for RAG systems

---

## Tools & Scripts

### Data Collection
- **`scripts/scrape_whoscored_network.py`**: Scrape tactical data from WhoScored
- **`scripts/update_live_matches_v2.py`**: Update results.csv with live matches

### LangFlow Components
- **`langflow_components/query_csv_tool.py`**: Query CSV data with filters
- **`langflow_components/get_tactical_data_tool.py`**: Get tactical statistics
- **`langflow_components/get_team_stats_tool.py`**: Get team performance stats
- **`langflow_components/analyze_team_tool.py`**: Analyze team performance
- **`langflow_components/compare_teams_tool.py`**: Compare two teams

---

## Schema Reference

For detailed schema information including:
- Complete column definitions with types and examples
- Calculated metrics formulas
- Query examples and best practices
- Agent reading guide

**See**: [`data_schema.json`](data_schema.json)

---

## Contributing

To add new matches to tactical_data.csv:
1. Use `scripts/scrape_whoscored_network.py` to scrape WhoScored data
2. Ensure match_id follows the format: `{PREFIX}_{YEAR}_{YYYY-MM-DD}_{HOME_TEAM}_{AWAY_TEAM}`
3. Verify all 41 columns are populated
4. Update this README if coverage changes significantly

---

**Last Updated**: June 2026  
**Maintained by**: FanPulse Team