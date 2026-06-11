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
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
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
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
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
    
    def generate_ai_insights(
        self,
        team_name: str,
        num_matches: int = 10,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights using Granite LLM.
        
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
            
            # Create prompt based on analysis type
            if analysis_type == "comprehensive":
                prompt = f"""Analyze the following football team statistics and provide comprehensive insights:

Team: {team_name}
Matches Analyzed: {analysis['matches_analyzed']}

Statistics:
- Win Rate: {stats['win_rate']:.1%}
- Wins: {stats['wins']}, Draws: {stats['draws']}, Losses: {stats['losses']}
- Goals Scored: {stats.get('goals_scored', 'N/A')}
- Goals Conceded: {stats.get('goals_conceded', 'N/A')}
- Goal Difference: {stats.get('goal_difference', 'N/A')}
- Recent Form: {form['form_string']} (Form Score: {form['form_score']:.1f}/100)

Recent Matches:
{json.dumps(recent_matches[:3], indent=2)}

Provide insights on:
1. Overall team performance and trends
2. Strengths and weaknesses
3. Playing style characteristics
4. Areas for improvement
5. Predictions for future performance

Keep the analysis concise, professional, and data-driven."""

            elif analysis_type == "tactical":
                prompt = f"""Analyze the tactical approach of {team_name} based on these statistics:

Recent Form: {form['form_string']}
Win Rate: {stats['win_rate']:.1%}
Goals per Match: {stats.get('avg_goals_scored', 'N/A')}
Goals Conceded per Match: {stats.get('avg_goals_conceded', 'N/A')}

Recent Matches:
{json.dumps(recent_matches[:3], indent=2)}

Provide tactical insights on:
1. Offensive strategy and effectiveness
2. Defensive organization
3. Match tempo and control
4. Key tactical patterns
5. Recommended tactical adjustments"""

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
            # Prepare match preview prompt
            prompt = f"""Generate a professional match preview for this upcoming football match:

Match: {home_team} vs {away_team}

Home Team ({home_team}):
- Recent Form: {prediction['home_form']['form_string']}
- Form Score: {prediction['home_form']['form_score']:.1f}/100
- Win Rate: {prediction['home_stats']['win_rate']:.1%}
- Average Goals: {prediction['home_stats'].get('avg_goals', 'N/A')}

Away Team ({away_team}):
- Recent Form: {prediction['away_form']['form_string']}
- Form Score: {prediction['away_form']['form_score']:.1f}/100
- Win Rate: {prediction['away_stats']['win_rate']:.1%}
- Average Goals: {prediction['away_stats'].get('avg_goals', 'N/A')}

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
1. Key matchup analysis
2. Tactical battle points
3. Players/factors to watch
4. Predicted outcome with reasoning
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
