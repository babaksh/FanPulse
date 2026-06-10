"""
Metrics Calculator for Tactical Pulse Agent
Calculates advanced football statistics and performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculates advanced football metrics and statistics.
    Provides insights into team and player performance.
    """
    
    def __init__(self):
        """Initialize the Metrics Calculator"""
        logger.info("Metrics Calculator initialized")
    
    def calculate_form(
        self,
        matches: pd.DataFrame,
        team_name: str,
        window: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate team form over recent matches.
        
        Args:
            matches: DataFrame with match results
            team_name: Name of the team
            window: Number of recent matches to consider
            
        Returns:
            Dictionary with form metrics
        """
        if matches.empty or len(matches) == 0:
            return {
                'form_string': '',
                'points': 0,
                'form_score': 0.0
            }
        
        form_string = []
        points = 0
        
        for _, match in matches.head(window).iterrows():
            is_home = team_name.lower() in str(match.get('home_team', '')).lower()
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
            # Handle NaN scores
            if pd.isna(home_score) or pd.isna(away_score):
                continue
            
            if is_home:
                if home_score > away_score:
                    form_string.append('W')
                    points += 3
                elif home_score == away_score:
                    form_string.append('D')
                    points += 1
                else:
                    form_string.append('L')
            else:
                if away_score > home_score:
                    form_string.append('W')
                    points += 3
                elif away_score == home_score:
                    form_string.append('D')
                    points += 1
                else:
                    form_string.append('L')
        
        # Calculate form score (0-100)
        max_points = window * 3
        form_score = (points / max_points * 100) if max_points > 0 else 0.0
        
        return {
            'form_string': ''.join(form_string),
            'points': points,
            'form_score': form_score,
            'matches_analyzed': len(form_string)
        }
    
    def calculate_expected_goals(
        self,
        shots: int,
        shots_on_target: int,
        big_chances: int = 0
    ) -> float:
        """
        Calculate Expected Goals (xG) - simplified version.
        
        Args:
            shots: Total shots
            shots_on_target: Shots on target
            big_chances: Number of big chances
            
        Returns:
            Expected goals value
        """
        # Simplified xG calculation
        # Real xG uses shot location, type, etc.
        base_xg = shots_on_target * 0.3  # 30% conversion for shots on target
        chance_xg = big_chances * 0.5     # 50% for big chances
        
        return round(base_xg + chance_xg, 2)
    
    def calculate_possession_value(
        self,
        possession_pct: float,
        shots: int,
        passes_completed: int,
        total_passes: int
    ) -> Dict[str, float]:
        """
        Calculate possession effectiveness metrics.
        
        Args:
            possession_pct: Possession percentage
            shots: Total shots
            passes_completed: Completed passes
            total_passes: Total passes attempted
            
        Returns:
            Dictionary with possession metrics
        """
        pass_accuracy = (passes_completed / total_passes * 100) if total_passes > 0 else 0.0
        shots_per_possession = (shots / possession_pct * 100) if possession_pct > 0 else 0.0
        
        # Possession efficiency score (0-100)
        efficiency = (pass_accuracy * 0.4 + shots_per_possession * 0.6)
        
        return {
            'pass_accuracy': round(pass_accuracy, 1),
            'shots_per_possession': round(shots_per_possession, 2),
            'possession_efficiency': round(min(efficiency, 100), 1)
        }
    
    def calculate_defensive_metrics(
        self,
        tackles: int,
        interceptions: int,
        clearances: int,
        blocks: int,
        goals_conceded: int,
        shots_faced: int
    ) -> Dict[str, Any]:
        """
        Calculate defensive performance metrics.
        
        Args:
            tackles: Successful tackles
            interceptions: Interceptions made
            clearances: Clearances made
            blocks: Shots blocked
            goals_conceded: Goals conceded
            shots_faced: Total shots faced
            
        Returns:
            Dictionary with defensive metrics
        """
        # Defensive actions
        total_defensive_actions = tackles + interceptions + clearances + blocks
        
        # Save percentage
        save_pct = ((shots_faced - goals_conceded) / shots_faced * 100) if shots_faced > 0 else 0.0
        
        # Defensive rating (0-100)
        defensive_rating = min(
            (total_defensive_actions * 2) + (save_pct * 0.5),
            100
        )
        
        return {
            'total_defensive_actions': total_defensive_actions,
            'tackles': tackles,
            'interceptions': interceptions,
            'clearances': clearances,
            'blocks': blocks,
            'save_percentage': round(save_pct, 1),
            'defensive_rating': round(defensive_rating, 1)
        }
    
    def calculate_attacking_metrics(
        self,
        goals: int,
        shots: int,
        shots_on_target: int,
        key_passes: int,
        dribbles_completed: int,
        crosses_completed: int
    ) -> Dict[str, Any]:
        """
        Calculate attacking performance metrics.
        
        Args:
            goals: Goals scored
            shots: Total shots
            shots_on_target: Shots on target
            key_passes: Key passes made
            dribbles_completed: Successful dribbles
            crosses_completed: Successful crosses
            
        Returns:
            Dictionary with attacking metrics
        """
        # Shot accuracy
        shot_accuracy = (shots_on_target / shots * 100) if shots > 0 else 0.0
        
        # Conversion rate
        conversion_rate = (goals / shots * 100) if shots > 0 else 0.0
        
        # Attacking threat score
        threat_score = (
            goals * 10 +
            shots_on_target * 3 +
            key_passes * 2 +
            dribbles_completed * 1.5 +
            crosses_completed * 1
        )
        
        return {
            'goals': goals,
            'shots': shots,
            'shots_on_target': shots_on_target,
            'shot_accuracy': round(shot_accuracy, 1),
            'conversion_rate': round(conversion_rate, 1),
            'key_passes': key_passes,
            'dribbles_completed': dribbles_completed,
            'crosses_completed': crosses_completed,
            'attacking_threat': round(threat_score, 1)
        }
    
    def calculate_momentum(
        self,
        recent_events: List[Dict[str, Any]],
        time_window: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate match momentum based on recent events.
        
        Args:
            recent_events: List of recent match events
            time_window: Time window in minutes
            
        Returns:
            Dictionary with momentum metrics
        """
        if not recent_events:
            return {
                'momentum_score': 50.0,  # Neutral
                'momentum_direction': 'neutral',
                'key_events': []
            }
        
        # Weight different events
        event_weights = {
            'goal': 15,
            'shot_on_target': 3,
            'shot_off_target': 1,
            'corner': 2,
            'free_kick': 2,
            'yellow_card': -2,
            'red_card': -10
        }
        
        home_momentum = 50.0
        away_momentum = 50.0
        
        for event in recent_events[-time_window:]:
            event_type = event.get('type', '')
            team = event.get('team', '')
            weight = event_weights.get(event_type, 0)
            
            if team == 'home':
                home_momentum += weight
            else:
                away_momentum += weight
        
        # Normalize to 0-100 scale
        total = home_momentum + away_momentum
        home_pct = (home_momentum / total * 100) if total > 0 else 50.0
        
        # Determine direction
        if home_pct > 60:
            direction = 'home_dominant'
        elif home_pct < 40:
            direction = 'away_dominant'
        else:
            direction = 'balanced'
        
        return {
            'momentum_score': round(home_pct, 1),
            'momentum_direction': direction,
            'home_momentum': round(home_momentum, 1),
            'away_momentum': round(away_momentum, 1)
        }
    
    def predict_match_outcome(
        self,
        home_team_stats: Dict[str, Any],
        away_team_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict match outcome based on team statistics.
        
        Args:
            home_team_stats: Home team statistics
            away_team_stats: Away team statistics
            
        Returns:
            Dictionary with prediction probabilities
        """
        # Extract key metrics
        home_form = home_team_stats.get('form_score', 50)
        away_form = away_team_stats.get('form_score', 50)
        
        home_goals_avg = home_team_stats.get('avg_goals_scored', 1.5)
        away_goals_avg = away_team_stats.get('avg_goals_scored', 1.5)
        
        # Simple prediction model
        # Home advantage: +10%
        home_advantage = 10
        
        # Calculate win probabilities
        home_strength = home_form + (home_goals_avg * 10) + home_advantage
        away_strength = away_form + (away_goals_avg * 10)
        
        total_strength = home_strength + away_strength
        
        home_win_prob = (home_strength / total_strength * 100) if total_strength > 0 else 33.3
        away_win_prob = (away_strength / total_strength * 100) if total_strength > 0 else 33.3
        draw_prob = 100 - home_win_prob - away_win_prob
        
        # Adjust for more realistic probabilities
        draw_prob = max(draw_prob, 20)  # Minimum 20% draw probability
        remaining = 100 - draw_prob
        home_win_prob = (home_win_prob / (home_win_prob + away_win_prob)) * remaining
        away_win_prob = remaining - home_win_prob
        
        # Predicted score
        predicted_home_goals = round(home_goals_avg * (home_win_prob / 50), 1)
        predicted_away_goals = round(away_goals_avg * (away_win_prob / 50), 1)
        
        return {
            'home_win_probability': round(home_win_prob, 1),
            'draw_probability': round(draw_prob, 1),
            'away_win_probability': round(away_win_prob, 1),
            'predicted_score': f"{predicted_home_goals:.1f} - {predicted_away_goals:.1f}",
            'confidence': 'medium'  # Could be calculated based on data quality
        }
    
    def calculate_player_rating(
        self,
        goals: int = 0,
        assists: int = 0,
        shots: int = 0,
        passes_completed: int = 0,
        total_passes: int = 0,
        tackles: int = 0,
        interceptions: int = 0,
        dribbles: int = 0,
        minutes_played: int = 90
    ) -> float:
        """
        Calculate player performance rating (0-10 scale).
        
        Args:
            goals: Goals scored
            assists: Assists made
            shots: Total shots
            passes_completed: Completed passes
            total_passes: Total passes attempted
            tackles: Successful tackles
            interceptions: Interceptions made
            dribbles: Successful dribbles
            minutes_played: Minutes played
            
        Returns:
            Player rating (0-10)
        """
        # Base rating
        rating = 6.0
        
        # Goal contributions
        rating += goals * 1.0
        rating += assists * 0.7
        
        # Passing
        pass_accuracy = (passes_completed / total_passes) if total_passes > 0 else 0.5
        rating += (pass_accuracy - 0.7) * 2  # Bonus/penalty for pass accuracy
        
        # Attacking actions
        rating += shots * 0.1
        rating += dribbles * 0.15
        
        # Defensive actions
        rating += tackles * 0.1
        rating += interceptions * 0.1
        
        # Adjust for minutes played
        if minutes_played < 90:
            rating *= (minutes_played / 90)
        
        # Cap rating between 0 and 10
        rating = max(0, min(10, rating))
        
        return round(rating, 1)


if __name__ == "__main__":
    # Test the metrics calculator
    logging.basicConfig(level=logging.INFO)
    
    calc = MetricsCalculator()
    
    print("\n" + "="*70)
    print("Metrics Calculator - Test Suite")
    print("="*70)
    
    # Test 1: Form calculation
    print("\nTest 1: Team Form")
    form = calc.calculate_form(pd.DataFrame(), "Brazil", 5)
    print(f"Form: {form}")
    
    # Test 2: Expected Goals
    print("\nTest 2: Expected Goals (xG)")
    xg = calc.calculate_expected_goals(shots=15, shots_on_target=6, big_chances=2)
    print(f"xG: {xg}")
    
    # Test 3: Match Prediction
    print("\nTest 3: Match Outcome Prediction")
    home_stats = {'form_score': 70, 'avg_goals_scored': 2.0}
    away_stats = {'form_score': 50, 'avg_goals_scored': 1.5}
    prediction = calc.predict_match_outcome(home_stats, away_stats)
    print(f"Prediction: {prediction}")
    
    # Test 4: Player Rating
    print("\nTest 4: Player Rating")
    rating = calc.calculate_player_rating(
        goals=1,
        assists=1,
        shots=4,
        passes_completed=45,
        total_passes=50,
        tackles=3,
        interceptions=2,
        dribbles=5
    )
    print(f"Player Rating: {rating}/10")
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)

# Made with Bob
