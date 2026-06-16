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
        self.schema_path = self.project_root / "data" / "data_schema.json"
        self.results_csv = self.project_root / "data" / "match_data" / "results.csv"
        self.tactical_csv = self.project_root / "data" / "match_data" / "tactical_stats.csv"
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
            team_filter: Optional[str] = None,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None,
            tournament_filter: Optional[str] = None,
            limit: int = 50
        ) -> str:
            """Query CSV data with filters.
            
            IMPORTANT: This tool reads data/data_schema.json to understand data structure.
            
            Args:
                table: Table name - "results" or "tactical_stats"
                team_filter: Team name to filter (searches both home and away)
                date_from: Start date (YYYY-MM-DD format)
                date_to: End date (YYYY-MM-DD format)
                tournament_filter: Tournament name filter
                limit: Maximum rows to return (default: 50, max: 200)
                
            Returns:
                Query results in markdown table format with schema context
            """
            try:
                self.log(f"Querying {table} with filters")
                self.status = f"Querying {table}..."
                
                # Load schema
                schema = self._load_schema()
                
                # Validate table
                if table not in ["results", "tactical_stats"]:
                    return f"❌ Invalid table: {table}. Must be 'results' or 'tactical_stats'"
                
                # Select CSV file
                csv_path = self.results_csv if table == "results" else self.tactical_csv
                
                if not csv_path.exists():
                    return f"❌ CSV file not found: {csv_path}"
                
                # Read CSV
                df = pd.read_csv(csv_path)
                df['date'] = pd.to_datetime(df['date'])
                
                # Apply filters
                filtered_df = df.copy()
                
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
                
                # Tournament filter
                if tournament_filter and 'tournament' in filtered_df.columns:
                    filtered_df = filtered_df[
                        filtered_df['tournament'].str.contains(tournament_filter, case=False, na=False)
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
                result = f"# 📊 Query Results: {table}.csv\n\n"
                result += f"**Filters Applied:**\n"
                result += f"- Team: {team_filter or 'Any'}\n"
                result += f"- Date Range: {date_from or 'Any'} to {date_to or 'Any'}\n"
                result += f"- Tournament: {tournament_filter or 'Any'}\n"
                result += f"- Rows Returned: {len(filtered_df)}\n\n"
                
                # Add schema context
                if table in schema:
                    table_schema = schema[table]
                    result += f"**Data Source:** {table_schema.get('table_role', 'N/A')}\n"
                    coverage = table_schema.get('coverage', {})
                    result += f"**Coverage:** {coverage.get('time_range', 'N/A')}, "
                    result += f"{coverage.get('total_matches', 'N/A')} matches\n\n"
                
                # Select key columns for display
                if table == "results":
                    display_cols = ['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament']
                else:  # tactical_stats
                    display_cols = ['match_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 
                                   'home_possession', 'away_possession', 'home_xg', 'away_xg']
                
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
                "Query CSV data with filters. "
                "Use this tool for custom queries outside the 4 specialized tools. "
                "Reads data/data_schema.json for schema awareness. "
                "Tables: 'results' (all matches 1872-2026) or 'tactical_stats' (tournament prefix system). "
                "Supports team, date, and tournament filtering."
            )
        )

# Made with Bob