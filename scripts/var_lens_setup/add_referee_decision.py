#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Referee Decision Script
============================

Add referee decisions and VAR reviews to match database for VAR-Lens agent.

Usage:
    python scripts/var_lens_setup/add_referee_decision.py

This script provides an interactive interface to add referee decisions.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DECISIONS_PATH = PROJECT_ROOT / "data" / "referee_decisions"
DECISIONS_PATH.mkdir(parents=True, exist_ok=True)


def add_referee_decision(
    match_id: str,
    minute: int,
    event_type: str,
    description: str,
    var_decision: Optional[Dict] = None,
    match_info: Optional[Dict] = None
) -> bool:
    """
    Add a referee decision with optional VAR review details.
    
    Args:
        match_id: Match identifier (e.g., "WC_2026-06-15_BRAZIL_ARGENTINA")
        minute: Minute of the decision
        event_type: Type of decision (goal_disallowed, penalty_given, red_card, etc.)
        description: Brief description of the decision
        var_decision: VAR review details (optional)
        match_info: Match metadata (optional, only needed for first decision)
        
    Returns:
        True if successful
    """
    event_file = DECISIONS_PATH / f"{match_id}.json"
    
    # Load existing events or create new
    if event_file.exists():
        with open(event_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "match_id": match_id,
            "match_info": match_info or {},
            "events": []
        }
    
    # Create event
    event = {
        "minute": minute,
        "type": event_type,
        "description": description,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add VAR decision if provided
    if var_decision:
        event["var_decision"] = var_decision
    
    # Add event
    data["events"].append(event)
    
    # Sort events by minute
    data["events"].sort(key=lambda x: x["minute"])
    
    # Save
    with open(event_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True


def interactive_add():
    """Interactive interface to add referee decisions"""
    print("=" * 70)
    print("⚖️ Add Referee Decision - Interactive Mode")
    print("=" * 70)
    print()
    
    # Get match ID
    print("📋 Match ID (e.g., WC_2026-06-15_BRAZIL_ARGENTINA):")
    match_id = input("> ").strip()
    
    if not match_id:
        print("❌ Match ID is required")
        return
    
    # Check if match exists
    event_file = DECISIONS_PATH / f"{match_id}.json"
    is_new_match = not event_file.exists()
    
    if is_new_match:
        print("\n📝 New match! Please provide match info:")
        home_team = input("  Home team: ").strip()
        away_team = input("  Away team: ").strip()
        date = input("  Date (YYYY-MM-DD): ").strip()
        tournament = input("  Tournament: ").strip()
        
        match_info = {
            "home_team": home_team,
            "away_team": away_team,
            "date": date,
            "tournament": tournament
        }
    else:
        match_info = None
        print(f"\n✅ Adding decision to existing match: {match_id}")
    
    print()
    print("=" * 70)
    print("Decision Details")
    print("=" * 70)
    
    # Get event details
    minute = int(input("\n⏱️  Minute: ").strip())
    
    print("\n📌 Decision Type:")
    print("  1. goal_disallowed")
    print("  2. penalty_given")
    print("  3. penalty_not_given")
    print("  4. red_card")
    print("  5. offside")
    print("  6. handball")
    print("  7. foul")
    print("  8. other")
    event_type_choice = input("Select (1-8): ").strip()
    
    event_types = {
        "1": "goal_disallowed",
        "2": "penalty_given",
        "3": "penalty_not_given",
        "4": "red_card",
        "5": "offside",
        "6": "handball",
        "7": "foul",
        "8": "other"
    }
    event_type = event_types.get(event_type_choice, "other")
    
    description = input("\n📝 Description: ").strip()
    
    # VAR decision
    print("\n🎥 Was VAR involved? (y/n): ", end="")
    has_var = input().strip().lower() == 'y'
    
    var_decision = None
    if has_var:
        print("\n📋 VAR Decision Details:")
        reason = input("  Reason: ").strip()
        review_duration = input("  Review duration (e.g., 2:15): ").strip()
        referee = input("  Referee: ").strip()
        details = input("  Details: ").strip()
        final_decision = input("  Final decision: ").strip()
        
        var_decision = {
            "reason": reason,
            "review_duration": review_duration,
            "referee": referee,
            "details": details,
            "final_decision": final_decision
        }
    
    # Add decision
    print()
    print("=" * 70)
    print("Adding decision...")
    
    success = add_referee_decision(
        match_id=match_id,
        minute=minute,
        event_type=event_type,
        description=description,
        var_decision=var_decision,
        match_info=match_info
    )
    
    if success:
        print("✅ Decision added successfully!")
        print(f"📁 File: {event_file}")
        print()
        print("🎯 You can now query this decision in VAR-Lens agent:")
        print(f'   "What happened at minute {minute} in {match_id}?"')
    else:
        print("❌ Failed to add decision")
    
    print("=" * 70)


def example_usage():
    """Show example usage"""
    print("=" * 70)
    print("📚 Example: Adding a Referee Decision")
    print("=" * 70)
    print()
    
    example_code = '''
from scripts.var_lens_setup.add_referee_decision import add_referee_decision

# Add a goal disallowed for offside
add_referee_decision(
    match_id="WC_2026-06-15_BRAZIL_ARGENTINA",
    minute=67,
    event_type="goal_disallowed",
    description="Neymar goal cancelled for offside",
    var_decision={
        "reason": "offside",
        "review_duration": "2:15",
        "referee": "Pierluigi Collina",
        "details": "Neymar was 0.5m ahead of last defender when ball was played",
        "camera_angles": ["main", "behind_goal", "var_line"],
        "final_decision": "goal_cancelled"
    },
    match_info={
        "home_team": "Brazil",
        "away_team": "Argentina",
        "date": "2026-06-15",
        "tournament": "FIFA World Cup 2026"
    }
)
'''
    print(example_code)
    print()


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_usage()
    else:
        interactive_add()


if __name__ == "__main__":
    main()

# Made with Bob