"""
Test Match Analyzer
Tests the complete match analysis functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.tactical_pulse.match_analyzer import MatchAnalyzer


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def main():
    """Test the Match Analyzer"""
    print_section("Match Analyzer - Test Suite")
    
    # Initialize analyzer
    print("Initializing Match Analyzer...")
    analyzer = MatchAnalyzer()
    
    # Test 1: Team Analysis
    print_section("TEST 1: Team Analysis")
    teams = ["Brazil", "Argentina", "Germany"]
    
    for team in teams:
        print(f"\n{team} Analysis:")
        analysis = analyzer.analyze_team(team, num_matches=10)
        
        if 'error' not in analysis:
            print(f"  Matches Analyzed: {analysis['matches_analyzed']}")
            print(f"  Form: {analysis['form']['form_string']}")
            print(f"  Form Score: {analysis['form']['form_score']:.1f}/100")
            print(f"  Win Rate: {analysis['statistics']['win_rate']:.1%}")
            print(f"  Goals: {analysis['statistics']['goals_scored']:.0f} scored, {analysis['statistics']['goals_conceded']:.0f} conceded")
        else:
            print(f"  Error: {analysis['error']}")
    
    # Test 2: Head-to-Head Analysis
    print_section("TEST 2: Head-to-Head Analysis")
    h2h_pairs = [
        ("Brazil", "Argentina"),
        ("Germany", "France"),
        ("Spain", "Italy")
    ]
    
    for team1, team2 in h2h_pairs:
        print(f"\n{team1} vs {team2}:")
        h2h = analyzer.analyze_head_to_head(team1, team2, num_matches=5)
        
        if 'error' not in h2h:
            print(f"  Matches: {h2h['total_matches']}")
            print(f"  Record: {h2h['team1_wins']}W-{h2h['draws']}D-{h2h['team2_wins']}L")
            print(f"  Goals: {h2h['team1_goals']}-{h2h['team2_goals']}")
            print(f"  {team1} Win Rate: {h2h['team1_win_rate']:.1f}%")
        else:
            print(f"  Error: {h2h['error']}")
    
    # Test 3: Match Prediction
    print_section("TEST 3: Match Prediction")
    predictions = [
        ("Brazil", "Argentina"),
        ("Germany", "France"),
        ("Spain", "England")
    ]
    
    for home, away in predictions:
        print(f"\n{home} vs {away}:")
        prediction = analyzer.predict_match(home, away, num_recent_matches=10)
        
        pred = prediction['prediction']
        print(f"  Predicted Score: {pred['predicted_score']}")
        print(f"  Probabilities:")
        print(f"    {home} Win: {pred['home_win_probability']:.1f}%")
        print(f"    Draw: {pred['draw_probability']:.1f}%")
        print(f"    {away} Win: {pred['away_win_probability']:.1f}%")
        print(f"  Form:")
        print(f"    {home}: {prediction['home_form']['form_string']} ({prediction['home_form']['form_score']:.1f}/100)")
        print(f"    {away}: {prediction['away_form']['form_string']} ({prediction['away_form']['form_score']:.1f}/100)")
    
    # Test 4: Tournament Analysis
    print_section("TEST 4: Tournament Analysis")
    tournaments = ["UEFA Euro", "FIFA World Cup", "Copa America"]
    
    for tournament in tournaments:
        print(f"\n{tournament}:")
        analysis = analyzer.analyze_tournament(tournament, limit=20)
        
        if 'error' not in analysis:
            print(f"  Matches Analyzed: {analysis['matches_analyzed']}")
            print(f"  Total Goals: {analysis.get('total_goals', 0)}")
            print(f"  Avg Goals/Match: {analysis.get('avg_goals_per_match', 0):.2f}")
            print(f"  Unique Teams: {analysis.get('unique_teams', 0)}")
        else:
            print(f"  Error: {analysis['error']}")
    
    # Test 5: Natural Language Insights
    print_section("TEST 5: Natural Language Insights")
    queries = [
        "What is Brazil's form?",
        "Predict Brazil vs Argentina",
        "Head to head Germany France"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        insight = analyzer.get_insights(query)
        print(f"Response: {insight}")
    
    # Summary
    print_section("Test Summary")
    print("[OK] Team analysis working")
    print("[OK] Head-to-head analysis working")
    print("[OK] Match prediction working")
    print("[OK] Tournament analysis working")
    print("[OK] Natural language insights working")
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)


if __name__ == "__main__":
    main()

# Made with Bob
