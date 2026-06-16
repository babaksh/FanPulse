"""
Query Referee Decisions Tool for LangFlow
Provides access to referee decisions and VAR reviews from matches
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
    display_name: str = "Query Referee Decisions"
    description: str = "Query referee decisions and VAR reviews from matches"
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
        
        def query_referee_decisions(match_id: str, minute: Optional[int] = None) -> str:
            """Query referee decisions and VAR reviews from a specific match.
            
            Args:
                match_id: Match identifier (e.g., "WC2026_2026_06_15_Brazil_Argentina")
                minute: Specific minute to query (optional, returns all decisions if not provided)
                
            Returns:
                JSON with referee decisions and VAR reviews for analysis
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
                            "message": "No referee decisions database found. Decisions can be added using scripts/var_lens_setup/add_referee_decision.py",
                            "note": "This feature tracks referee decisions and VAR reviews during matches."
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
                
                # Filter by minute if specified
                if minute is not None:
                    filtered_events = [e for e in events if e.get("minute") == minute]
                    
                    if not filtered_events:
                        return json.dumps({
                            "match_id": match_id,
                            "minute": minute,
                            "decisions_found": 0,
                            "message": f"No decisions found at minute {minute}",
                            "total_match_decisions": len(events),
                            "note": "Try querying without minute parameter to see all decisions"
                        }, indent=2)
                    
                    events = filtered_events
                
                # Build response
                result = {
                    "match_id": match_id,
                    "decisions_found": len(events),
                    "referee_decisions": events,
                    "match_info": match_data.get("match_info", {}),
                    "note": "These are referee decisions and VAR reviews. Use query_fifa_documents to get the official rules."
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
                "Query referee decisions and VAR reviews from matches. Returns JSON with decision details including "
                "VAR reviews, referee names, review duration, and incident descriptions. Use this for match-specific "
                "questions like 'What happened at minute 67?' or 'Why was the goal disallowed?'. "
                "Combine with query_fifa_documents to explain the official rules behind the decisions."
            )
        )

# Made with Bob