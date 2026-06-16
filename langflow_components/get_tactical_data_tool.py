"""
Get Tactical Data Tool for LangFlow
Provides tactical statistics from major tournaments - Returns JSON for LLM analysis
"""

from lfx.custom import Component
from lfx.io import Output
from lfx.field_typing import Tool
from langchain_core.tools import StructuredTool
from pathlib import Path
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)


class GetTacticalDataTool(Component):
    display_name: str = "Get Tactical Data"
    description: str = "Get tactical statistics from major tournaments"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "activity"
    name: str = "get_tactical_data_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.tactical_csv_path = self.project_root / "data" / "match_data" / "tactical_stats.csv"
    
    def build_tool(self) -> Tool:
        """Build the tactical data tool"""
        
        def get_tactical_data(team_name: str, tournament_prefix: str = None) -> str:
            """Get tactical statistics for a team from major tournaments.
            
            Args:
                team_name: Team name (e.g., "Argentina", "Brazil")
                tournament_prefix: Tournament filter (e.g., "WC2022", "WC2026")
                
            Returns:
                Tactical statistics from tactical_stats.csv (tournament matches with prefix)
            """
            try:
                self.log(f"Getting tactical data for: {team_name}")
                self.status = f"Fetching tactical data for {team_name}..."
                
                # Check if tactical data file exists
                if not self.tactical_csv_path.exists():
                    return f"❌ Tactical data file not found at: {self.tactical_csv_path}"
                
                # Read tactical CSV
                df = pd.read_csv(self.tactical_csv_path)
                df['date'] = pd.to_datetime(df['date'])
                
                # Get team matches
                team_matches = df[
                    (df['home_team'].str.contains(team_name, case=False, na=False)) |
                    (df['away_team'].str.contains(team_name, case=False, na=False))
                ].copy()
                
                if team_matches.empty:
                    return f"❌ No tactical data found for {team_name} in major tournaments.\n\n" \
                           f"**Note:** Tactical data is only available for matches with recognized tournament prefixes."
                
                # Filter by tournament prefix if provided
                if tournament_prefix:
                    team_matches = team_matches[
                        team_matches['match_id'].str.startswith(tournament_prefix, na=False)
                    ]
                    
                    if team_matches.empty:
                        return f"❌ No tactical data found for {team_name} in tournament: {tournament_prefix}"
                
                # Sort by date
                team_matches = team_matches.sort_values('date', ascending=False)
                
                # Calculate aggregate statistics
                total_matches = len(team_matches)
                
                # Separate home and away matches for accurate stats
                home_matches = team_matches[team_matches['home_team'].str.contains(team_name, case=False, na=False)]
                away_matches = team_matches[team_matches['away_team'].str.contains(team_name, case=False, na=False)]
                
                # Calculate averages (handle NaN values)
                # When team plays home, use home_* columns; when away, use away_* columns
                poss_values = []
                xg_values = []
                shots_values = []
                sot_values = []
                
                for _, match in home_matches.iterrows():
                    if pd.notna(match['home_possession']):
                        poss_values.append(match['home_possession'])
                    if pd.notna(match['home_xg']):
                        xg_values.append(match['home_xg'])
                    if pd.notna(match['home_shots']):
                        shots_values.append(match['home_shots'])
                    if pd.notna(match['home_shots_on_target']):
                        sot_values.append(match['home_shots_on_target'])
                
                for _, match in away_matches.iterrows():
                    if pd.notna(match['away_possession']):
                        poss_values.append(match['away_possession'])
                    if pd.notna(match['away_xg']):
                        xg_values.append(match['away_xg'])
                    if pd.notna(match['away_shots']):
                        shots_values.append(match['away_shots'])
                    if pd.notna(match['away_shots_on_target']):
                        sot_values.append(match['away_shots_on_target'])
                
                avg_possession = sum(poss_values) / len(poss_values) if poss_values else 0
                avg_xg = sum(xg_values) / len(xg_values) if xg_values else 0
                avg_shots = sum(shots_values) / len(shots_values) if shots_values else 0
                avg_shots_on_target = sum(sot_values) / len(sot_values) if sot_values else 0
                
                # Get most used formation
                formations = []
                for _, match in home_matches.iterrows():
                    if pd.notna(match.get('home_formation')):
                        formations.append(match['home_formation'])
                for _, match in away_matches.iterrows():
                    if pd.notna(match.get('away_formation')):
                        formations.append(match['away_formation'])
                
                most_used_formation = max(set(formations), key=formations.count) if formations else "N/A"
                
                # Identify tournaments
                tournaments = team_matches['match_id'].str.extract(r'^([A-Z0-9]+)_')[0].unique()
                tournament_names = []
                for t in tournaments:
                    if t == 'WC2022':
                        tournament_names.append('World Cup 2022')
                    elif t == 'WC2026':
                        tournament_names.append('World Cup 2026')
                    else:
                        tournament_names.append(t)
                
                # Build recent matches list
                recent_matches = []
                for _, match in team_matches.head(5).iterrows():
                    is_home = team_name.lower() in str(match['home_team']).lower()
                    recent_matches.append({
                        "date": match['date'].strftime('%Y-%m-%d') if pd.notna(match['date']) else None,
                        "home_team": str(match['home_team']),
                        "away_team": str(match['away_team']),
                        "score": f"{int(match['home_score'])}-{int(match['away_score'])}" if pd.notna(match['home_score']) else None,
                        "team_possession": round(float(match['home_possession'] if is_home else match['away_possession']), 1),
                        "team_xg": round(float(match['home_xg'] if is_home else match['away_xg']), 2) if pd.notna(match['home_xg'] if is_home else match['away_xg']) else None
                    })
                
                # Build JSON output
                result = {
                    "team_name": team_name,
                    "tournament_coverage": {
                        "tournaments": tournament_names,
                        "total_matches": int(total_matches)
                    },
                    "aggregate_statistics": {
                        "possession": {
                            "average": round(float(avg_possession), 1),
                            "most_used_formation": most_used_formation
                        },
                        "attacking": {
                            "avg_xg": round(float(avg_xg), 2) if avg_xg > 0 else None,
                            "avg_shots": round(float(avg_shots), 1),
                            "avg_shots_on_target": round(float(avg_shots_on_target), 1),
                            "shot_accuracy_percent": round(float((avg_shots_on_target/avg_shots*100) if avg_shots > 0 else 0), 1)
                        }
                    },
                    "recent_matches": recent_matches,
                    "data_source": {
                        "file": "tactical_stats.csv",
                        "type": "major tournaments",
                        "tournaments_covered": tournament_names
                    }
                }
                
                self.log(f"Successfully retrieved tactical data for {team_name}")
                self.status = f"Tactical data for {team_name}"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                error_msg = f"Error in get_tactical_data tool: {e}"
                self.log(error_msg)
                self.status = "Error"
                return error_msg
        
        return StructuredTool.from_function(
            func=get_tactical_data,
            name="get_tactical_data",
            description=(
                "Get tactical statistics in JSON format for a team from major tournaments. Returns possession, xG, shots, "
                "formations, shot accuracy, and recent match details. Data from tactical_stats.csv for tournaments with "
                "prefix (WC2022, WC2026, EURO2024, etc.). Optional tournament_prefix parameter to filter specific tournament. "
                "Use when you need detailed tactical metrics for analysis."
            )
        )

# Made with Bob