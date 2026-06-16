"""
Get Team Stats Tool for LangFlow
Provides quick statistical data for teams - Returns JSON for LLM analysis
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


class GetTeamStatsTool(Component):
    display_name: str = "Get Team Stats"
    description: str = "Get quick statistical data for a team"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "trending-up"
    name: str = "get_team_stats_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.csv_path = self.project_root / "data" / "match_data" / "results.csv"
    
    def build_tool(self) -> Tool:
        """Build the team stats tool"""
        
        def get_team_stats(team_name: str) -> str:
            """Get quick statistical overview for a team.
            
            Args:
                team_name: Team name (e.g., "Argentina", "Brazil")
                
            Returns:
                Statistical summary from results.csv (1872-2026)
            """
            try:
                self.log(f"Getting stats for team: {team_name}")
                self.status = f"Fetching stats for {team_name}..."
                
                # Read CSV
                df = pd.read_csv(self.csv_path)
                df['date'] = pd.to_datetime(df['date'])
                
                # Get team matches
                team_matches = df[
                    (df['home_team'].str.contains(team_name, case=False, na=False)) |
                    (df['away_team'].str.contains(team_name, case=False, na=False))
                ].copy()
                
                # Filter out matches with NA scores
                team_matches = team_matches.dropna(subset=['home_score', 'away_score'])
                
                if team_matches.empty:
                    return f"❌ No data found for team: {team_name}"
                
                # Sort by date (most recent first)
                team_matches = team_matches.sort_values('date', ascending=False)
                
                # Calculate statistics
                total_matches = len(team_matches)
                wins = 0
                draws = 0
                losses = 0
                goals_scored = 0
                goals_conceded = 0
                
                for _, match in team_matches.iterrows():
                    is_home = team_name.lower() in str(match['home_team']).lower()
                    home_score = int(match['home_score'])
                    away_score = int(match['away_score'])
                    
                    if is_home:
                        goals_scored += home_score
                        goals_conceded += away_score
                        if home_score > away_score:
                            wins += 1
                        elif home_score == away_score:
                            draws += 1
                        else:
                            losses += 1
                    else:
                        goals_scored += away_score
                        goals_conceded += home_score
                        if away_score > home_score:
                            wins += 1
                        elif away_score == home_score:
                            draws += 1
                        else:
                            losses += 1
                
                # Calculate derived stats
                win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
                avg_goals_scored = goals_scored / total_matches if total_matches > 0 else 0
                avg_goals_conceded = goals_conceded / total_matches if total_matches > 0 else 0
                goal_difference = goals_scored - goals_conceded
                
                # Calculate recent form (last 5 matches)
                form_string = []
                for _, match in team_matches.head(5).iterrows():
                    is_home = team_name.lower() in str(match['home_team']).lower()
                    home_score = int(match['home_score'])
                    away_score = int(match['away_score'])
                    
                    if is_home:
                        if home_score > away_score:
                            form_string.append('W')
                        elif home_score == away_score:
                            form_string.append('D')
                        else:
                            form_string.append('L')
                    else:
                        if away_score > home_score:
                            form_string.append('W')
                        elif away_score == home_score:
                            form_string.append('D')
                        else:
                            form_string.append('L')
                
                form_score = (form_string.count('W') * 3 + form_string.count('D')) / 15 * 100
                
                # Build last 5 results
                last_5_results = []
                for i, (_, match) in enumerate(team_matches.head(5).iterrows()):
                    last_5_results.append({
                        "date": match['date'].strftime('%Y-%m-%d'),
                        "home_team": str(match['home_team']),
                        "away_team": str(match['away_team']),
                        "score": f"{int(match['home_score'])}-{int(match['away_score'])}",
                        "result": form_string[i]
                    })
                
                # Build JSON output
                result = {
                    "team_name": team_name,
                    "overall_record": {
                        "total_matches": int(total_matches),
                        "wins": int(wins),
                        "draws": int(draws),
                        "losses": int(losses),
                        "win_rate": round(float(win_rate), 1),
                        "draw_rate": round(float(draws/total_matches*100), 1),
                        "loss_rate": round(float(losses/total_matches*100), 1)
                    },
                    "goals": {
                        "scored": int(goals_scored),
                        "conceded": int(goals_conceded),
                        "goal_difference": int(goal_difference),
                        "avg_scored_per_match": round(float(avg_goals_scored), 2),
                        "avg_conceded_per_match": round(float(avg_goals_conceded), 2)
                    },
                    "recent_form": {
                        "last_5_matches": '-'.join(form_string),
                        "form_score": round(float(form_score), 0),
                        "results": last_5_results
                    },
                    "data_source": "results.csv (1872-2026, ~49,000 matches)"
                }
                
                self.log(f"Successfully retrieved stats for {team_name}")
                self.status = f"Stats for {team_name}"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                error_msg = f"Error in get_team_stats tool: {e}"
                self.log(error_msg)
                self.status = "Error"
                return error_msg
        
        return StructuredTool.from_function(
            func=get_team_stats,
            name="get_team_stats",
            description=(
                "Get quick statistical overview in JSON format for a team. Returns overall record (matches, wins, draws, losses, rates), "
                "goals (scored, conceded, averages), and recent form (last 5 matches with results). Data from results.csv (1872-2026). "
                "Use when you need basic statistics without tactical details. For tactical data, use analyze_team or get_tactical_data instead."
            )
        )

# Made with Bob
