"""
Get Tactical Data Tool for LangFlow
Provides tactical statistics from tactical_data.csv - Returns JSON for LLM analysis
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
    description: str = "Get detailed tactical statistics from WhoScored data"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "activity"
    name: str = "get_tactical_data_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.tactical_csv_path = self.project_root / "data" / "match_data" / "tactical_data.csv"
    
    def build_tool(self) -> Tool:
        """Build the tactical data tool"""
        
        def get_tactical_data(team_name: str, tournament_prefix: str = None) -> str:
            """Get detailed tactical statistics for a team from tactical_data.csv.
            
            Args:
                team_name: Team name (e.g., "Argentina", "Brazil", "Iran")
                tournament_prefix: Tournament filter (e.g., "WC_2026", "EURO_2024")
                
            Returns:
                Detailed tactical statistics including formations, possession, shots, passes, 
                defensive metrics, and calculated intensity metrics in JSON format
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
                    return f"❌ No tactical data found for {team_name}.\n\n" \
                           f"**Note:** Tactical data is only available for matches that have been scraped from WhoScored."
                
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
                
                # Calculate averages for all metrics
                def safe_avg(values):
                    """Calculate average, handling empty lists"""
                    return round(sum(values) / len(values), 1) if values else 0
                
                # Collect values from home and away matches
                poss_values = []
                shots_total_values = []
                shots_on_target_values = []
                shot_accuracy_values = []
                passes_total_values = []
                pass_accuracy_values = []
                key_passes_values = []
                tackles_won_values = []
                tackle_success_values = []
                interceptions_values = []
                clearances_values = []
                aerials_won_values = []
                attacking_intensity_values = []
                defensive_intensity_values = []
                avg_age_values = []
                
                for _, match in home_matches.iterrows():
                    if pd.notna(match['home_possession']):
                        poss_values.append(match['home_possession'])
                    if pd.notna(match['home_shots_total']):
                        shots_total_values.append(match['home_shots_total'])
                    if pd.notna(match['home_shots_on_target']):
                        shots_on_target_values.append(match['home_shots_on_target'])
                    if pd.notna(match['home_shot_accuracy']):
                        shot_accuracy_values.append(match['home_shot_accuracy'])
                    if pd.notna(match['home_passes_total']):
                        passes_total_values.append(match['home_passes_total'])
                    if pd.notna(match['home_pass_accuracy']):
                        pass_accuracy_values.append(match['home_pass_accuracy'])
                    if pd.notna(match['home_key_passes']):
                        key_passes_values.append(match['home_key_passes'])
                    if pd.notna(match['home_tackles_won']):
                        tackles_won_values.append(match['home_tackles_won'])
                    if pd.notna(match['home_tackle_success']):
                        tackle_success_values.append(match['home_tackle_success'])
                    if pd.notna(match['home_interceptions']):
                        interceptions_values.append(match['home_interceptions'])
                    if pd.notna(match['home_clearances']):
                        clearances_values.append(match['home_clearances'])
                    if pd.notna(match['home_aerials_won']):
                        aerials_won_values.append(match['home_aerials_won'])
                    if pd.notna(match['home_attacking_intensity']):
                        attacking_intensity_values.append(match['home_attacking_intensity'])
                    if pd.notna(match['home_defensive_intensity']):
                        defensive_intensity_values.append(match['home_defensive_intensity'])
                    if pd.notna(match['home_avg_age']):
                        avg_age_values.append(match['home_avg_age'])
                
                for _, match in away_matches.iterrows():
                    if pd.notna(match['away_possession']):
                        poss_values.append(match['away_possession'])
                    if pd.notna(match['away_shots_total']):
                        shots_total_values.append(match['away_shots_total'])
                    if pd.notna(match['away_shots_on_target']):
                        shots_on_target_values.append(match['away_shots_on_target'])
                    if pd.notna(match['away_shot_accuracy']):
                        shot_accuracy_values.append(match['away_shot_accuracy'])
                    if pd.notna(match['away_passes_total']):
                        passes_total_values.append(match['away_passes_total'])
                    if pd.notna(match['away_pass_accuracy']):
                        pass_accuracy_values.append(match['away_pass_accuracy'])
                    if pd.notna(match['away_key_passes']):
                        key_passes_values.append(match['away_key_passes'])
                    if pd.notna(match['away_tackles_won']):
                        tackles_won_values.append(match['away_tackles_won'])
                    if pd.notna(match['away_tackle_success']):
                        tackle_success_values.append(match['away_tackle_success'])
                    if pd.notna(match['away_interceptions']):
                        interceptions_values.append(match['away_interceptions'])
                    if pd.notna(match['away_clearances']):
                        clearances_values.append(match['away_clearances'])
                    if pd.notna(match['away_aerials_won']):
                        aerials_won_values.append(match['away_aerials_won'])
                    if pd.notna(match['away_attacking_intensity']):
                        attacking_intensity_values.append(match['away_attacking_intensity'])
                    if pd.notna(match['away_defensive_intensity']):
                        defensive_intensity_values.append(match['away_defensive_intensity'])
                    if pd.notna(match['away_avg_age']):
                        avg_age_values.append(match['away_avg_age'])
                
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
                tournaments = team_matches['tournament'].unique().tolist()
                
                # Build recent matches list with detailed stats
                recent_matches = []
                for _, match in team_matches.head(5).iterrows():
                    is_home = team_name.lower() in str(match['home_team']).lower()
                    recent_matches.append({
                        "match_id": str(match['match_id']),
                        "date": match['date'].strftime('%Y-%m-%d') if pd.notna(match['date']) else None,
                        "opponent": str(match['away_team'] if is_home else match['home_team']),
                        "score": f"{int(match['home_score'])}-{int(match['away_score'])}" if pd.notna(match['home_score']) else None,
                        "result": "W" if (is_home and match['home_score'] > match['away_score']) or (not is_home and match['away_score'] > match['home_score']) else ("D" if match['home_score'] == match['away_score'] else "L"),
                        "formation": str(match['home_formation'] if is_home else match['away_formation']),
                        "possession": round(float(match['home_possession'] if is_home else match['away_possession']), 1),
                        "shots": int(match['home_shots_total'] if is_home else match['away_shots_total']),
                        "shots_on_target": int(match['home_shots_on_target'] if is_home else match['away_shots_on_target']),
                        "shot_accuracy": round(float(match['home_shot_accuracy'] if is_home else match['away_shot_accuracy']), 1),
                        "passes": int(match['home_passes_total'] if is_home else match['away_passes_total']),
                        "pass_accuracy": round(float(match['home_pass_accuracy'] if is_home else match['away_pass_accuracy']), 1),
                        "attacking_intensity": int(match['home_attacking_intensity'] if is_home else match['away_attacking_intensity']),
                        "defensive_intensity": int(match['home_defensive_intensity'] if is_home else match['away_defensive_intensity'])
                    })
                
                # Build JSON output
                result = {
                    "team_name": team_name,
                    "coverage": {
                        "tournaments": tournaments,
                        "total_matches": int(total_matches),
                        "home_matches": len(home_matches),
                        "away_matches": len(away_matches)
                    },
                    "team_profile": {
                        "average_age": safe_avg(avg_age_values),
                        "most_used_formation": most_used_formation
                    },
                    "aggregate_statistics": {
                        "possession": {
                            "average_percent": safe_avg(poss_values),
                            "interpretation": "High possession (>60%) indicates control, low (<40%) suggests counter-attacking style"
                        },
                        "attacking": {
                            "avg_shots_per_match": safe_avg(shots_total_values),
                            "avg_shots_on_target": safe_avg(shots_on_target_values),
                            "avg_shot_accuracy_percent": safe_avg(shot_accuracy_values),
                            "avg_key_passes": safe_avg(key_passes_values),
                            "avg_attacking_intensity": safe_avg(attacking_intensity_values),
                            "interpretation": "Attacking intensity = shots + key passes. Higher values (>30) indicate aggressive attacking"
                        },
                        "passing": {
                            "avg_passes_per_match": safe_avg(passes_total_values),
                            "avg_pass_accuracy_percent": safe_avg(pass_accuracy_values),
                            "interpretation": "Pass accuracy >85% indicates possession-based style, <75% suggests direct play"
                        },
                        "defending": {
                            "avg_tackles_won": safe_avg(tackles_won_values),
                            "avg_tackle_success_percent": safe_avg(tackle_success_values),
                            "avg_interceptions": safe_avg(interceptions_values),
                            "avg_clearances": safe_avg(clearances_values),
                            "avg_defensive_intensity": safe_avg(defensive_intensity_values),
                            "interpretation": "Defensive intensity = tackles + interceptions + clearances. Higher values (>50) indicate heavy defensive work"
                        },
                        "aerial": {
                            "avg_aerials_won": safe_avg(aerials_won_values),
                            "interpretation": "Aerial dominance important for set pieces and long-ball strategy"
                        }
                    },
                    "recent_matches": recent_matches,
                    "data_source": {
                        "type": "Tournament Tactical Database",
                        "total_columns": 41,
                        "includes_calculated_metrics": True
                    }
                }
                
                self.log(f"Successfully retrieved tactical data for {team_name}")
                self.status = f"Tactical data for {team_name}: {total_matches} matches"
                
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
                "Get comprehensive tactical statistics in JSON format for a team from tactical_data.csv. "
                "Returns 41 metrics including: formations, possession, shots (total/on-target/accuracy), "
                "passes (total/accuracy/key passes), defensive stats (tackles/interceptions/clearances), "
                "aerials, and calculated intensity metrics (attacking_intensity, defensive_intensity). "
                "Data from WhoScored scraper. Optional tournament_prefix parameter to filter specific tournament. "
                "Use when you need detailed tactical analysis with all available metrics."
            )
        )

# Made with Bob