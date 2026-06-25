"""
Query Referee Decisions Tool for LangFlow
Provides access to VAR-reviewable decisions from World Cup 2026 matches

Note: This database contains only the 4 types of decisions that can be reviewed by VAR
according to FIFA/IFAB protocol:
1. Goals (and offenses in the build-up)
2. Penalty decisions
3. Direct red card incidents
4. Mistaken identity

Yellow cards and other non-VAR incidents are NOT included in this database.
"""

from typing import Optional
from lfx.custom import Component
from lfx.io import Output
from lfx.field_typing import Tool
from langchain_core.tools import StructuredTool
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class QueryRefereeDecisionsTool(Component):
    display_name: str = "Query VAR-Reviewable Decisions"
    description: str = "Query VAR-reviewable decisions from World Cup 2026 matches (Goals, Penalties, Red Cards, Mistaken Identity)"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "gavel"
    name: str = "query_referee_decisions_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.events_path = self.project_root / "data" / "referee_decisions"
        
        # Create directory if it doesn't exist
        self.events_path.mkdir(parents=True, exist_ok=True)
    
    def build_tool(self) -> Tool:
        """Build the match events query tool"""
        
        def query_referee_decisions(
            match_id: Optional[str] = None,
            home_team: Optional[str] = None,
            away_team: Optional[str] = None,
            minute: Optional[int] = None,
            decision_type: Optional[str] = None,
            var_only: bool = False
        ) -> str:
            """Query VAR decisions from World Cup 2026 matches.
            
            DATABASE CONTAINS ONLY VAR-reviewed events:
            - Goals disallowed (offside, foul, handball)
            - Penalties awarded or not awarded via VAR
            - Red cards upgraded via VAR (cardUpgrade)
            - Mistaken identity corrections
            
            Every event in the database has a var_decision object. No yellow cards, no non-VAR incidents.
            
            Args:
                match_id: Match identifier (e.g., "WC_2026-06-21_BELGIUM_IRAN"). Optional if team names provided.
                home_team: Home team name (e.g., "Belgium"). Use with away_team to search by teams.
                away_team: Away team name (e.g., "Iran"). Use with home_team to search by teams.
                minute: Specific minute to query (optional, returns all events if not provided)
                decision_type: Filter by event type, e.g. "var_review" (optional)
                var_only: Kept for compatibility — all events are VAR events, so this has no effect
                
            Returns:
                JSON with VAR events, each containing:
                - minute, type, description (short label)
                - var_decision.review_type: goalDisallowed / penaltyAwarded / penaltyNotAwarded / cardUpgrade / mistakenIdentity
                - var_decision.outcome: goal_disallowed / penalty_awarded / penalty_not_awarded / card_upgraded / identity_corrected
                - var_decision.note: full FlashScore commentary — USE THIS to explain what happened
                - var_decision.player, player_id, is_home
                
            Examples:
                - query_referee_decisions(home_team="Belgium", away_team="Iran")
                - query_referee_decisions(match_id="WC_2026-06-21_BELGIUM_IRAN")
                - query_referee_decisions(home_team="Belgium", away_team="Iran", minute=25)
            """
            try:
                # If team names provided, search for match_id
                if home_team and away_team and not match_id:
                    self.log(f"Searching for match: {home_team} vs {away_team}")
                    self.status = f"Searching for {home_team} vs {away_team}..."
                    
                    # Get all match files
                    all_events = list(self.events_path.glob("*.json"))
                    
                    if not all_events:
                        return json.dumps({
                            "home_team": home_team,
                            "away_team": away_team,
                            "decisions_found": 0,
                            "message": "No VAR-reviewable decisions database found.",
                            "note": "This database contains only VAR-reviewable decisions: Goals, Penalties, Red Cards, and Mistaken Identity."
                        }, indent=2)
                    
                    # Search for matching teams (case-insensitive, normalize names)
                    def normalize_name(name: str) -> str:
                        """Normalize team name for comparison"""
                        return name.upper().replace("_", " ").replace("&", "AND").strip()
                    
                    home_norm = normalize_name(home_team)
                    away_norm = normalize_name(away_team)
                    
                    # Find all matches with these teams
                    matching_files = []
                    for event_file in all_events:
                        try:
                            with open(event_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                match_home = normalize_name(data.get("match_info", {}).get("home_team", ""))
                                match_away = normalize_name(data.get("match_info", {}).get("away_team", ""))
                                
                                # Check both home/away and away/home combinations
                                if (home_norm == match_home and away_norm == match_away) or \
                                   (home_norm == match_away and away_norm == match_home):
                                    matching_files.append((event_file, data.get("match_info", {}).get("date", "")))
                        except:
                            continue
                    
                    if not matching_files:
                        return json.dumps({
                            "home_team": home_team,
                            "away_team": away_team,
                            "decisions_found": 0,
                            "message": f"No match found between {home_team} and {away_team}",
                            "suggestion": "Try checking available matches or use exact match_id",
                            "total_matches_available": len(all_events)
                        }, indent=2)
                    
                    # Sort by date (most recent first) and use the most recent match
                    matching_files.sort(key=lambda x: x[1], reverse=True)
                    event_file = matching_files[0][0]
                    match_id = event_file.stem
                    self.log(f"Found match: {match_id}")
                
                elif not match_id:
                    return json.dumps({
                        "error": "Must provide either match_id OR both home_team and away_team",
                        "examples": [
                            "query_referee_decisions(match_id='WC_2026-06-21_BELGIUM_IRAN')",
                            "query_referee_decisions(home_team='Belgium', away_team='Iran')"
                        ]
                    }, indent=2)
                
                # Now we have match_id, proceed with normal flow
                self.log(f"Querying referee decisions: {match_id}" + (f" (minute {minute})" if minute else ""))
                self.status = f"Searching decisions for {match_id}..."
                
                # Build event file path
                event_file = self.events_path / f"{match_id}.json"
                
                if not event_file.exists():
                    # Check if any events exist
                    all_events = list(self.events_path.glob("*.json"))
                    
                    if not all_events:
                        return json.dumps({
                            "match_id": match_id,
                            "decisions_found": 0,
                            "message": "No VAR-reviewable decisions available.",
                            "note": "This database contains only VAR-reviewable decisions: Goals, Penalties, Red Cards, and Mistaken Identity."
                        }, indent=2)

                    return json.dumps({
                        "match_id": match_id,
                        "decisions_found": 0,
                        "message": f"No VAR decisions found for match: {match_id}",
                        "total_matches_with_decisions": len(all_events)
                    }, indent=2)
                
                # Load match events
                with open(event_file, 'r', encoding='utf-8') as f:
                    match_data = json.load(f)
                
                events = match_data.get("events", [])
                total_events = len(events)
                
                # Apply filters
                filtered_events = events
                
                # var_only=True → only var_review events (excludes red_card)
                if var_only:
                    filtered_events = [e for e in filtered_events if e.get('type') == 'var_review']
                
                # Filter by decision type
                if decision_type:
                    filtered_events = [e for e in filtered_events if e.get("type") == decision_type]
                
                # Filter by minute
                if minute is not None:
                    filtered_events = [e for e in filtered_events if e.get("minute") == minute]
                
                # Check if any events match filters
                if not filtered_events:
                    filters_applied = []
                    if minute is not None:
                        filters_applied.append(f"minute {minute}")
                    if decision_type:
                        filters_applied.append(f"type '{decision_type}'")
                    if var_only:
                        filters_applied.append("VAR decisions only")
                    
                    filter_text = " and ".join(filters_applied) if filters_applied else "specified criteria"
                    
                    return json.dumps({
                        "match_id": match_id,
                        "decisions_found": 0,
                        "message": f"No decisions found matching {filter_text}",
                        "total_match_decisions": total_events,
                        "var_decisions_in_match": sum(1 for e in events if "var_decision" in e),
                        "filters_applied": {
                            "minute": minute,
                            "decision_type": decision_type,
                            "var_only": var_only
                        },
                        "note": "Try removing some filters to see more results"
                    }, indent=2)
                
                events = filtered_events
                
                # Analyze VAR decisions
                var_decisions = [e for e in events if "var_decision" in e]
                
                # Build enhanced response
                result = {
                    "match_id": match_id,
                    "match_info": match_data.get("match_info", {}),
                    "summary": {
                        "total_events": len(events),
                        "var_reviews": sum(1 for e in events if e.get("type") == "var_review"),
                        "red_cards": sum(1 for e in events if e.get("type") == "red_card"),
                        "goals_disallowed": sum(1 for e in events if e.get("var_decision", {}).get("outcome") == "goal_disallowed"),
                        "penalties": sum(1 for e in events if "penalty" in e.get("var_decision", {}).get("outcome", "")),
                        "card_upgrades": sum(1 for e in events if e.get("var_decision", {}).get("review_type") == "cardUpgrade"),
                        "filters_applied": {
                            "minute": minute,
                            "decision_type": decision_type,
                            "var_only": var_only
                        }
                    },
                    "decisions": events,
                    "var_analysis": {
                        "total_var_reviews": len(var_decisions),
                        "review_types": list(set(v["var_decision"]["review_type"] for v in var_decisions)),
                        "outcomes": {
                            "confirmed": sum(1 for v in var_decisions if v["var_decision"].get("confirmed", False)),
                            "overturned": sum(1 for v in var_decisions if not v["var_decision"].get("confirmed", False))
                        }
                    } if var_decisions else None,
                    "note": "Use query_fifa_documents to understand the official rules behind these decisions."
                }
                
                self.log(f"Found {len(events)} decision(s)")
                self.status = f"Found {len(events)} decision(s)"
                
                return json.dumps(result, indent=2)
            
            except Exception as e:
                error_msg = f"Error querying referee decisions: {e}"
                self.log(error_msg)
                self.status = "Error"
                return json.dumps({
                    "error": str(e),
                    "match_id": match_id
                }, indent=2)
        
        return StructuredTool.from_function(
            func=query_referee_decisions,
            name="query_referee_decisions",
            description=(
                "Query referee decisions and VAR reviews from World Cup 2026 matches. Returns detailed JSON with:\n"
                "- Decision details: minute, type (yellow_card/red_card/penalty), description, player, reason\n"
                "- VAR information: review_type (cardUpgrade/goalCheck/penaltyCheck), initial_decision, final_decision, confirmed status\n"
                "- Player data: player_id, is_home flag\n"
                "- Match context: teams, date, tournament, venue, city\n"
                "- Summary statistics: total decisions, VAR reviews, card counts\n\n"
                "Filters available:\n"
                "- minute: Get decisions at specific minute\n"
                "- decision_type: Filter by 'yellow_card', 'red_card', 'penalty', etc.\n"
                "- var_only: Set to true to only see VAR-reviewed decisions\n\n"
                "Use for questions like:\n"
                "- 'What happened at minute 82?'\n"
                "- 'Show me all VAR decisions in this match'\n"
                "- 'Why was the red card given?'\n"
                "- 'What was the initial decision before VAR review?'\n\n"
                "Always combine with query_fifa_documents to explain the official FIFA/IFAB rules."
            )
        )

# Made with Bob"""