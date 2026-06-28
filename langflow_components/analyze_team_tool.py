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
        self.tactical_csv = self.project_root / "data" / "match_data" / "tactical_data.csv"
    
    def build_tool(self) -> Tool:
        """Build the team analysis tool"""
        
        def analyze_team(team_name: str) -> str:
            """Get comprehensive analysis of a team's performance.
            
            Args:
                team_name: Team name (e.g., "Argentina", "Brazil", "Iran")
                
            Returns:
                Analysis from results.csv (1872-2026) and tactical_data.csv (WhoScored scraped matches)
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
                
                # Try to load tactical data from tactical_data.csv
                tactical_data_by_tournament = {}
                
                if self.tactical_csv.exists():
                    tactical_df = pd.read_csv(self.tactical_csv)
                    tactical_df['date'] = pd.to_datetime(tactical_df['date'])
                    
                    # Get team's tactical matches
                    team_tactical = tactical_df[
                        (tactical_df['home_team'].str.contains(team_name, case=False, na=False)) |
                        (tactical_df['away_team'].str.contains(team_name, case=False, na=False))
                    ].copy()
                    
                    if not team_tactical.empty:
                        # Group by tournament
                        tournaments = team_tactical['tournament'].unique()
                        
                        for tournament in tournaments:
                            tournament_matches = team_tactical[team_tactical['tournament'] == tournament]
                            home_matches = tournament_matches[tournament_matches['home_team'].str.contains(team_name, case=False, na=False)]
                            away_matches = tournament_matches[tournament_matches['away_team'].str.contains(team_name, case=False, na=False)]
                            
                            # Calculate wins
                            tournament_wins = 0
                            for _, m in home_matches.iterrows():
                                if m['home_score'] > m['away_score']:
                                    tournament_wins += 1
                            for _, m in away_matches.iterrows():
                                if m['away_score'] > m['home_score']:
                                    tournament_wins += 1
                            
                            # Collect tactical metrics
                            poss_vals = []
                            shots_vals = []
                            shot_acc_vals = []
                            passes_vals = []
                            pass_acc_vals = []
                            key_passes_vals = []
                            attacking_int_vals = []
                            defensive_int_vals = []
                            
                            for _, m in home_matches.iterrows():
                                if pd.notna(m['home_possession']): poss_vals.append(m['home_possession'])
                                if pd.notna(m['home_shots_total']): shots_vals.append(m['home_shots_total'])
                                if pd.notna(m['home_shot_accuracy']): shot_acc_vals.append(m['home_shot_accuracy'])
                                if pd.notna(m['home_passes_total']): passes_vals.append(m['home_passes_total'])
                                if pd.notna(m['home_pass_accuracy']): pass_acc_vals.append(m['home_pass_accuracy'])
                                if pd.notna(m['home_key_passes']): key_passes_vals.append(m['home_key_passes'])
                                if pd.notna(m['home_attacking_intensity']): attacking_int_vals.append(m['home_attacking_intensity'])
                                if pd.notna(m['home_defensive_intensity']): defensive_int_vals.append(m['home_defensive_intensity'])
                            
                            for _, m in away_matches.iterrows():
                                if pd.notna(m['away_possession']): poss_vals.append(m['away_possession'])
                                if pd.notna(m['away_shots_total']): shots_vals.append(m['away_shots_total'])
                                if pd.notna(m['away_shot_accuracy']): shot_acc_vals.append(m['away_shot_accuracy'])
                                if pd.notna(m['away_passes_total']): passes_vals.append(m['away_passes_total'])
                                if pd.notna(m['away_pass_accuracy']): pass_acc_vals.append(m['away_pass_accuracy'])
                                if pd.notna(m['away_key_passes']): key_passes_vals.append(m['away_key_passes'])
                                if pd.notna(m['away_attacking_intensity']): attacking_int_vals.append(m['away_attacking_intensity'])
                                if pd.notna(m['away_defensive_intensity']): defensive_int_vals.append(m['away_defensive_intensity'])
                            
                            # Calculate averages
                            def safe_avg(vals):
                                return round(sum(vals) / len(vals), 1) if vals else 0
                            
                            tactical_data_by_tournament[tournament] = {
                                'matches': len(tournament_matches),
                                'win_rate': round((tournament_wins / len(tournament_matches) * 100), 1) if len(tournament_matches) > 0 else 0,
                                'avg_possession': safe_avg(poss_vals),
                                'avg_shots': safe_avg(shots_vals),
                                'avg_shot_accuracy': safe_avg(shot_acc_vals),
                                'avg_passes': safe_avg(passes_vals),
                                'avg_pass_accuracy': safe_avg(pass_acc_vals),
                                'avg_key_passes': safe_avg(key_passes_vals),
                                'avg_attacking_intensity': safe_avg(attacking_int_vals),
                                'avg_defensive_intensity': safe_avg(defensive_int_vals)
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
                        "form_score": round(float(form_score), 1),
                        "interpretation": "Form score out of 100 (W=3pts, D=1pt, L=0pts)"
                    },
                    "tactical_data_by_tournament": tactical_data_by_tournament,
                    "data_sources": {
                        "historical_results": "Historical Match Database (1872-2026, ~49,000 matches)",
                        "tactical_data_available": bool(tactical_data_by_tournament),
                        "tactical_data_source": "Tournament Tactical Database",
                        "tournaments_with_tactical_data": list(tactical_data_by_tournament.keys())
                    }
                }
                
                self.log(f"Successfully analyzed {team_name}")
                self.status = f"Analyzed {team_name}: {total_matches} matches"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                self.log(f"Error in analyze_team tool: {e}")
                self.status = "Error"
                return json.dumps({"error": str(e)}, ensure_ascii=False)
        
        return StructuredTool.from_function(
            func=analyze_team,
            name="analyze_team",
            description=(
                "Get comprehensive team performance data in JSON format. Returns overall statistics (matches, wins, goals), "
                "recent form (last 10 matches with W/D/L), and detailed tactical data by tournament (possession, shots, "
                "shot accuracy, passes, pass accuracy, key passes, attacking intensity, defensive intensity). "
                "Data from results.csv (1872-2026, all matches) and tactical_data.csv (WhoScored scraped matches with 41 metrics). "
                "Use when you need complete team analysis with both historical and tactical insights."
            )
        )

# Made with Bob
