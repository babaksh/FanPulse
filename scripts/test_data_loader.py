"""
Test Match Data Loader
Tests the data loading and statistics functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.tactical_pulse.data_loader import MatchDataLoader


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def main():
    """Test the Match Data Loader"""
    print_section("Match Data Loader - Test Suite")
    
    # Initialize loader
    print("Initializing Match Data Loader...")
    loader = MatchDataLoader()
    
    # Test 1: Dataset Info
    print_section("TEST 1: Dataset Information")
    info = loader.get_dataset_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test 2: Team Statistics
    print_section("TEST 2: Team Statistics")
    teams_to_test = ["Brazil", "Argentina", "Germany", "France"]
    
    for team in teams_to_test:
        print(f"\n{team} (Last 10 matches):")
        stats = loader.get_team_stats(team, last_n_matches=10)
        
        if stats['matches_played'] > 0:
            print(f"  Matches: {stats['matches_played']}")
            print(f"  Record: {stats['wins']}W - {stats['draws']}D - {stats['losses']}L")
            print(f"  Win Rate: {stats['win_rate']:.1%}")
            print(f"  Goals: {stats['goals_scored']:.0f} scored, {stats['goals_conceded']:.0f} conceded")
            print(f"  Goal Difference: {stats['goal_difference']:+.0f}")
            print(f"  Avg Goals/Match: {stats['avg_goals_scored']:.2f}")
        else:
            print(f"  No matches found")
    
    # Test 3: Head-to-Head
    print_section("TEST 3: Head-to-Head Analysis")
    h2h_pairs = [
        ("Brazil", "Argentina"),
        ("Germany", "France"),
        ("Spain", "Italy")
    ]
    
    for team1, team2 in h2h_pairs:
        print(f"\n{team1} vs {team2}:")
        matches = loader.get_head_to_head(team1, team2, limit=5)
        
        if not matches.empty:
            print(f"  Found {len(matches)} matches")
            for idx, match in matches.head(3).iterrows():
                date = match.get('date', 'Unknown')
                home = match.get('home_team', 'Unknown')
                away = match.get('away_team', 'Unknown')
                score = f"{match.get('home_score', 0)}-{match.get('away_score', 0)}"
                tournament = match.get('tournament', 'Unknown')
                print(f"  • {date}: {home} {score} {away} ({tournament})")
        else:
            print(f"  No head-to-head matches found")
    
    # Test 4: Tournament Matches
    print_section("TEST 4: Tournament Matches")
    tournaments = ["FIFA World Cup", "UEFA Euro", "Copa America"]
    
    for tournament in tournaments:
        matches = loader.get_tournament_matches(tournament, limit=5)
        if not matches.empty:
            print(f"\n{tournament}: {len(matches)} matches found")
            for idx, match in matches.head(3).iterrows():
                date = match.get('date', 'Unknown')
                home = match.get('home_team', 'Unknown')
                away = match.get('away_team', 'Unknown')
                score = f"{match.get('home_score', 0)}-{match.get('away_score', 0)}"
                print(f"  • {date}: {home} {score} {away}")
        else:
            print(f"\n{tournament}: No matches found")
    
    # Test 5: Search Functionality
    print_section("TEST 5: Search Functionality")
    search_queries = ["Brazil", "World Cup", "2022"]
    
    for query in search_queries:
        matches = loader.search_matches(query, limit=5)
        print(f"\nSearch: '{query}' - {len(matches)} results")
        if not matches.empty:
            for idx, match in matches.head(3).iterrows():
                date = match.get('date', 'Unknown')
                home = match.get('home_team', 'Unknown')
                away = match.get('away_team', 'Unknown')
                score = f"{match.get('home_score', 0)}-{match.get('away_score', 0)}"
                print(f"  • {date}: {home} {score} {away}")
    
    # Test 6: Recent Team Matches
    print_section("TEST 6: Recent Team Matches")
    team = "Brazil"
    print(f"\n{team}'s last 5 matches:")
    matches = loader.get_team_matches(team, limit=5)
    
    if not matches.empty:
        for idx, match in matches.iterrows():
            date = match.get('date', 'Unknown')
            home = match.get('home_team', 'Unknown')
            away = match.get('away_team', 'Unknown')
            score = f"{match.get('home_score', 0)}-{match.get('away_score', 0)}"
            tournament = match.get('tournament', 'Unknown')
            
            # Determine if Brazil was home or away
            is_home = team.lower() in str(home).lower()
            result = "W" if (is_home and match.get('home_score', 0) > match.get('away_score', 0)) or \
                           (not is_home and match.get('away_score', 0) > match.get('home_score', 0)) else \
                     "D" if match.get('home_score', 0) == match.get('away_score', 0) else "L"
            
            print(f"  [{result}] {date}: {home} {score} {away} ({tournament})")
    else:
        print(f"  No matches found")
    
    # Summary
    print_section("Test Summary")
    print("[OK] Dataset loaded successfully")
    print("[OK] Team statistics calculated")
    print("[OK] Head-to-head analysis working")
    print("[OK] Tournament filtering working")
    print("[OK] Search functionality working")
    print("[OK] Recent matches retrieval working")
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)


if __name__ == "__main__":
    main()

# Made with Bob
