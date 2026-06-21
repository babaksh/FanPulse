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
            match_id: str,
            minute: Optional[int] = None,
            decision_type: Optional[str] = None,
            var_only: bool = False
        ) -> str:
            """Query referee decisions and VAR reviews from a specific match.
            
            Args:
                match_id: Match identifier (e.g., "WC_2026-06-15_BRAZIL_ARGENTINA")
                minute: Specific minute to query (optional, returns all decisions if not provided)
                decision_type: Filter by type: "yellow_card", "red_card", "penalty", "goal_disallowed" (optional)
                var_only: If True, only return decisions that involved VAR review (optional)
                
            Returns:
                JSON with detailed referee decisions including:
                - Basic info: minute, type, description, player, reason
                - VAR details (if applicable): review_type, initial_decision, final_decision, confirmed
                - Player info: player_id, is_home
                - Match context: teams, date, tournament, venue
            """
            try:
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
                            "message": "No VAR-reviewable decisions database found. Use scripts/sofascore_var_extractor.py to extract data from SofaScore.",
                            "note": "This database contains only VAR-reviewable decisions: Goals, Penalties, Red Cards, and Mistaken Identity."
                        }, indent=2)
                    
                    # Suggest available matches
                    available_matches = [f.stem for f in all_events]
                    return json.dumps({
                        "match_id": match_id,
                        "decisions_found": 0,
                        "message": f"No decisions found for match: {match_id}",
                        "available_matches": available_matches[:5],
                        "total_matches_with_decisions": len(available_matches)
                    }, indent=2)
                
                # Load match events
                with open(event_file, 'r', encoding='utf-8') as f:
                    match_data = json.load(f)
                
                events = match_data.get("events", [])
                total_events = len(events)
                
                # Apply filters
                filtered_events = events
                
                # Filter by VAR only
                if var_only:
                    filtered_events = [e for e in filtered_events if "var_decision" in e]
                
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
                        "total_decisions": len(events),
                        "var_reviews": len(var_decisions),
                        "goals": sum(1 for e in events if e.get("type") in ["goal", "own_goal"]),
                        "penalties": sum(1 for e in events if e.get("type") == "penalty"),
                        "yellow_cards": sum(1 for e in events if e.get("type") == "yellow_card"),
                        "red_cards": sum(1 for e in events if e.get("type") == "red_card"),
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