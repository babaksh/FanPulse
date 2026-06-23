"""
Compare Teams Tool for LangFlow
Provides head-to-head comparison between two teams - Returns JSON for LLM analysis
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


class CompareTeamsTool(Component):
    display_name: str = "Compare Teams"
    description: str = "Compare two teams head-to-head"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "git-compare"
    name: str = "compare_teams_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.results_csv = self.project_root / "data" / "match_data" / "results.csv"
    
    def build_tool(self) -> Tool:
        """Build the team comparison tool"""
        
        def compare_teams(team1: str, team2: str) -> str:
            """Compare two teams head-to-head.
            
            Args:
                team1: First team name (e.g., "Argentina")
                team2: Second team name (e.g., "Brazil")
                
            Returns:
                Head-to-head comparison from results.csv (1872-2026)
            """
            try:
                self.log(f"Comparing teams: {team1} vs {team2}")
                self.status = f"Comparing {team1} vs {team2}..."
                
                # Read CSV
                df = pd.read_csv(self.results_csv)
                df['date'] = pd.to_datetime(df['date'])
                
                # Get head-to-head matches
                h2h_matches = df[
                    ((df['home_team'].str.contains(team1, case=False, na=False)) &
                     (df['away_team'].str.contains(team2, case=False, na=False))) |
                    ((df['home_team'].str.contains(team2, case=False, na=False)) &
                     (df['away_team'].str.contains(team1, case=False, na=False)))
                ].copy()
                
                h2h_matches = h2h_matches.dropna(subset=['home_score', 'away_score'])
                h2h_matches = h2h_matches.sort_values('date', ascending=False)
                
                # Get individual team stats
                team1_matches = df[
                    (df['home_team'].str.contains(team1, case=False, na=False)) |
                    (df['away_team'].str.contains(team1, case=False, na=False))
                ].dropna(subset=['home_score', 'away_score'])
                
                team2_matches = df[
                    (df['home_team'].str.contains(team2, case=False, na=False)) |
                    (df['away_team'].str.contains(team2, case=False, na=False))
                ].dropna(subset=['home_score', 'away_score'])
                
                # Calculate team1 stats
                team1_wins = 0
                team1_goals = 0
                team1_conceded = 0
                for _, match in team1_matches.iterrows():
                    is_home = team1.lower() in str(match['home_team']).lower()
                    home_score = int(match['home_score'])
                    away_score = int(match['away_score'])
                    
                    if is_home:
                        team1_goals += home_score
                        team1_conceded += away_score
                        if home_score > away_score:
                            team1_wins += 1
                    else:
                        team1_goals += away_score
                        team1_conceded += home_score
                        if away_score > home_score:
                            team1_wins += 1
                
                team1_win_rate = (team1_wins / len(team1_matches) * 100) if len(team1_matches) > 0 else 0
                team1_gd = team1_goals - team1_conceded
                
                # Calculate team2 stats
                team2_wins = 0
                team2_goals = 0
                team2_conceded = 0
                for _, match in team2_matches.iterrows():
                    is_home = team2.lower() in str(match['home_team']).lower()
                    home_score = int(match['home_score'])
                    away_score = int(match['away_score'])
                    
                    if is_home:
                        team2_goals += home_score
                        team2_conceded += away_score
                        if home_score > away_score:
                            team2_wins += 1
                    else:
                        team2_goals += away_score
                        team2_conceded += home_score
                        if away_score > home_score:
                            team2_wins += 1
                
                team2_win_rate = (team2_wins / len(team2_matches) * 100) if len(team2_matches) > 0 else 0
                team2_gd = team2_goals - team2_conceded
                
                # Build JSON output
                result = {
                    "team1": team1,
                    "team2": team2,
                    "head_to_head": {},
                    "overall_statistics": {
                        team1: {
                            "total_matches": int(len(team1_matches)),
                            "win_rate": round(float(team1_win_rate), 1),
                            "goals_scored": int(team1_goals),
                            "goals_conceded": int(team1_conceded),
                            "goal_difference": int(team1_gd)
                        },
                        team2: {
                            "total_matches": int(len(team2_matches)),
                            "win_rate": round(float(team2_win_rate), 1),
                            "goals_scored": int(team2_goals),
                            "goals_conceded": int(team2_conceded),
                            "goal_difference": int(team2_gd)
                        }
                    },
                    "data_source": "Historical Match Database (1872-2026, ~49,000 matches)"
                }
                
                # Add head-to-head data if available
                if not h2h_matches.empty:
                    team1_h2h_wins = 0
                    team2_h2h_wins = 0
                    draws = 0
                    
                    for _, match in h2h_matches.iterrows():
                        team1_is_home = team1.lower() in str(match['home_team']).lower()
                        home_score = int(match['home_score'])
                        away_score = int(match['away_score'])
                        
                        if team1_is_home:
                            if home_score > away_score:
                                team1_h2h_wins += 1
                            elif home_score < away_score:
                                team2_h2h_wins += 1
                            else:
                                draws += 1
                        else:
                            if away_score > home_score:
                                team1_h2h_wins += 1
                            elif away_score < home_score:
                                team2_h2h_wins += 1
                            else:
                                draws += 1
                    
                    recent_meetings = []
                    for _, match in h2h_matches.head(5).iterrows():
                        recent_meetings.append({
                            "date": match['date'].strftime('%Y-%m-%d') if pd.notna(match['date']) else None,
                            "home_team": str(match['home_team']),
                            "away_team": str(match['away_team']),
                            "score": f"{int(match['home_score'])}-{int(match['away_score'])}",
                            "tournament": str(match.get('tournament', 'N/A'))
                        })
                    
                    result["head_to_head"] = {
                        "total_meetings": int(len(h2h_matches)),
                        f"{team1}_wins": int(team1_h2h_wins),
                        f"{team2}_wins": int(team2_h2h_wins),
                        "draws": int(draws),
                        "recent_meetings": recent_meetings
                    }
                else:
                    result["head_to_head"] = {
                        "total_meetings": 0,
                        "note": f"{team1} and {team2} have not faced each other in recorded history"
                    }
                
                self.log(f"Successfully compared {team1} vs {team2}")
                self.status = f"Compared {team1} vs {team2}"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                error_msg = f"Error in compare_teams tool: {e}"
                self.log(error_msg)
                self.status = "Error"
                return error_msg
        
        return StructuredTool.from_function(
            func=compare_teams,
            name="compare_teams",
            description=(
                "Compare two teams head-to-head in JSON format. Returns head-to-head record (wins, draws, recent meetings), "
                "overall statistics for both teams (matches, win rate, goals, goal difference), and comparison data. "
                "Data from results.csv (1872-2026). Use when you need to compare two teams for analysis."
                "Uses results.csv (1872-2026) for historical data."
            )
        )

# Made with Bob