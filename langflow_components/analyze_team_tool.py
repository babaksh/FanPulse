"""
Analyze Team Tool for LangFlow
Provides comprehensive team analysis - Returns JSON for LLM analysis
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


class AnalyzeTeamTool(Component):
    display_name: str = "Analyze Team"
    description: str = "Get comprehensive analysis of a team's performance"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "ChartColumn"
    name: str = "analyze_team_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.results_csv = self.project_root / "data" / "match_data" / "results.csv"
        self.tactical_csv = self.project_root / "data" / "match_data" / "tactical_stats.csv"
    
    def build_tool(self) -> Tool:
        """Build the team analysis tool"""
        
        def analyze_team(team_name: str) -> str:
            """Get comprehensive analysis of a team's performance.
            
            Args:
                team_name: Team name (e.g., "Argentina", "Brazil")
                
            Returns:
                Analysis from results.csv (1872-2026) and tactical_stats.csv (tournament matches with prefix)
            """
            try:
                self.log(f"Analyzing team: {team_name}")
                self.status = f"Analyzing {team_name}..."
                
                # Read results CSV
                results_df = pd.read_csv(self.results_csv)
                results_df['date'] = pd.to_datetime(results_df['date'])
                
                # Get team matches from results
                team_matches = results_df[
                    (results_df['home_team'].str.contains(team_name, case=False, na=False)) |
                    (results_df['away_team'].str.contains(team_name, case=False, na=False))
                ].copy()
                
                team_matches = team_matches.dropna(subset=['home_score', 'away_score'])
                
                if team_matches.empty:
                    return f"❌ No data found for team: {team_name}"
                
                team_matches = team_matches.sort_values('date', ascending=False)
                
                # Calculate overall statistics
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
                
                win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
                avg_goals_scored = goals_scored / total_matches if total_matches > 0 else 0
                avg_goals_conceded = goals_conceded / total_matches if total_matches > 0 else 0
                goal_difference = goals_scored - goals_conceded
                
                # Calculate recent form (last 10 matches)
                form_string = []
                for _, match in team_matches.head(10).iterrows():
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
                
                form_score = (form_string.count('W') * 3 + form_string.count('D')) / 30 * 100
                
                # Try to load tactical data
                wc2022_data = None
                wc2026_data = None
                
                if self.tactical_csv.exists():
                    tactical_df = pd.read_csv(self.tactical_csv)
                    tactical_df['date'] = pd.to_datetime(tactical_df['date'])
                    
                    # Get team's tactical matches
                    team_tactical = tactical_df[
                        (tactical_df['home_team'].str.contains(team_name, case=False, na=False)) |
                        (tactical_df['away_team'].str.contains(team_name, case=False, na=False))
                    ].copy()
                    
                    # Separate by tournament
                    wc2022_matches = team_tactical[team_tactical['match_id'].str.startswith('WC2022_', na=False)]
                    wc2026_matches = team_tactical[team_tactical['match_id'].str.startswith('WC2026_', na=False)]
                    
                    # Calculate WC2022 stats
                    if not wc2022_matches.empty:
                        home_matches = wc2022_matches[wc2022_matches['home_team'].str.contains(team_name, case=False, na=False)]
                        away_matches = wc2022_matches[wc2022_matches['away_team'].str.contains(team_name, case=False, na=False)]
                        
                        wc2022_wins = 0
                        for _, m in home_matches.iterrows():
                            if m['home_score'] > m['away_score']:
                                wc2022_wins += 1
                        for _, m in away_matches.iterrows():
                            if m['away_score'] > m['home_score']:
                                wc2022_wins += 1
                        
                        poss_vals = []
                        xg_vals = []
                        shots_vals = []
                        for _, m in home_matches.iterrows():
                            if pd.notna(m['home_possession']): poss_vals.append(m['home_possession'])
                            if pd.notna(m['home_xg']): xg_vals.append(m['home_xg'])
                            if pd.notna(m['home_shots']): shots_vals.append(m['home_shots'])
                        for _, m in away_matches.iterrows():
                            if pd.notna(m['away_possession']): poss_vals.append(m['away_possession'])
                            if pd.notna(m['away_xg']): xg_vals.append(m['away_xg'])
                            if pd.notna(m['away_shots']): shots_vals.append(m['away_shots'])
                        
                        home_poss = sum(poss_vals) / len(poss_vals) if poss_vals else 0
                        home_xg = sum(xg_vals) / len(xg_vals) if xg_vals else 0
                        home_shots = sum(shots_vals) / len(shots_vals) if shots_vals else 0
                        away_poss = 0
                        away_xg = 0
                        away_shots = 0
                        
                        wc2022_data = {
                            'matches': len(wc2022_matches),
                            'win_rate': (wc2022_wins / len(wc2022_matches) * 100) if len(wc2022_matches) > 0 else 0,
                            'avg_possession': (home_poss + away_poss) / 2 if len(wc2022_matches) > 0 else 0,
                            'avg_xg': (home_xg + away_xg) / 2 if len(wc2022_matches) > 0 else 0,
                            'avg_shots': (home_shots + away_shots) / 2 if len(wc2022_matches) > 0 else 0,
                        }
                    
                    # Calculate WC2026 stats
                    if not wc2026_matches.empty:
                        home_matches = wc2026_matches[wc2026_matches['home_team'].str.contains(team_name, case=False, na=False)]
                        away_matches = wc2026_matches[wc2026_matches['away_team'].str.contains(team_name, case=False, na=False)]
                        
                        wc2026_wins = 0
                        for _, m in home_matches.iterrows():
                            if m['home_score'] > m['away_score']:
                                wc2026_wins += 1
                        for _, m in away_matches.iterrows():
                            if m['away_score'] > m['home_score']:
                                wc2026_wins += 1
                        
                        poss_vals = []
                        xg_vals = []
                        shots_vals = []
                        for _, m in home_matches.iterrows():
                            if pd.notna(m['home_possession']): poss_vals.append(m['home_possession'])
                            if pd.notna(m['home_xg']): xg_vals.append(m['home_xg'])
                            if pd.notna(m['home_shots']): shots_vals.append(m['home_shots'])
                        for _, m in away_matches.iterrows():
                            if pd.notna(m['away_possession']): poss_vals.append(m['away_possession'])
                            if pd.notna(m['away_xg']): xg_vals.append(m['away_xg'])
                            if pd.notna(m['away_shots']): shots_vals.append(m['away_shots'])
                        
                        home_poss = sum(poss_vals) / len(poss_vals) if poss_vals else 0
                        home_xg = sum(xg_vals) / len(xg_vals) if xg_vals else 0
                        home_shots = sum(shots_vals) / len(shots_vals) if shots_vals else 0
                        away_poss = 0
                        away_xg = 0
                        away_shots = 0
                        
                        wc2026_data = {
                            'matches': len(wc2026_matches),
                            'win_rate': (wc2026_wins / len(wc2026_matches) * 100) if len(wc2026_matches) > 0 else 0,
                            'avg_possession': (home_poss + away_poss) / 2 if len(wc2026_matches) > 0 else 0,
                            'avg_xg': (home_xg + away_xg) / 2 if len(wc2026_matches) > 0 else 0,
                            'avg_shots': (home_shots + away_shots) / 2 if len(wc2026_matches) > 0 else 0,
                        }
                
                # Build JSON output for LLM analysis
                result = {
                    "team_name": team_name,
                    "overall_performance": {
                        "total_matches": int(total_matches),
                        "wins": int(wins),
                        "draws": int(draws),
                        "losses": int(losses),
                        "win_rate": round(float(win_rate), 1),
                        "goals_scored": int(goals_scored),
                        "goals_conceded": int(goals_conceded),
                        "goal_difference": int(goal_difference),
                        "avg_goals_scored": round(float(avg_goals_scored), 2),
                        "avg_goals_conceded": round(float(avg_goals_conceded), 2)
                    },
                    "recent_form": {
                        "last_10_matches": form_string,
                        "form_score": round(float(form_score), 1)
                    },
                    "tournament_data": {}
                }
                
                # Add tournament data if available
                if wc2022_data:
                    result["tournament_data"]["world_cup_2022"] = {
                        "matches_played": wc2022_data['matches'],
                        "win_rate": round(float(wc2022_data['win_rate']), 1),
                        "avg_possession": round(float(wc2022_data['avg_possession']), 1),
                        "avg_xg": round(float(wc2022_data['avg_xg']), 2) if wc2022_data['avg_xg'] > 0 else None,
                        "avg_shots": round(float(wc2022_data['avg_shots']), 1)
                    }
                
                if wc2026_data:
                    result["tournament_data"]["world_cup_2026"] = {
                        "matches_played": wc2026_data['matches'],
                        "win_rate": round(float(wc2026_data['win_rate']), 1),
                        "avg_possession": round(float(wc2026_data['avg_possession']), 1),
                        "avg_xg": round(float(wc2026_data['avg_xg']), 2) if wc2026_data['avg_xg'] > 0 else None,
                        "avg_shots": round(float(wc2026_data['avg_shots']), 1)
                    }
                
                # Add data source info
                result["data_sources"] = {
                    "historical_results": "results.csv (1872-2026, ~49,000 matches)",
                    "tactical_data_available": bool(wc2022_data or wc2026_data),
                    "tournaments_with_tactical_data": []
                }
                
                if wc2022_data:
                    result["data_sources"]["tournaments_with_tactical_data"].append("World Cup 2022")
                if wc2026_data:
                    result["data_sources"]["tournaments_with_tactical_data"].append("World Cup 2026")
                
                self.log(f"Successfully analyzed {team_name}")
                self.status = f"Analyzed {team_name}"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                error_msg = f"Error in analyze_team tool: {e}"
                self.log(error_msg)
                self.status = "Error"
                return error_msg
        
        return StructuredTool.from_function(
            func=analyze_team,
            name="analyze_team",
            description=(
                "Get comprehensive team performance data in JSON format. Returns overall statistics (matches, wins, goals), "
                "recent form (last 10 matches), and tournament tactical data (possession, xG, shots) for major tournaments "
                "(World Cup 2022/2026, etc.). Data from results.csv (1872-2026) and tactical_stats.csv (tournament matches). "
                "Use when you need detailed team analysis data for interpretation."
            )
        )

# Made with Bob
