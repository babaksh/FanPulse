"""
Query CSV Tool for LangFlow
Provides flexible CSV querying with schema awareness (Self-Contained Version)
"""

from lfx.custom import Component
from lfx.io import Output
from lfx.field_typing import Tool
from langchain_core.tools import StructuredTool
from pathlib import Path
import pandas as pd
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QueryCSVTool(Component):
    display_name: str = "Query CSV"
    description: str = "Query CSV data with filters and schema awareness"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "database"
    name: str = "query_csv_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.schema_path = self.project_root / "data" / "match_data" / "data_schema.json"
        self.results_csv = self.project_root / "data" / "match_data" / "results.csv"
        self.tactical_csv = self.project_root / "data" / "match_data" / "tactical_data.csv"
        self.schema = None
    
    def _load_schema(self):
        """Load data schema from JSON file"""
        if self.schema is None:
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                self.log(f"Schema loaded: {len(self.schema)} sections")
            except Exception as e:
                self.log(f"Warning: Could not load schema: {e}")
                self.schema = {}
        return self.schema
    
    def build_tool(self) -> Tool:
        """Build the CSV query tool"""
        
        def query_csv(
            table: str,
            query_mode: str = "simple",
            team_filter: Optional[str] = None,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None,
            tournament_filter: Optional[str] = None,
            formation_filter: Optional[str] = None,
            min_possession: Optional[float] = None,
            max_possession: Optional[float] = None,
            custom_filter: Optional[str] = None,
            resolve_loser_stat: Optional[str] = None,
            resolve_winner_stat: Optional[str] = None,
            team_perspective: Optional[str] = None,
            columns: Optional[str] = None,
            limit: int = 50
        ) -> str:
            """Query CSV data with filters - supports both simple and custom query modes.
            
            Args:
                table: Table name - "results" or "tactical_data"
                query_mode: Query mode - "simple" (use predefined filters) or "custom" (use custom_filter)
                
                SIMPLE MODE PARAMETERS (query_mode="simple"):
                team_filter: Team name to filter (searches both home and away)
                date_from: Start date (YYYY-MM-DD format)
                date_to: End date (YYYY-MM-DD format)
                tournament_filter: Tournament name OR match_id prefix filter
                    - For tournament names: "FIFA World Cup", "Friendly", "UEFA Euro"
                    - For match_id prefixes: "WC_2026" (World Cup 2026), "EURO_2024", "FRIENDLY_2025"
                    - Smart detection: if contains underscore + digits, searches match_id; otherwise searches tournament name
                formation_filter: Formation to filter (e.g., "4-3-3", "4-2-3-1") - only for tactical_data table
                    - Searches both home_formation and away_formation columns
                min_possession: Minimum possession percentage (0-100) - only for tactical_data table
                    - Filters matches where either team has >= this possession
                max_possession: Maximum possession percentage (0-100) - only for tactical_data table
                    - Filters matches where either team has <= this possession
                
                CUSTOM MODE PARAMETERS (query_mode="custom"):
                custom_filter: Pandas boolean expression for filtering (e.g., "(home_shots_total > 15) & (away_shots_total > 15)")
                    - Use column names from schema
                    - Supported operators: >, <, >=, <=, ==, !=, &, |, ~
                    - Examples:
                        * "(home_possession > 60) & (home_score > away_score)"
                        * "(home_shots_on_target / home_shots_total > 0.5)"
                        * "home_team.str.contains('Brazil')"

                PERSPECTIVE PARAMETERS (optional, work with any query_mode):

                resolve_loser_stat: Base stat column name WITHOUT home_/away_ prefix.
                    Resolves home/away using scores → returns one row per LOSING team.
                    Output columns: date | losing_team | opponent | result | loser_<stat>
                    Use for: "teams that lost despite high X", "which teams lost with >80% pass accuracy"

                resolve_winner_stat: Base stat column name WITHOUT home_/away_ prefix.
                    Resolves home/away using scores → returns one row per WINNING team.
                    Output columns: date | winning_team | opponent | result | winner_<stat>
                    Use for: "teams that won with low possession", "winners with most shots"

                team_perspective: Team name to focus on (e.g. "Brazil").
                    Resolves each row so the named team's stats are always in the same columns,
                    regardless of whether they were home or away.
                    Output columns: date | team | opponent | result | team_<stat1> | team_<stat2> | ...
                    The stats returned are those listed in the `columns` parameter (without home_/away_ prefix).
                    Use for: "Brazil's stats in each match", "Spain's possession per game",
                             "how did France perform in each WC 2026 match?"
                    Requires: `columns` to list the base stat names to include (e.g. "possession,pass_accuracy,shots_total")
                    Note: resolve_loser_stat / resolve_winner_stat take priority if also provided.

                columns: Comma-separated base stat names (WITHOUT home_/away_ prefix) when team_perspective is set.
                    Otherwise: full column names to display (e.g., "date,home_team,away_team,home_score").
                    Ignored when resolve_loser_stat or resolve_winner_stat is set.
                
                COMMON PARAMETERS:
                limit: Maximum rows to return (default: 50, max: 200)
                
            Returns:
                Query results in markdown table format.
                resolve_loser_stat  → date | losing_team  | opponent | result | loser_<stat>
                resolve_winner_stat → date | winning_team | opponent | result | winner_<stat>
                team_perspective    → date | team | opponent | result | team_<stat> ...
                default             → raw filtered rows
            """
            try:
                # Auto-detect mode if custom_filter is provided
                if custom_filter and query_mode == "simple":
                    query_mode = "custom"
                    self.log("Auto-switching to custom mode because custom_filter was provided")
                
                self.log(f"Querying {table} in {query_mode} mode")
                self.status = f"Querying {table}..."
                
                # Load schema
                schema = self._load_schema()
                
                # Validate query_mode
                if query_mode not in ["simple", "custom"]:
                    return f"❌ Invalid query_mode: {query_mode}. Must be 'simple' or 'custom'"
                
                # Validate table
                if table not in ["results", "tactical_data"]:
                    return f"❌ Invalid table: {table}. Must be 'results' or 'tactical_data'"
                
                # Select CSV file
                csv_path = self.results_csv if table == "results" else self.tactical_csv
                
                if not csv_path.exists():
                    return f"❌ CSV file not found: {csv_path}"
                
                # Read CSV
                df = pd.read_csv(csv_path)
                df['date'] = pd.to_datetime(df['date'])
                
                # Apply filters based on mode
                filtered_df = df.copy()
                
                if query_mode == "custom":
                    # CUSTOM MODE: Use custom_filter expression
                    if not custom_filter:
                        return "❌ custom_filter is required when query_mode='custom'"
                    
                    try:
                        # Validate custom_filter for safety
                        dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file', 'os.', 'sys.']
                        if any(keyword in custom_filter.lower() for keyword in dangerous_keywords):
                            return f"❌ Unsafe expression in custom_filter. Avoid: {', '.join(dangerous_keywords)}"
                        
                        # Apply custom filter using query()
                        self.log(f"Applying custom filter: {custom_filter}")
                        filtered_df = df.query(custom_filter)
                        
                    except Exception as e:
                        return f"❌ Error in custom_filter: {e}\n\n" \
                               f"Tips:\n" \
                               f"- Use column names from schema (check with read_schema tool)\n" \
                               f"- Use & for AND, | for OR, ~ for NOT\n" \
                               f"- Use parentheses for complex expressions\n" \
                               f"- For string operations: column.str.contains('text')\n" \
                               f"- Example: (home_possession > 60) & (home_score > away_score)"
                
                else:
                    # SIMPLE MODE: Use predefined filters
                    # Team filter
                    if team_filter:
                        filtered_df = filtered_df[
                            (filtered_df['home_team'].str.contains(team_filter, case=False, na=False)) |
                            (filtered_df['away_team'].str.contains(team_filter, case=False, na=False))
                        ]
                    
                    # Date filters
                    if date_from:
                        try:
                            date_from_dt = pd.to_datetime(date_from)
                            filtered_df = filtered_df[filtered_df['date'] >= date_from_dt]
                        except:
                            return f"❌ Invalid date_from format: {date_from}. Use YYYY-MM-DD"
                    
                    if date_to:
                        try:
                            date_to_dt = pd.to_datetime(date_to)
                            filtered_df = filtered_df[filtered_df['date'] <= date_to_dt]
                        except:
                            return f"❌ Invalid date_to format: {date_to}. Use YYYY-MM-DD"
                    
                    # Tournament filter - smart detection
                    if tournament_filter:
                        import re as _re
                        is_match_id_prefix = '_' in tournament_filter and any(char.isdigit() for char in tournament_filter)

                        if is_match_id_prefix and 'match_id' in filtered_df.columns:
                            # e.g. "WC_2026", "EURO_2024" — filter by match_id prefix
                            filtered_df = filtered_df[
                                filtered_df['match_id'].str.contains(tournament_filter, case=False, na=False)
                            ]
                        elif 'tournament' in filtered_df.columns:
                            # Check if a 4-digit year is appended to the tournament name
                            # e.g. "FIFA World Cup 2026" → name="FIFA World Cup", year=2026
                            year_match = _re.search(r'\b(18|19|20)\d{2}\b', tournament_filter)
                            if year_match:
                                year = int(year_match.group())
                                tournament_name = tournament_filter[:year_match.start()].strip()
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(tournament_name, case=False, na=False)
                                ]
                                # Apply year constraint via date column
                                filtered_df = filtered_df[
                                    filtered_df['date'].dt.year == year
                                ]
                            else:
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(tournament_filter, case=False, na=False)
                                ]
                    
                    # Formation filter (only for tactical_data)
                    if formation_filter and table == "tactical_data":
                        if 'home_formation' in filtered_df.columns and 'away_formation' in filtered_df.columns:
                            filtered_df = filtered_df[
                                (filtered_df['home_formation'].str.contains(formation_filter, case=False, na=False)) |
                                (filtered_df['away_formation'].str.contains(formation_filter, case=False, na=False))
                            ]
                    
                    # Possession filters (only for tactical_data)
                    if (min_possession is not None or max_possession is not None) and table == "tactical_data":
                        if 'home_possession' in filtered_df.columns and 'away_possession' in filtered_df.columns:
                            if min_possession is not None:
                                filtered_df = filtered_df[
                                    (filtered_df['home_possession'] >= min_possession) |
                                    (filtered_df['away_possession'] >= min_possession)
                                ]
                            if max_possession is not None:
                                filtered_df = filtered_df[
                                    (filtered_df['home_possession'] <= max_possession) |
                                    (filtered_df['away_possession'] <= max_possession)
                                ]
                
                # Apply limit
                limit = min(limit, 200)  # Max 200 rows
                filtered_df = filtered_df.head(limit)
                
                if filtered_df.empty:
                    return f"❌ No data found matching filters:\n" \
                           f"- Table: {table}\n" \
                           f"- Team: {team_filter or 'Any'}\n" \
                           f"- Date From: {date_from or 'Any'}\n" \
                           f"- Date To: {date_to or 'Any'}\n" \
                           f"- Tournament: {tournament_filter or 'Any'}"

                # ----------------------------------------------------------------
                # RESOLVE LOSER STAT: resolve home/away ambiguity in Python
                # so the model receives one clean row per losing team.
                # ----------------------------------------------------------------
                if resolve_loser_stat:
                    home_col = f"home_{resolve_loser_stat}"
                    away_col = f"away_{resolve_loser_stat}"
                    for col in [home_col, away_col, "home_score", "away_score"]:
                        if col not in filtered_df.columns:
                            return f"❌ Column '{col}' not found. Check resolve_loser_stat value."

                    records = []
                    for _, row in filtered_df.iterrows():
                        h = row["home_score"]
                        a = row["away_score"]
                        if h == a:
                            continue  # draw — no loser
                        if h < a:
                            loser, opponent = row["home_team"], row["away_team"]
                            loser_stat = row[home_col]
                            result_str = f"Lost {int(h)}–{int(a)}"
                        else:
                            loser, opponent = row["away_team"], row["home_team"]
                            loser_stat = row[away_col]
                            result_str = f"Lost {int(a)}–{int(h)}"
                        records.append({
                            "date": str(row["date"])[:10],
                            "losing_team": loser,
                            "opponent": opponent,
                            "result": result_str,
                            f"loser_{resolve_loser_stat}": round(float(loser_stat), 1),
                        })

                    if not records:
                        return "Based on all available data, no matches met this criterion."

                    resolved_df = pd.DataFrame(records)
                    result = f"# 📊 Match Results: Tournament Tactical Database\n\n"
                    result += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    result += "## Data:\n\n"
                    result += resolved_df.to_markdown(index=False)
                    result += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Resolved {len(resolved_df)} losing teams"
                    return result

                # ----------------------------------------------------------------
                # RESOLVE WINNER STAT
                # ----------------------------------------------------------------
                if resolve_winner_stat:
                    home_col = f"home_{resolve_winner_stat}"
                    away_col = f"away_{resolve_winner_stat}"
                    for col in [home_col, away_col, "home_score", "away_score"]:
                        if col not in filtered_df.columns:
                            return f"❌ Column '{col}' not found. Check resolve_winner_stat value."

                    records = []
                    for _, row in filtered_df.iterrows():
                        h = row["home_score"]
                        a = row["away_score"]
                        if h == a:
                            continue  # draw — no winner
                        if h > a:
                            winner, opponent = row["home_team"], row["away_team"]
                            winner_stat = row[home_col]
                            result_str = f"Won {int(h)}–{int(a)}"
                        else:
                            winner, opponent = row["away_team"], row["home_team"]
                            winner_stat = row[away_col]
                            result_str = f"Won {int(a)}–{int(h)}"
                        records.append({
                            "date": str(row["date"])[:10],
                            "winning_team": winner,
                            "opponent": opponent,
                            "result": result_str,
                            f"winner_{resolve_winner_stat}": round(float(winner_stat), 1),
                        })

                    if not records:
                        return "Based on all available data, no matches met this criterion."

                    resolved_df = pd.DataFrame(records)
                    result = f"# 📊 Match Results: Tournament Tactical Database\n\n"
                    result += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    result += "## Data:\n\n"
                    result += resolved_df.to_markdown(index=False)
                    result += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Resolved {len(resolved_df)} winning teams"
                    return result

                # ----------------------------------------------------------------
                # TEAM PERSPECTIVE
                # ----------------------------------------------------------------
                if team_perspective:
                    stat_cols = [c.strip() for c in columns.split(',')] if columns else []
                    for col in ["home_score", "away_score", "home_team", "away_team"]:
                        if col not in filtered_df.columns:
                            return f"❌ Column '{col}' not found in {table}."

                    records = []
                    for _, row in filtered_df.iterrows():
                        is_home = team_perspective.lower() in str(row["home_team"]).lower()
                        is_away = team_perspective.lower() in str(row["away_team"]).lower()
                        if not is_home and not is_away:
                            continue
                        h, a = row["home_score"], row["away_score"]
                        if is_home:
                            opponent = row["away_team"]
                            team_score, opp_score = int(h), int(a)
                            prefix = "home"
                        else:
                            opponent = row["home_team"]
                            team_score, opp_score = int(a), int(h)
                            prefix = "away"

                        if team_score > opp_score:
                            result_str = f"Won {team_score}–{opp_score}"
                        elif team_score == opp_score:
                            result_str = f"Draw {team_score}–{opp_score}"
                        else:
                            result_str = f"Lost {team_score}–{opp_score}"

                        record = {
                            "date": str(row["date"])[:10],
                            "team": str(row["home_team"] if is_home else row["away_team"]),
                            "opponent": str(opponent),
                            "result": result_str,
                        }
                        for stat in stat_cols:
                            col_name = f"{prefix}_{stat}"
                            if col_name in row.index and pd.notna(row[col_name]):
                                record[stat] = round(float(row[col_name]), 1) if isinstance(row[col_name], float) else row[col_name]
                        records.append(record)

                    if not records:
                        return f"Based on all available data, no matches found for {team_perspective}."

                    resolved_df = pd.DataFrame(records)
                    table_display_name = "Historical Match Database" if table == "results" else "Tournament Tactical Database"
                    result = f"# 📊 Match Results: {table_display_name}\n\n"
                    result += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    result += "## Data:\n\n"
                    result += resolved_df.to_markdown(index=False)
                    result += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Team perspective: {len(resolved_df)} matches for {team_perspective}"
                    return result

                # Build result
                table_display_name = "Historical Match Database" if table == "results" else "Tournament Tactical Database"
                result = f"# 📊 Match Results: {table_display_name}\n\n"
                
                result += f"**Rows Returned:** {len(filtered_df)}\n\n"
                
                # Add schema context (no internal file names exposed)
                if table in schema:
                    table_schema = schema[table]
                    coverage = table_schema.get('coverage', {})
                    result += f"**Coverage:** {coverage.get('time_range', 'N/A')}, "
                    result += f"{coverage.get('total_matches', 'N/A')} matches\n\n"
                
                # Select columns for display
                if columns:
                    # Custom columns specified
                    requested_cols = [col.strip() for col in columns.split(',')]
                    display_cols = [col for col in requested_cols if col in filtered_df.columns]
                    
                    if not display_cols:
                        return f"❌ None of the requested columns exist in {table}\n" \
                               f"Requested: {requested_cols}\n" \
                               f"Available: {list(filtered_df.columns)}"
                    
                    missing_cols = [col for col in requested_cols if col not in filtered_df.columns]
                    if missing_cols:
                        result += f"⚠️ **Warning:** Columns not found: {missing_cols}\n\n"
                else:
                    # Default columns based on table
                    if table == "results":
                        display_cols = ['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament']
                    else:  # tactical_data
                        display_cols = ['match_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score',
                                       'home_possession', 'away_possession', 'home_shots_total', 'away_shots_total',
                                       'home_shot_accuracy', 'away_shot_accuracy']
                    
                    # Filter to existing columns
                    display_cols = [col for col in display_cols if col in filtered_df.columns]
                
                display_df = filtered_df[display_cols]
                
                # Format dates
                if 'date' in display_df.columns:
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                
                # Convert to markdown table
                result += "## Data:\n\n"
                result += display_df.to_markdown(index=False)
                
                # Add summary statistics
                result += f"\n\n## Summary:\n"
                result += f"- Total Matches: {len(filtered_df)}\n"
                
                if team_filter:
                    # Calculate team stats
                    home_matches = filtered_df[filtered_df['home_team'].str.contains(team_filter, case=False, na=False)]
                    away_matches = filtered_df[filtered_df['away_team'].str.contains(team_filter, case=False, na=False)]
                    
                    home_wins = len(home_matches[home_matches['home_score'] > home_matches['away_score']])
                    away_wins = len(away_matches[away_matches['away_score'] > away_matches['home_score']])
                    total_wins = home_wins + away_wins
                    
                    result += f"- {team_filter} Wins: {total_wins}\n"
                    result += f"- {team_filter} Home Wins: {home_wins}\n"
                    result += f"- {team_filter} Away Wins: {away_wins}\n"
                
                self.log(f"Query successful: {len(filtered_df)} rows")
                self.status = f"Retrieved {len(filtered_df)} rows"
                
                return result
            
            except Exception as e:
                error_msg = f"Error querying CSV: {e}"
                self.log(error_msg)
                self.status = "Error"
                return f"❌ {error_msg}"
        
        return StructuredTool.from_function(
            func=query_csv,
            name="query_csv",
            description=(
                "Query CSV data with two modes: 'simple' (predefined filters) or 'custom' (pandas expressions). "
                "Tables: 'results' (all matches 1872-2026) or 'tactical_data' (WhoScored scraped matches with 41 metrics). "
                "\n\n"
                "SIMPLE MODE (query_mode='simple'): "
                "Use predefined filters: team_filter, date_from, date_to, tournament_filter, formation_filter, min_possession, max_possession. "
                "tournament_filter accepts both tournament names ('FIFA World Cup') and match_id prefixes ('WC_2026', 'EURO_2024'). "
                "\n\n"
                "CUSTOM MODE (query_mode='custom'): "
                "Use custom_filter for pandas boolean expressions (e.g., '(home_possession > 60) & (home_score > away_score)'). "
                "Supports: >, <, >=, <=, ==, !=, &, |, ~, .str.contains(). "
                "\n\n"
                "PERSPECTIVE PARAMETERS (optional, combine with any mode to eliminate home/away confusion): "
                "\n"
                "resolve_loser_stat='<stat>': returns one row per LOSING team with their correct stat. "
                "→ date | losing_team | opponent | result | loser_<stat>. "
                "Use for: 'teams that lost despite high X stat'. "
                "\n"
                "resolve_winner_stat='<stat>': returns one row per WINNING team with their correct stat. "
                "→ date | winning_team | opponent | result | winner_<stat>. "
                "Use for: 'teams that won with low possession', 'winners with fewest shots'. "
                "\n"
                "team_perspective='<TeamName>': returns one row per match from that team's point of view. "
                "→ date | team | opponent | result | <stat1> | <stat2> | ... "
                "Requires columns='stat1,stat2,...' listing base stat names (WITHOUT home_/away_ prefix). "
                "Use for: 'Brazil stats per match', 'Spain possession in each game', 'France WC 2026 performance'. "
                "\n\n"
                "All three perspective params use base stat names WITHOUT home_/away_ prefix "
                "(e.g. 'pass_accuracy', 'possession', 'shots_total', 'tackles_won')."
            )
        )

# Made with Bob