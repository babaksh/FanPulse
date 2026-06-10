"""
Match Data Loader for Tactical Pulse Agent
Loads and preprocesses match data from various sources
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class MatchDataLoader:
    """
    Loads and manages match data from CSV files and other sources.
    Provides access to historical match results, team statistics, and player data.
    """
    
    def __init__(self, data_path: str = "data/match_data/results.csv"):
        """
        Initialize the Match Data Loader.
        
        Args:
            data_path: Path to the match results CSV file
        """
        self.data_path = Path(data_path)
        self.matches_df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self):
        """Load match data from CSV file"""
        try:
            logger.info(f"Loading match data from: {self.data_path}")
            self.matches_df = pd.read_csv(self.data_path)
            
            # Convert date column to datetime
            if 'date' in self.matches_df.columns:
                self.matches_df['date'] = pd.to_datetime(self.matches_df['date'])
            
            if self.matches_df is not None:
                logger.info(f"Loaded {len(self.matches_df)} matches")
            else:
                logger.info("Loaded 0 matches")
            logger.info(f"Columns: {list(self.matches_df.columns)}")
            
        except FileNotFoundError:
            logger.error(f"Match data file not found: {self.data_path}")
            self.matches_df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading match data: {e}")
            self.matches_df = pd.DataFrame()
    
    def get_match_by_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific match by ID.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Dictionary with match details or None if not found
        """
        if self.matches_df is None or self.matches_df.empty:
            return None
        
        # Assuming the dataframe has an index or ID column
        if match_id < len(self.matches_df):
            match = self.matches_df.iloc[match_id]
            return match.to_dict()
        
        return None
    
    def get_team_matches(
        self,
        team_name: str,
        limit: int = 10,
        home_only: bool = False,
        away_only: bool = False
    ) -> pd.DataFrame:
        """
        Get matches for a specific team.
        
        Args:
            team_name: Name of the team
            limit: Maximum number of matches to return
            home_only: Only return home matches
            away_only: Only return away matches
            
        Returns:
            DataFrame with team's matches
        """
        if self.matches_df is None or self.matches_df.empty:
            return pd.DataFrame()
        
        # Filter matches where team played
        if home_only:
            matches = self.matches_df[
                self.matches_df['home_team'].str.contains(team_name, case=False, na=False)
            ]
        elif away_only:
            matches = self.matches_df[
                self.matches_df['away_team'].str.contains(team_name, case=False, na=False)
            ]
        else:
            matches = self.matches_df[
                (self.matches_df['home_team'].str.contains(team_name, case=False, na=False)) |
                (self.matches_df['away_team'].str.contains(team_name, case=False, na=False))
            ]
        
        # Sort by date (most recent first) and limit
        if 'date' in matches.columns:
            matches = matches.sort_values('date', ascending=False)
        
        return matches.head(limit)
    
    def get_head_to_head(
        self,
        team1: str,
        team2: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get head-to-head matches between two teams.
        
        Args:
            team1: First team name
            team2: Second team name
            limit: Maximum number of matches to return
            
        Returns:
            DataFrame with head-to-head matches
        """
        if self.matches_df is None or self.matches_df.empty:
            return pd.DataFrame()
        
        # Find matches where both teams played against each other
        matches = self.matches_df[
            ((self.matches_df['home_team'].str.contains(team1, case=False, na=False)) &
             (self.matches_df['away_team'].str.contains(team2, case=False, na=False))) |
            ((self.matches_df['home_team'].str.contains(team2, case=False, na=False)) &
             (self.matches_df['away_team'].str.contains(team1, case=False, na=False)))
        ]
        
        # Sort by date (most recent first) and limit
        if 'date' in matches.columns:
            matches = matches.sort_values('date', ascending=False)
        
        return matches.head(limit)
    
    def get_team_stats(self, team_name: str, last_n_matches: int = 10) -> Dict[str, Any]:
        """
        Calculate statistics for a team based on recent matches.
        
        Args:
            team_name: Name of the team
            last_n_matches: Number of recent matches to analyze
            
        Returns:
            Dictionary with team statistics
        """
        matches = self.get_team_matches(team_name, limit=last_n_matches)
        
        if matches.empty:
            return {
                'team': team_name,
                'matches_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'win_rate': 0.0
            }
        
        stats = {
            'team': team_name,
            'matches_played': len(matches),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_scored': 0,
            'goals_conceded': 0
        }
        
        for _, match in matches.iterrows():
            is_home = team_name.lower() in str(match.get('home_team', '')).lower()
            
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
            if is_home:
                stats['goals_scored'] += home_score
                stats['goals_conceded'] += away_score
                
                if home_score > away_score:
                    stats['wins'] += 1
                elif home_score == away_score:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
            else:
                stats['goals_scored'] += away_score
                stats['goals_conceded'] += home_score
                
                if away_score > home_score:
                    stats['wins'] += 1
                elif away_score == home_score:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
        
        # Calculate derived stats
        stats['win_rate'] = stats['wins'] / stats['matches_played'] if stats['matches_played'] > 0 else 0.0
        stats['avg_goals_scored'] = stats['goals_scored'] / stats['matches_played'] if stats['matches_played'] > 0 else 0.0
        stats['avg_goals_conceded'] = stats['goals_conceded'] / stats['matches_played'] if stats['matches_played'] > 0 else 0.0
        stats['goal_difference'] = stats['goals_scored'] - stats['goals_conceded']
        
        return stats
    
    def get_tournament_matches(
        self,
        tournament: str,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get matches from a specific tournament.
        
        Args:
            tournament: Tournament name (e.g., "FIFA World Cup")
            limit: Maximum number of matches to return
            
        Returns:
            DataFrame with tournament matches
        """
        if self.matches_df is None or self.matches_df.empty:
            return pd.DataFrame()
        
        # Filter by tournament
        if 'tournament' in self.matches_df.columns:
            matches = self.matches_df[
                self.matches_df['tournament'].str.contains(tournament, case=False, na=False)
            ]
        else:
            return pd.DataFrame()
        
        # Sort by date and limit
        if 'date' in matches.columns:
            matches = matches.sort_values('date', ascending=False)
        
        if limit:
            matches = matches.head(limit)
        
        return matches
    
    def search_matches(
        self,
        query: str,
        search_fields: List[str] = ['home_team', 'away_team', 'tournament'],
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Search for matches using a query string.
        
        Args:
            query: Search query
            search_fields: Fields to search in
            limit: Maximum number of results
            
        Returns:
            DataFrame with matching matches
        """
        if self.matches_df is None or self.matches_df.empty:
            return pd.DataFrame()
        
        # Create a mask for matches that contain the query in any search field
        mask = pd.Series([False] * len(self.matches_df))
        
        for field in search_fields:
            if field in self.matches_df.columns:
                mask |= self.matches_df[field].str.contains(query, case=False, na=False)
        
        matches = self.matches_df[mask]
        
        # Sort by date and limit
        if 'date' in matches.columns:
            matches = matches.sort_values('date', ascending=False)
        
        return matches.head(limit)
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        if self.matches_df is None or self.matches_df.empty:
            return {
                'total_matches': 0,
                'columns': [],
                'date_range': None
            }
        
        info = {
            'total_matches': len(self.matches_df),
            'columns': list(self.matches_df.columns),
            'memory_usage': f"{self.matches_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }
        
        # Add date range if available
        if 'date' in self.matches_df.columns:
            info['date_range'] = {
                'earliest': str(self.matches_df['date'].min()),
                'latest': str(self.matches_df['date'].max())
            }
        
        # Add unique teams count
        if 'home_team' in self.matches_df.columns and 'away_team' in self.matches_df.columns:
            all_teams = set(self.matches_df['home_team'].unique()) | set(self.matches_df['away_team'].unique())
            info['unique_teams'] = len(all_teams)
        
        # Add tournaments count
        if 'tournament' in self.matches_df.columns:
            info['unique_tournaments'] = self.matches_df['tournament'].nunique()
        
        return info


if __name__ == "__main__":
    # Test the data loader
    logging.basicConfig(level=logging.INFO)
    
    loader = MatchDataLoader()
    
    # Print dataset info
    info = loader.get_dataset_info()
    print("\n" + "="*70)
    print("Dataset Information")
    print("="*70)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Test team stats
    print("\n" + "="*70)
    print("Brazil Statistics (Last 10 Matches)")
    print("="*70)
    stats = loader.get_team_stats("Brazil", last_n_matches=10)
    for key, value in stats.items():
        print(f"{key}: {value}")

# Made with Bob
