"""
Match Analyzer for Tactical Pulse Agent
Combines data loading and metrics calculation for comprehensive match analysis
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import logging
import json

from .data_loader import MatchDataLoader
from .metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)


class MatchAnalyzer:
    """
    High-level match analysis combining data loading and metrics calculation.
    Provides comprehensive insights into matches, teams, and players.
    """
    
    def __init__(self, data_path: str = "data/match_data/results.csv"):
        """
        Initialize the Match Analyzer.
        
        Args:
            data_path: Path to match data CSV file
        """
        self.data_loader = MatchDataLoader(data_path)
        self.metrics_calc = MetricsCalculator()
        self.llm = None  # Will be initialized when needed
        logger.info("Match Analyzer initialized")
    
    def initialize_llm(
        self,
        provider: str = "ollama",
        model_name: str = "granite4.1:8b",
        **kwargs
    ):
        """
        Initialize the LLM for AI-powered insights.
        
        Args:
            provider: LLM provider (ollama, ibm_granite, openai, etc.)
            model_name: Model name
            **kwargs: Additional provider-specific parameters
        """
        try:
            # Import LLM factory from VAR-Lens
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from src.agents.var_lens.llm_providers import LLMFactory
            
            self.llm = LLMFactory.create_llm(
                provider=provider,
                model_name=model_name,
                temperature=0.7,
                max_tokens=1000,
                **kwargs
            )
            logger.info(f"LLM initialized: {provider}/{model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return False
    
    def analyze_team(
        self,
        team_name: str,
        num_matches: int = 10
    ) -> Dict[str, Any]:
        """
        Comprehensive team analysis.
        
        Args:
            team_name: Name of the team
            num_matches: Number of recent matches to analyze
            
        Returns:
            Dictionary with complete team analysis
        """
        logger.info(f"Analyzing team: {team_name}")
        
        # Get team matches
        matches = self.data_loader.get_team_matches(team_name, limit=num_matches)
        
        if matches.empty:
            return {
                'team': team_name,
                'error': 'No matches found',
                'matches_analyzed': 0
            }
        
        # Get basic stats
        stats = self.data_loader.get_team_stats(team_name, last_n_matches=num_matches)
        
        # Calculate form
        form = self.metrics_calc.calculate_form(matches, team_name, window=5)
        
        # Combine all analysis
        analysis = {
            'team': team_name,
            'matches_analyzed': len(matches),
            'statistics': stats,
            'form': form,
            'recent_matches': []
        }
        
        # Add recent match details
        for idx, match in matches.head(5).iterrows():
            match_info = {
                'date': str(match.get('date', 'Unknown')),
                'home_team': match.get('home_team', 'Unknown'),
                'away_team': match.get('away_team', 'Unknown'),
                'score': f"{match.get('home_score', 0):.0f}-{match.get('away_score', 0):.0f}",
                'tournament': match.get('tournament', 'Unknown')
            }
            analysis['recent_matches'].append(match_info)
        
        return analysis
    
    def analyze_head_to_head(
        self,
        team1: str,
        team2: str,
        num_matches: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze head-to-head record between two teams.
        
        Args:
            team1: First team name
            team2: Second team name
            num_matches: Number of recent H2H matches
            
        Returns:
            Dictionary with H2H analysis
        """
        logger.info(f"Analyzing H2H: {team1} vs {team2}")
        
        # Get H2H matches
        matches = self.data_loader.get_head_to_head(team1, team2, limit=num_matches)
        
        if matches.empty:
            return {
                'team1': team1,
                'team2': team2,
                'error': 'No head-to-head matches found',
                'matches_analyzed': 0
            }
        
        # Calculate H2H stats
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals = 0
        team2_goals = 0
        
        for _, match in matches.iterrows():
            home = match.get('home_team', '')
            away = match.get('away_team', '')
            home_score = float(match.get('home_score', 0) or 0)
            away_score = float(match.get('away_score', 0) or 0)
            
            # Skip if scores are NaN
            if pd.isna(home_score) or pd.isna(away_score):
                continue
            
            # Determine which team is which
            team1_is_home = team1.lower() in str(home).lower()
            
            if team1_is_home:
                team1_goals += home_score
                team2_goals += away_score
                if home_score > away_score:
                    team1_wins += 1
                elif home_score < away_score:
                    team2_wins += 1
                else:
                    draws += 1
            else:
                team1_goals += away_score
                team2_goals += home_score
                if away_score > home_score:
                    team1_wins += 1
                elif away_score < home_score:
                    team2_wins += 1
                else:
                    draws += 1
        
        total_matches = team1_wins + team2_wins + draws
        
        return {
            'team1': team1,
            'team2': team2,
            'matches_analyzed': len(matches),
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_goals': int(team1_goals),
            'team2_goals': int(team2_goals),
            'team1_win_rate': round(team1_wins / total_matches * 100, 1) if total_matches > 0 else 0.0,
            'recent_matches': [
                {
                    'date': str(match.get('date', 'Unknown')),
                    'home_team': match.get('home_team', 'Unknown'),
                    'away_team': match.get('away_team', 'Unknown'),
                    'score': f"{match.get('home_score', 0):.0f}-{match.get('away_score', 0):.0f}",
                    'tournament': match.get('tournament', 'Unknown')
                }
                for _, match in matches.head(5).iterrows()
            ]
        }
    
    def predict_match(
        self,
        home_team: str,
        away_team: str,
        num_recent_matches: int = 10
    ) -> Dict[str, Any]:
        """
        Predict match outcome based on recent form and statistics.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            num_recent_matches: Number of recent matches to consider
            
        Returns:
            Dictionary with match prediction
        """
        logger.info(f"Predicting match: {home_team} vs {away_team}")
        
        # Get team statistics
        home_stats = self.data_loader.get_team_stats(home_team, last_n_matches=num_recent_matches)
        away_stats = self.data_loader.get_team_stats(away_team, last_n_matches=num_recent_matches)
        
        # Get team form
        home_matches = self.data_loader.get_team_matches(home_team, limit=num_recent_matches)
        away_matches = self.data_loader.get_team_matches(away_team, limit=num_recent_matches)
        
        home_form = self.metrics_calc.calculate_form(home_matches, home_team, window=5)
        away_form = self.metrics_calc.calculate_form(away_matches, away_team, window=5)
        
        # Add form scores to stats
        home_stats['form_score'] = home_form['form_score']
        away_stats['form_score'] = away_form['form_score']
        
        # Get prediction
        prediction = self.metrics_calc.predict_match_outcome(home_stats, away_stats)
        
        # Get H2H record
        h2h = self.analyze_head_to_head(home_team, away_team, num_matches=5)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_form': home_form,
            'away_form': away_form,
            'home_stats': {
                'matches': home_stats['matches_played'],
                'wins': home_stats['wins'],
                'win_rate': home_stats['win_rate'],
                'avg_goals': home_stats.get('avg_goals_scored', 0)
            },
            'away_stats': {
                'matches': away_stats['matches_played'],
                'wins': away_stats['wins'],
                'win_rate': away_stats['win_rate'],
                'avg_goals': away_stats.get('avg_goals_scored', 0)
            },
            'prediction': prediction,
            'head_to_head': {
                'total_matches': h2h.get('total_matches', 0),
                'home_wins': h2h.get('team1_wins', 0),
                'away_wins': h2h.get('team2_wins', 0),
                'draws': h2h.get('draws', 0)
            }
        }
    
    def analyze_tournament(
        self,
        tournament_name: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze matches from a specific tournament.
        
        Args:
            tournament_name: Name of the tournament
            limit: Maximum number of matches to analyze
            
        Returns:
            Dictionary with tournament analysis
        """
        logger.info(f"Analyzing tournament: {tournament_name}")
        
        matches = self.data_loader.get_tournament_matches(tournament_name, limit=limit)
        
        if matches.empty:
            return {
                'tournament': tournament_name,
                'error': 'No matches found',
                'matches_analyzed': 0
            }
        
        # Calculate tournament statistics
        total_goals = 0
        total_matches = 0
        teams = set()
        
        for _, match in matches.iterrows():
            home_score = float(match.get('home_score', 0) or 0)
            away_score = float(match.get('away_score', 0) or 0)
            
            if not pd.isna(home_score) and not pd.isna(away_score):
                total_goals += home_score + away_score
                total_matches += 1
            
            teams.add(match.get('home_team', ''))
            teams.add(match.get('away_team', ''))
        
        avg_goals = total_goals / total_matches if total_matches > 0 else 0
        
        return {
            'tournament': tournament_name,
            'matches_analyzed': len(matches),
            'total_matches': total_matches,
            'total_goals': int(total_goals),
            'avg_goals_per_match': round(avg_goals, 2),
            'unique_teams': len(teams),
            'recent_matches': [
                {
                    'date': str(match.get('date', 'Unknown')),
                    'home_team': match.get('home_team', 'Unknown'),
                    'away_team': match.get('away_team', 'Unknown'),
                    'score': f"{match.get('home_score', 0):.0f}-{match.get('away_score', 0):.0f}"
                }
                for _, match in matches.head(10).iterrows()
            ]
        }
    
    def get_insights(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate natural language insights based on query.
        
        Args:
            query: User's question or query
            context: Optional context information
            
        Returns:
            Natural language response
        """
        query_lower = query.lower()
        
        # Simple keyword-based routing
        if 'predict' in query_lower or 'who will win' in query_lower:
            # Extract team names (simplified)
            words = query.split()
            if 'vs' in query_lower or 'versus' in query_lower:
                parts = query_lower.split('vs' if 'vs' in query_lower else 'versus')
                if len(parts) == 2:
                    team1 = parts[0].strip().split()[-1].title()
                    team2 = parts[1].strip().split()[0].title()
                    prediction = self.predict_match(team1, team2)
                    return f"Prediction for {team1} vs {team2}: {prediction['prediction']['predicted_score']}"
        
        elif 'form' in query_lower:
            # Extract team name
            for word in query.split():
                if word.istitle() and len(word) > 3:
                    analysis = self.analyze_team(word)
                    if 'error' not in analysis:
                        form = analysis['form']
                        return f"{word}'s recent form: {form['form_string']} (Form score: {form['form_score']:.1f}/100)"
        
        elif 'head to head' in query_lower or 'h2h' in query_lower:
            # Extract team names
            words = [w for w in query.split() if w.istitle() and len(w) > 3]
            if len(words) >= 2:
                h2h = self.analyze_head_to_head(words[0], words[1])
                if 'error' not in h2h:
                    return f"{words[0]} vs {words[1]} H2H: {h2h['team1_wins']}W-{h2h['draws']}D-{h2h['team2_wins']}L"
        
        return "I can help you with team analysis, match predictions, and head-to-head records. Please provide team names or specific questions."
    def _calculate_comprehensive_tactical_stats(
        self,
        tactical_data: pd.DataFrame,
        team_name: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive tactical statistics from all 49 columns.
        
        Args:
            tactical_data: DataFrame with tactical match data
            team_name: Name of the team to analyze
            
        Returns:
            Dictionary with comprehensive tactical statistics
        """
        if tactical_data.empty:
            return {}
        
        stats = {}
        
        # Determine if team is home or away in each match
        is_home_matches = tactical_data['home_team'].str.contains(team_name, case=False, na=False)
        is_away_matches = tactical_data['away_team'].str.contains(team_name, case=False, na=False)
        
        # Formation Analysis
        home_formations = tactical_data.loc[is_home_matches, 'home_formation'].dropna()
        away_formations = tactical_data.loc[is_away_matches, 'away_formation'].dropna()
        all_formations = list(home_formations) + list(away_formations)
        if all_formations:
            stats['most_used_formation'] = max(set(all_formations), key=all_formations.count)
            stats['formation_variety'] = len(set(all_formations))
        
        # Possession Statistics
        home_poss = tactical_data.loc[is_home_matches, 'home_possession'].dropna()
        away_poss = tactical_data.loc[is_away_matches, 'away_possession'].dropna()
        all_poss = pd.concat([home_poss, away_poss])
        if not all_poss.empty:
            stats['avg_possession'] = float(all_poss.mean())
            stats['possession_consistency'] = float(all_poss.std())
        
        # Shooting Statistics
        home_shots = tactical_data.loc[is_home_matches, 'home_shots'].dropna()
        away_shots = tactical_data.loc[is_away_matches, 'away_shots'].dropna()
        all_shots = pd.concat([home_shots, away_shots])
        if not all_shots.empty:
            stats['avg_shots'] = float(all_shots.mean())
            stats['shots_consistency'] = float(all_shots.std())
        
        # Shot Accuracy
        home_shots_on = tactical_data.loc[is_home_matches, 'home_shots_on_target'].dropna()
        away_shots_on = tactical_data.loc[is_away_matches, 'away_shots_on_target'].dropna()
        all_shots_on = pd.concat([home_shots_on, away_shots_on])
        if not all_shots.empty and not all_shots_on.empty:
            stats['shot_accuracy'] = float((all_shots_on.sum() / all_shots.sum()) * 100)
        
        # Shot Distribution
        home_inside = tactical_data.loc[is_home_matches, 'home_shots_insidebox'].dropna()
        away_inside = tactical_data.loc[is_away_matches, 'away_shots_insidebox'].dropna()
        home_outside = tactical_data.loc[is_home_matches, 'home_shots_outsidebox'].dropna()
        away_outside = tactical_data.loc[is_away_matches, 'away_shots_outsidebox'].dropna()
        all_inside = pd.concat([home_inside, away_inside])
        all_outside = pd.concat([home_outside, away_outside])
        if not all_inside.empty:
            stats['avg_shots_insidebox'] = float(all_inside.mean())
        if not all_outside.empty:
            stats['avg_shots_outsidebox'] = float(all_outside.mean())
        
        # Expected Goals (xG)
        home_xg = tactical_data.loc[is_home_matches, 'home_xg'].dropna()
        away_xg = tactical_data.loc[is_away_matches, 'away_xg'].dropna()
        all_xg = pd.concat([home_xg, away_xg])
        if not all_xg.empty:
            stats['avg_xg'] = float(all_xg.mean())
        
        # Passing Statistics
        home_passes = tactical_data.loc[is_home_matches, 'home_passes'].dropna()
        away_passes = tactical_data.loc[is_away_matches, 'away_passes'].dropna()
        all_passes = pd.concat([home_passes, away_passes])
        if not all_passes.empty:
            stats['avg_passes'] = float(all_passes.mean())
        
        home_pass_acc = tactical_data.loc[is_home_matches, 'home_pass_accuracy'].dropna()
        away_pass_acc = tactical_data.loc[is_away_matches, 'away_pass_accuracy'].dropna()
        all_pass_acc = pd.concat([home_pass_acc, away_pass_acc])
        if not all_pass_acc.empty:
            stats['avg_pass_accuracy'] = float(all_pass_acc.mean())
        
        # Defensive Statistics
        home_tackles = tactical_data.loc[is_home_matches, 'home_tackles'].dropna()
        away_tackles = tactical_data.loc[is_away_matches, 'away_tackles'].dropna()
        all_tackles = pd.concat([home_tackles, away_tackles])
        if not all_tackles.empty:
            stats['avg_tackles'] = float(all_tackles.mean())
        
        home_interceptions = tactical_data.loc[is_home_matches, 'home_interceptions'].dropna()
        away_interceptions = tactical_data.loc[is_away_matches, 'away_interceptions'].dropna()
        all_interceptions = pd.concat([home_interceptions, away_interceptions])
        if not all_interceptions.empty:
            stats['avg_interceptions'] = float(all_interceptions.mean())
        
        home_clearances = tactical_data.loc[is_home_matches, 'home_clearances'].dropna()
        away_clearances = tactical_data.loc[is_away_matches, 'away_clearances'].dropna()
        all_clearances = pd.concat([home_clearances, away_clearances])
        if not all_clearances.empty:
            stats['avg_clearances'] = float(all_clearances.mean())
        
        # Set Pieces
        home_corners = tactical_data.loc[is_home_matches, 'home_corners'].dropna()
        away_corners = tactical_data.loc[is_away_matches, 'away_corners'].dropna()
        all_corners = pd.concat([home_corners, away_corners])
        if not all_corners.empty:
            stats['avg_corners'] = float(all_corners.mean())
        
        home_offsides = tactical_data.loc[is_home_matches, 'home_offsides'].dropna()
        away_offsides = tactical_data.loc[is_away_matches, 'away_offsides'].dropna()
        all_offsides = pd.concat([home_offsides, away_offsides])
        if not all_offsides.empty:
            stats['avg_offsides'] = float(all_offsides.mean())
        
        # Discipline
        home_fouls = tactical_data.loc[is_home_matches, 'home_fouls'].dropna()
        away_fouls = tactical_data.loc[is_away_matches, 'away_fouls'].dropna()
        all_fouls = pd.concat([home_fouls, away_fouls])
        if not all_fouls.empty:
            stats['avg_fouls'] = float(all_fouls.mean())
        
        home_yellows = tactical_data.loc[is_home_matches, 'home_yellow_cards'].dropna()
        away_yellows = tactical_data.loc[is_away_matches, 'away_yellow_cards'].dropna()
        all_yellows = pd.concat([home_yellows, away_yellows])
        if not all_yellows.empty:
            stats['avg_yellow_cards'] = float(all_yellows.mean())
        
        home_reds = tactical_data.loc[is_home_matches, 'home_red_cards'].dropna()
        away_reds = tactical_data.loc[is_away_matches, 'away_red_cards'].dropna()
        all_reds = pd.concat([home_reds, away_reds])
        if not all_reds.empty:
            stats['total_red_cards'] = int(all_reds.sum())
        
        # Goalkeeping
        home_saves = tactical_data.loc[is_home_matches, 'home_goalkeeper_saves'].dropna()
        away_saves = tactical_data.loc[is_away_matches, 'away_goalkeeper_saves'].dropna()
        all_saves = pd.concat([home_saves, away_saves])
        if not all_saves.empty:
            stats['avg_goalkeeper_saves'] = float(all_saves.mean())
        
        # Calculate derived metrics
        if 'avg_shots' in stats and 'avg_shots_insidebox' in stats:
            stats['shot_location_ratio'] = (stats['avg_shots_insidebox'] / stats['avg_shots'] * 100) if stats['avg_shots'] > 0 else 0
        
        if 'avg_possession' in stats:
            if stats['avg_possession'] >= 55:
                stats['playing_style'] = 'Possession-based'
            elif stats['avg_possession'] <= 45:
                stats['playing_style'] = 'Counter-attacking'
            else:
                stats['playing_style'] = 'Balanced'
        
        if 'avg_tackles' in stats and 'avg_interceptions' in stats:
            stats['defensive_intensity'] = stats['avg_tackles'] + stats['avg_interceptions']
        
        stats['matches_analyzed'] = len(tactical_data)
        
        return stats
    
    
    def generate_ai_insights(
        self,
        team_name: str,
        num_matches: int = 10,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights using Granite LLM with tactical data.
        
        Args:
            team_name: Team name to analyze
            num_matches: Number of recent matches
            analysis_type: Type of analysis (comprehensive, tactical, performance)
            
        Returns:
            Dictionary with AI insights
        """
        # Get statistical analysis first
        analysis = self.analyze_team(team_name, num_matches)
        
        if 'error' in analysis:
            return analysis
        
        # Get tactical data if available
        tactical_data = self.data_loader.get_tactical_data(team_name, limit=num_matches)
        has_tactical_data = not tactical_data.empty
        
        # Calculate comprehensive tactical statistics
        tactical_stats = self._calculate_comprehensive_tactical_stats(tactical_data, team_name) if has_tactical_data else {}
        
        # Initialize LLM if not already done
        if self.llm is None:
            if not self.initialize_llm():
                return {
                    'error': 'LLM not available',
                    'statistics': analysis,
                    'ai_insights': None
                }
        
        try:
            # Prepare data for LLM
            stats = analysis['statistics']
            form = analysis['form']
            recent_matches = analysis.get('recent_matches', [])
            
            # Build comprehensive tactical summary if data available
            tactical_summary = ""
            if has_tactical_data and tactical_stats:
                tactical_summary = f"""
COMPREHENSIVE TACTICAL ANALYSIS (from {tactical_stats.get('matches_analyzed', 0)} matches):

FORMATION & STYLE:
- Primary Formation: {tactical_stats.get('most_used_formation', 'N/A')}
- Formation Variety: {tactical_stats.get('formation_variety', 0)} different formations used
- Playing Style: {tactical_stats.get('playing_style', 'N/A')}

POSSESSION & CONTROL:
- Average Possession: {tactical_stats.get('avg_possession', 0):.1f}%
- Possession Consistency: ±{tactical_stats.get('possession_consistency', 0):.1f}%

ATTACKING METRICS:
- Shots per Match: {tactical_stats.get('avg_shots', 0):.1f}
- Shot Accuracy: {tactical_stats.get('shot_accuracy', 0):.1f}%
- Shots Inside Box: {tactical_stats.get('avg_shots_insidebox', 0):.1f} ({tactical_stats.get('shot_location_ratio', 0):.1f}% of total)
- Shots Outside Box: {tactical_stats.get('avg_shots_outsidebox', 0):.1f}
- Expected Goals (xG): {tactical_stats.get('avg_xg', 0):.2f} per match

PASSING & BUILD-UP:
- Total Passes: {tactical_stats.get('avg_passes', 0):.0f} per match
- Pass Accuracy: {tactical_stats.get('avg_pass_accuracy', 0):.1f}%

DEFENSIVE METRICS:
- Tackles per Match: {tactical_stats.get('avg_tackles', 0):.1f}
- Interceptions: {tactical_stats.get('avg_interceptions', 0):.1f}
- Clearances: {tactical_stats.get('avg_clearances', 0):.1f}
- Defensive Intensity: {tactical_stats.get('defensive_intensity', 0):.1f}

SET PIECES:
- Corners Won: {tactical_stats.get('avg_corners', 0):.1f} per match
- Offsides: {tactical_stats.get('avg_offsides', 0):.1f} per match

DISCIPLINE:
- Fouls Committed: {tactical_stats.get('avg_fouls', 0):.1f} per match
- Yellow Cards: {tactical_stats.get('avg_yellow_cards', 0):.1f} per match
- Red Cards: {tactical_stats.get('total_red_cards', 0)} total

GOALKEEPING:
- Saves per Match: {tactical_stats.get('avg_goalkeeper_saves', 0):.1f}
"""
            
            # Create enhanced prompt based on analysis type
            if analysis_type == "comprehensive":
                prompt = f"""You are an elite football tactical analyst with expertise in data-driven performance analysis. Analyze the following comprehensive statistics for {team_name}:

TEAM: {team_name}
MATCHES ANALYZED: {analysis['matches_analyzed']}

PERFORMANCE STATISTICS:
- Win Rate: {stats['win_rate']:.1%}
- Record: {stats['wins']}W-{stats['draws']}D-{stats['losses']}L
- Goals Scored: {stats.get('goals_scored', 'N/A')} (Avg: {stats.get('avg_goals_scored', 0):.2f}/match)
- Goals Conceded: {stats.get('goals_conceded', 'N/A')} (Avg: {stats.get('avg_goals_conceded', 0):.2f}/match)
- Goal Difference: {stats.get('goal_difference', 'N/A')}
- Recent Form: {form['form_string']} (Form Score: {form['form_score']:.1f}/100)
{tactical_summary}
RECENT MATCHES:
{json.dumps(recent_matches[:3], indent=2)}

ANALYSIS REQUIREMENTS:
Provide a comprehensive, data-driven tactical analysis covering:

1. FORMATION & TACTICAL SETUP:
   - Analyze the primary formation and its effectiveness
   - Evaluate formation variety and tactical flexibility
   - Assess how the formation supports the team's playing style

2. ATTACKING ANALYSIS:
   - Shot quality and conversion efficiency (xG vs actual goals)
   - Shot location patterns (inside vs outside box)
   - Attacking build-up through passing statistics
   - Possession effectiveness in creating chances

3. DEFENSIVE ORGANIZATION:
   - Defensive intensity (tackles + interceptions)
   - Clearance patterns and defensive solidity
   - Goalkeeper performance and shot-stopping ability
   - Defensive discipline (fouls, cards)

4. POSSESSION & CONTROL:
   - Possession percentage and its correlation with results
   - Pass accuracy and build-up play quality
   - Playing style classification (possession-based/counter-attacking/balanced)

5. SET PIECES & DISCIPLINE:
   - Corner effectiveness
   - Offside trap usage
   - Disciplinary record and its impact

6. STRENGTHS & WEAKNESSES:
   - Identify 3 key strengths based on data
   - Identify 3 areas for improvement
   - Provide specific tactical recommendations

7. PERFORMANCE TRENDS & PREDICTIONS:
   - Analyze form trajectory
   - Predict likely performance in upcoming matches
   - Suggest tactical adjustments for improvement

Keep analysis professional, specific, and backed by the provided statistics."""

            elif analysis_type == "tactical":
                prompt = f"""You are a professional football tactical analyst. Conduct an in-depth tactical analysis of {team_name}:

TEAM: {team_name}
FORM: {form['form_string']} (Score: {form['form_score']:.1f}/100)
WIN RATE: {stats['win_rate']:.1%}
GOALS: {stats.get('avg_goals_scored', 0):.2f} scored, {stats.get('avg_goals_conceded', 0):.2f} conceded per match
{tactical_summary}
RECENT MATCHES:
{json.dumps(recent_matches[:3], indent=2)}

TACTICAL ANALYSIS FRAMEWORK:

1. OFFENSIVE TACTICS:
   - Formation's attacking structure and width
   - Shot generation: quantity ({tactical_stats.get('avg_shots', 0):.1f}/match) vs quality (xG: {tactical_stats.get('avg_xg', 0):.2f})
   - Shot location strategy: {tactical_stats.get('shot_location_ratio', 0):.1f}% inside box
   - Possession-based attack vs direct play
   - Passing patterns: {tactical_stats.get('avg_passes', 0):.0f} passes at {tactical_stats.get('avg_pass_accuracy', 0):.1f}% accuracy
   - Set piece threat: {tactical_stats.get('avg_corners', 0):.1f} corners/match

2. DEFENSIVE STRUCTURE:
   - Formation's defensive shape ({tactical_stats.get('most_used_formation', 'N/A')})
   - Defensive intensity: {tactical_stats.get('defensive_intensity', 0):.1f} (tackles + interceptions)
   - Pressing strategy and offside trap: {tactical_stats.get('avg_offsides', 0):.1f} offsides/match
   - Goalkeeper involvement: {tactical_stats.get('avg_goalkeeper_saves', 0):.1f} saves/match
   - Defensive discipline: {tactical_stats.get('avg_fouls', 0):.1f} fouls, {tactical_stats.get('avg_yellow_cards', 0):.1f} yellows/match

3. MATCH CONTROL & TEMPO:
   - Possession dominance: {tactical_stats.get('avg_possession', 0):.1f}%
   - Playing style: {tactical_stats.get('playing_style', 'N/A')}
   - Tempo control through passing
   - Transition speed (counter-attacks vs build-up)

4. TACTICAL PATTERNS:
   - Formation consistency vs flexibility
   - Key tactical tendencies from data
   - Match-to-match adaptability

5. TACTICAL RECOMMENDATIONS:
   - Specific formation adjustments
   - Attacking pattern improvements
   - Defensive organization enhancements
   - Set piece optimization
   - Player positioning suggestions

Provide detailed, actionable tactical insights based on all available data."""

            else:  # performance
                prompt = f"""Evaluate the performance of {team_name}:

Form Score: {form['form_score']:.1f}/100
Win Rate: {stats['win_rate']:.1%}
Recent Results: {form['form_string']}

Provide performance analysis:
1. Current performance level
2. Consistency and reliability
3. Momentum and trajectory
4. Key performance indicators
5. Performance outlook"""
            
            # Generate insights with LLM
            logger.info(f"Generating AI insights for {team_name}...")
            ai_response = self.llm.invoke(prompt)
            
            return {
                'team': team_name,
                'matches_analyzed': analysis['matches_analyzed'],
                'statistics': stats,
                'form': form,
                'recent_matches': recent_matches,
                'ai_insights': {
                    'type': analysis_type,
                    'content': ai_response,
                    'generated_by': 'IBM Granite 4.1 8B'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                'error': str(e),
                'statistics': analysis,
                'ai_insights': None
            }
    
    def generate_match_preview(
        self,
        home_team: str,
        away_team: str,
        num_matches: int = 10
    ) -> Dict[str, Any]:
        """
        Generate AI-powered match preview with predictions and insights.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            num_matches: Number of recent matches to consider
            
        Returns:
            Dictionary with match preview and AI insights
        """
        # Get prediction first
        prediction = self.predict_match(home_team, away_team, num_matches)
        
        if 'error' in prediction:
            return prediction
        
        # Initialize LLM if needed
        if self.llm is None:
            if not self.initialize_llm():
                return {
                    'error': 'LLM not available',
                    'prediction': prediction,
                    'ai_preview': None
                }
        
        try:
            # Get tactical data for both teams
            home_tactical = self.data_loader.get_tactical_data(home_team, limit=5)
            away_tactical = self.data_loader.get_tactical_data(away_team, limit=5)
            
            # Build tactical summaries
            home_tactical_summary = ""
            away_tactical_summary = ""
            
            if not home_tactical.empty:
                home_formations = home_tactical['home_formation'].dropna().tolist() if 'home_formation' in home_tactical.columns else []
                home_formation = max(set(home_formations), key=home_formations.count) if home_formations else "N/A"
                home_poss = home_tactical['home_possession'].fillna(0).mean() if 'home_possession' in home_tactical.columns else 0
                home_tactical_summary = f"\n- Preferred Formation: {home_formation}\n- Average Possession: {home_poss:.1f}%"
            
            if not away_tactical.empty:
                away_formations = away_tactical['away_formation'].dropna().tolist() if 'away_formation' in away_tactical.columns else []
                away_formation = max(set(away_formations), key=away_formations.count) if away_formations else "N/A"
                away_poss = away_tactical['away_possession'].fillna(0).mean() if 'away_possession' in away_tactical.columns else 0
                away_tactical_summary = f"\n- Preferred Formation: {away_formation}\n- Average Possession: {away_poss:.1f}%"
            
            # Prepare match preview prompt
            prompt = f"""Generate a professional match preview for this upcoming football match:

Match: {home_team} vs {away_team}

Home Team ({home_team}):
- Recent Form: {prediction['home_form']['form_string']}
- Form Score: {prediction['home_form']['form_score']:.1f}/100
- Win Rate: {prediction['home_stats']['win_rate']:.1%}
- Average Goals: {prediction['home_stats'].get('avg_goals', 'N/A')}{home_tactical_summary}

Away Team ({away_team}):
- Recent Form: {prediction['away_form']['form_string']}
- Form Score: {prediction['away_form']['form_score']:.1f}/100
- Win Rate: {prediction['away_stats']['win_rate']:.1%}
- Average Goals: {prediction['away_stats'].get('avg_goals', 'N/A')}{away_tactical_summary}

Head-to-Head:
- Total Matches: {prediction['head_to_head']['total_matches']}
- {home_team} Wins: {prediction['head_to_head']['home_wins']}
- {away_team} Wins: {prediction['head_to_head']['away_wins']}
- Draws: {prediction['head_to_head']['draws']}

Statistical Prediction:
- Predicted Score: {prediction['prediction']['predicted_score']}
- Home Win: {prediction['prediction']['home_win_probability']}%
- Draw: {prediction['prediction']['draw_probability']}%
- Away Win: {prediction['prediction']['away_win_probability']}%

Provide a comprehensive match preview including:
1. Key matchup analysis (consider formations and playing styles)
2. Tactical battle points (possession, formations, attacking patterns)
3. Players/factors to watch
4. Predicted outcome with reasoning based on tactical and statistical data
5. Potential game scenarios

Keep it engaging and insightful for football fans."""
            
            logger.info(f"Generating match preview: {home_team} vs {away_team}")
            ai_preview = self.llm.invoke(prompt)
            
            return {
                'match': f"{home_team} vs {away_team}",
                'prediction': prediction['prediction'],
                'home_team_analysis': {
                    'team': home_team,
                    'form': prediction['home_form'],
                    'stats': prediction['home_stats']
                },
                'away_team_analysis': {
                    'team': away_team,
                    'form': prediction['away_form'],
                    'stats': prediction['away_stats']
                },
                'head_to_head': prediction['head_to_head'],
                'ai_preview': {
                    'content': ai_preview,
                    'generated_by': 'IBM Granite 4.1 8B'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating match preview: {e}")
            return {
                'error': str(e),
                'prediction': prediction,
                'ai_preview': None
            }


if __name__ == "__main__":
    # Test the match analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MatchAnalyzer()
    
    print("\n" + "="*70)
    print("Match Analyzer - Test Suite")
    print("="*70)
    
    # Test 1: Team Analysis
    print("\nTest 1: Team Analysis")
    analysis = analyzer.analyze_team("Brazil", num_matches=10)
    print(f"Team: {analysis['team']}")
    print(f"Matches: {analysis['matches_analyzed']}")
    print(f"Form: {analysis['form']['form_string']}")
    print(f"Win Rate: {analysis['statistics']['win_rate']:.1%}")
    
    # Test 2: Head-to-Head
    print("\nTest 2: Head-to-Head Analysis")
    h2h = analyzer.analyze_head_to_head("Brazil", "Argentina", num_matches=5)
    print(f"{h2h['team1']} vs {h2h['team2']}")
    print(f"Record: {h2h['team1_wins']}W-{h2h['draws']}D-{h2h['team2_wins']}L")
    
    # Test 3: Match Prediction
    print("\nTest 3: Match Prediction")
    prediction = analyzer.predict_match("Brazil", "Argentina")
    print(f"Prediction: {prediction['prediction']['predicted_score']}")
    print(f"Home Win: {prediction['prediction']['home_win_probability']}%")
    print(f"Draw: {prediction['prediction']['draw_probability']}%")
    print(f"Away Win: {prediction['prediction']['away_win_probability']}%")
    
    # Test 4: Tournament Analysis
    print("\nTest 4: Tournament Analysis")
    tournament = analyzer.analyze_tournament("UEFA Euro", limit=10)
    print(f"Tournament: {tournament['tournament']}")
    print(f"Matches: {tournament['matches_analyzed']}")
    print(f"Avg Goals: {tournament.get('avg_goals_per_match', 0)}")
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)

# Made with Bob
