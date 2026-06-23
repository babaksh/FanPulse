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
            columns: Optional[str] = None,
            limit: int = 50
        ) -> str:
            """Query CSV data with filters - supports both simple and custom query modes.
            
            IMPORTANT: This tool reads data/match_data/data_schema.json to understand data structure.
            Use read_schema tool FIRST to see available columns before making custom queries.
            
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
                columns: Comma-separated column names to display (e.g., "date,home_team,away_team,home_score")
                    - If not provided, shows default columns based on table
                
                COMMON PARAMETERS:
                limit: Maximum rows to return (default: 50, max: 200)
                
            Returns:
                Query results in markdown table format with schema context
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
                        is_match_id_prefix = '_' in tournament_filter and any(char.isdigit() for char in tournament_filter)
                        
                        if is_match_id_prefix and 'match_id' in filtered_df.columns:
                            filtered_df = filtered_df[
                                filtered_df['match_id'].str.contains(tournament_filter, case=False, na=False)
                            ]
                        elif 'tournament' in filtered_df.columns:
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
                
                # Build result
                table_display_name = "Historical Match Database" if table == "results" else "Tournament Tactical Database"
                result = f"# 📊 Query Results: {table_display_name}\n\n"
                result += f"**Query Mode:** {query_mode}\n"
                
                if query_mode == "custom":
                    result += f"**Custom Filter:** `{custom_filter}`\n"
                else:
                    result += f"**Filters Applied:**\n"
                    result += f"- Team: {team_filter or 'Any'}\n"
                    result += f"- Date Range: {date_from or 'Any'} to {date_to or 'Any'}\n"
                    result += f"- Tournament: {tournament_filter or 'Any'}\n"
                
                result += f"**Rows Returned:** {len(filtered_df)}\n\n"
                
                # Add schema context
                if table in schema:
                    table_schema = schema[table]
                    result += f"**Data Source:** {table_schema.get('table_role', 'N/A')}\n"
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
                "IMPORTANT: Use read_schema tool FIRST to see available columns before custom queries. "
                "Tables: 'results' (all matches 1872-2026) or 'tactical_data' (WhoScored scraped matches with 41 metrics). "
                "\n\n"
                "SIMPLE MODE (query_mode='simple'): "
                "Use predefined filters: team_filter, date_from, date_to, tournament_filter, formation_filter, min_possession, max_possession. "
                "tournament_filter accepts both tournament names ('FIFA World Cup') and match_id prefixes ('WC_2026', 'EURO_2024'). "
                "\n\n"
                "CUSTOM MODE (query_mode='custom'): "
                "Use custom_filter for pandas boolean expressions (e.g., '(home_possession > 60) & (home_score > away_score)'). "
                "Supports: >, <, >=, <=, ==, !=, &, |, ~, .str.contains(). "
                "Use 'columns' parameter to specify which columns to display (comma-separated). "
                "\n\n"
                "Examples: "
                "Simple: query_mode='simple', team_filter='Brazil', date_from='2026-06-01' | "
                "Custom: query_mode='custom', custom_filter='(home_shots_total > 15) & (away_shots_total > 15)', columns='date,home_team,away_team,home_shots_total,away_shots_total'"
            )
        )

# Made with Bob