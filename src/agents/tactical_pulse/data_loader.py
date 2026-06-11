"""
Match Data Loader for Tactical Pulse Agent
Loads and preprocesses match data from various sources
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, cast
import logging
from datetime import datetime
import json

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
    
    def get_match_by_index(self, match_index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific match by DataFrame index.
        
        Args:
            match_index: Match index in DataFrame
            
        Returns:
            Dictionary with match details or None if not found
        """
        if self.matches_df is None or self.matches_df.empty:
            return None
        
        # Get match by index
        if match_index < len(self.matches_df):
            match = self.matches_df.iloc[match_index]
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
            matches = cast(pd.DataFrame, matches.sort_values(by='date', ascending=False))  # type: ignore[call-overload]
        
        return cast(pd.DataFrame, matches.head(limit))
    
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
            matches = cast(pd.DataFrame, matches.sort_values(by='date', ascending=False))  # type: ignore[call-overload]
        
        return cast(pd.DataFrame, matches.head(limit))
    
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
            
            home_score = int(match.get('home_score', 0) or 0)
            away_score = int(match.get('away_score', 0) or 0)
            
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
            matches = cast(pd.DataFrame, matches.sort_values(by='date', ascending=False))  # type: ignore[call-overload]
        
        if limit:
            matches = cast(pd.DataFrame, matches.head(limit))
        
        return cast(pd.DataFrame, matches)
    
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
            matches = cast(pd.DataFrame, matches.sort_values(by='date', ascending=False))  # type: ignore[call-overload]
        
        return cast(pd.DataFrame, matches.head(limit))
    
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
    
    def add_match_data(
        self,
        match_data: Dict[str, Any],
        save_to_csv: bool = True
    ) -> Dict[str, Any]:
        """
        Add new match data dynamically to the dataset.
        This allows real-time updates during matches or adding historical data.
        
        Args:
            match_data: Dictionary containing match information with keys:
                - date: Match date (str or datetime)
                - home_team: Home team name
                - away_team: Away team name
                - home_score: Home team score
                - away_score: Away team score
                - tournament: Tournament name (optional)
                - city: City where match was played (optional)
                - country: Country where match was played (optional)
                - neutral: Whether match was on neutral ground (optional)
                - Additional fields as needed
            save_to_csv: Whether to save updated data to CSV file
            
        Returns:
            Dictionary with operation results
        """
        logger.info(f"Adding match data: {match_data.get('home_team')} vs {match_data.get('away_team')}")
        
        try:
            # Validate required fields
            required_fields = ['date', 'home_team', 'away_team', 'home_score', 'away_score']
            missing_fields = [f for f in required_fields if f not in match_data]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {missing_fields}",
                    "match_added": False
                }
            
            # Convert date to datetime if it's a string
            if isinstance(match_data['date'], str):
                match_data['date'] = pd.to_datetime(match_data['date'])
            
            # Create new row as DataFrame
            new_match = pd.DataFrame([match_data])
            
            # Append to existing data
            if self.matches_df is None or self.matches_df.empty:
                self.matches_df = new_match
            else:
                self.matches_df = pd.concat([self.matches_df, new_match], ignore_index=True)
            
            # Save to CSV if requested
            if save_to_csv:
                self.matches_df.to_csv(self.data_path, index=False)
                logger.info(f"Match data saved to {self.data_path}")
            
            return {
                "success": True,
                "match_added": True,
                "total_matches": len(self.matches_df),
                "match_info": {
                    "date": str(match_data['date']),
                    "home_team": match_data['home_team'],
                    "away_team": match_data['away_team'],
                    "score": f"{match_data['home_score']}-{match_data['away_score']}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding match data: {e}")
            return {
                "success": False,
                "error": str(e),
                "match_added": False
            }
    
    def add_match_batch(
        self,
        matches_data: List[Dict[str, Any]],
        save_to_csv: bool = True
    ) -> Dict[str, Any]:
        """
        Add multiple matches at once.
        
        Args:
            matches_data: List of match dictionaries
            save_to_csv: Whether to save after adding all matches
            
        Returns:
            Dictionary with batch operation results
        """
        logger.info(f"Adding batch of {len(matches_data)} matches")
        
        results = {
            "success": True,
            "matches_added": 0,
            "matches_failed": 0,
            "errors": []
        }
        
        for match_data in matches_data:
            result = self.add_match_data(match_data, save_to_csv=False)
            
            if result["success"]:
                results["matches_added"] += 1
            else:
                results["matches_failed"] += 1
                results["errors"].append({
                    "match": f"{match_data.get('home_team')} vs {match_data.get('away_team')}",
                    "error": result.get("error")
                })
        
        # Save once after all matches are added
        if save_to_csv and results["matches_added"] > 0:
            try:
                self.matches_df.to_csv(self.data_path, index=False)
                logger.info(f"Batch data saved to {self.data_path}")
            except Exception as e:
                results["success"] = False
                results["errors"].append({"save_error": str(e)})
        
        results["total_matches"] = len(self.matches_df) if self.matches_df is not None else 0
        
        return results
    
    def update_match_data(
        self,
        match_id: Optional[str] = None,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        date: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
        save_to_csv: bool = True
    ) -> Dict[str, Any]:
        """
        Update existing match data.
        Can identify match by match_id or by team names and date.
        
        Args:
            match_id: Unique match identifier (if available)
            home_team: Home team name
            away_team: Away team name
            date: Match date
            updates: Dictionary of fields to update
            save_to_csv: Whether to save changes
            
        Returns:
            Dictionary with update results
        """
        if self.matches_df is None or self.matches_df.empty:
            return {
                "success": False,
                "error": "No data loaded",
                "matches_updated": 0
            }
        
        if updates is None:
            return {
                "success": False,
                "error": "No updates provided",
                "matches_updated": 0
            }
        
        try:
            # Find match
            if match_id and 'match_id' in self.matches_df.columns:
                mask = self.matches_df['match_id'] == match_id
            elif home_team and away_team and date:
                mask = (
                    (self.matches_df['home_team'] == home_team) &
                    (self.matches_df['away_team'] == away_team) &
                    (self.matches_df['date'] == pd.to_datetime(date))
                )
            else:
                return {
                    "success": False,
                    "error": "Insufficient match identification parameters",
                    "matches_updated": 0
                }
            
            # Update fields
            matches_found = mask.sum()
            
            if matches_found == 0:
                return {
                    "success": False,
                    "error": "Match not found",
                    "matches_updated": 0
                }
            
            for field, value in updates.items():
                self.matches_df.loc[mask, field] = value
            
            # Save if requested
            if save_to_csv:
                self.matches_df.to_csv(self.data_path, index=False)
            
            return {
                "success": True,
                "matches_updated": matches_found,
                "updated_fields": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating match data: {e}")
            return {
                "success": False,
                "error": str(e),
                "matches_updated": 0
            }
    
    def get_match_by_id(
        self,
        match_id: Optional[str] = None,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific match by ID or team names and date.
        
        Args:
            match_id: Unique match identifier
            home_team: Home team name
            away_team: Away team name
            date: Match date
            
        Returns:
            Match data as dictionary or None if not found
        """
        if self.matches_df is None or self.matches_df.empty:
            return None
        
        try:
            # Find match
            if match_id and 'match_id' in self.matches_df.columns:
                mask = self.matches_df['match_id'] == match_id
            elif home_team and away_team and date:
                mask = (
                    (self.matches_df['home_team'] == home_team) &
                    (self.matches_df['away_team'] == away_team) &
                    (self.matches_df['date'] == pd.to_datetime(date))
                )
            else:
                return None
            
            matches = self.matches_df[mask]
            
            if len(matches) == 0:
                return None
            
            # Return first match as dictionary
            return matches.iloc[0].to_dict()
            
        except Exception as e:
            logger.error(f"Error getting match: {e}")
            return None


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
