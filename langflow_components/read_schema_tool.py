"""
Read Schema Tool for LangFlow
Provides access to data schema for understanding available columns and data structure
"""

from lfx.custom import Component
from lfx.io import Output
from lfx.field_typing import Tool
from langchain_core.tools import StructuredTool
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ReadSchemaTool(Component):
    display_name: str = "Read Data Schema"
    description: str = "Read complete data schema to understand available columns and data structure"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "file-json"
    name: str = "read_schema_tool"
    
    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.schema_path = self.project_root / "data" / "match_data" / "data_schema.json"
    
    def build_tool(self) -> Tool:
        """Build the schema reading tool"""
        
        def read_schema() -> str:
            """Read complete data schema from data/match_data/data_schema.json
            
            This tool provides comprehensive information about:
            - Available tables (results.csv, tactical_data.csv)
            - All columns in each table with descriptions
            - Data types, formats, and valid ranges
            - Match ID prefixes and tournament codes
            - Calculated metrics and their formulas
            - Usage examples and best practices
            - Common mistakes to avoid
            
            IMPORTANT: Always call this tool BEFORE making custom queries to understand:
            - What columns exist in each table
            - Correct column names for filtering
            - Data types and valid value ranges
            - Which table contains which metrics
            
            Returns:
                Complete schema as formatted JSON string with all metadata
            """
            try:
                self.log("Reading data schema")
                self.status = "Reading schema..."
                
                if not self.schema_path.exists():
                    return f"❌ Schema file not found: {self.schema_path}"
                
                # Read schema
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                # Format schema for readability
                result = "# 📋 FanPulse Data Schema\n\n"
                result += "## Overview\n\n"
                
                # Agent reading guide
                if "_agent_reading_guide" in schema:
                    guide = schema["_agent_reading_guide"]
                    result += f"**Purpose:** {guide.get('purpose', 'N/A')}\n\n"
                    result += "**Core Rules:**\n"
                    for rule in guide.get('core_rules', []):
                        result += f"- {rule}\n"
                    result += "\n"
                
                # Results table
                if "results.csv" in schema:
                    results_schema = schema["results.csv"]
                    result += "## 📊 Table: Historical Match Database\n\n"
                    result += f"**Role:** {results_schema.get('table_role', 'N/A')}\n"
                    result += f"**Coverage:** {results_schema.get('coverage', {}).get('time_range', 'N/A')}\n"
                    result += f"**Total Matches:** {results_schema.get('coverage', {}).get('total_matches', 'N/A')}\n\n"
                    
                    result += "**Columns:**\n"
                    for col_name, col_info in results_schema.get('columns', {}).items():
                        result += f"- `{col_name}`: {col_info.get('desc', 'N/A')} "
                        result += f"(type: {col_info.get('type', 'N/A')})\n"
                    result += "\n"
                
                # Tactical data table
                if "tactical_data.csv" in schema:
                    tactical_schema = schema["tactical_data.csv"]
                    result += "## ⚽ Table: Tournament Tactical Database\n\n"
                    result += f"**Role:** {tactical_schema.get('table_role', 'N/A')}\n"
                    result += f"**Coverage:** {tactical_schema.get('coverage', {}).get('time_range', 'N/A')}\n"
                    result += f"**Total Matches:** {tactical_schema.get('coverage', {}).get('total_matches', 'N/A')}\n\n"
                    
                    result += "**Columns (41 total):**\n"
                    columns = tactical_schema.get('columns', {})
                    
                    # Group columns by category
                    result += "\n**Basic Info:**\n"
                    basic_cols = ['match_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament']
                    for col in basic_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                    
                    result += "\n**Formations & Demographics:**\n"
                    form_cols = ['home_formation', 'away_formation', 'home_avg_age', 'away_avg_age']
                    for col in form_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                    
                    result += "\n**Possession:**\n"
                    poss_cols = ['home_possession', 'away_possession']
                    for col in poss_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')} "
                            result += f"(range: {columns[col].get('range', 'N/A')})\n"
                    
                    result += "\n**Shooting:**\n"
                    shot_cols = ['home_shots_total', 'away_shots_total', 'home_shots_on_target', 
                                'away_shots_on_target', 'home_shots_blocked', 'away_shots_blocked',
                                'home_shot_accuracy', 'away_shot_accuracy']
                    for col in shot_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                    
                    result += "\n**Passing:**\n"
                    pass_cols = ['home_passes_total', 'away_passes_total', 'home_pass_accuracy', 
                                'away_pass_accuracy', 'home_key_passes', 'away_key_passes']
                    for col in pass_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                    
                    result += "\n**Defending:**\n"
                    def_cols = ['home_tackles_won', 'away_tackles_won', 'home_tackle_success', 
                               'away_tackle_success', 'home_interceptions', 'away_interceptions',
                               'home_clearances', 'away_clearances', 'home_aerials_won', 'away_aerials_won']
                    for col in def_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                    
                    result += "\n**Intensity Metrics:**\n"
                    int_cols = ['home_attacking_intensity', 'away_attacking_intensity',
                               'home_defensive_intensity', 'away_defensive_intensity']
                    for col in int_cols:
                        if col in columns:
                            result += f"- `{col}`: {columns[col].get('desc', 'N/A')}\n"
                            if 'calculation' in columns[col]:
                                result += f"  - Formula: {columns[col]['calculation']}\n"
                    
                    result += "\n"
                
                # Common mistakes
                if "common_mistakes_to_avoid" in schema:
                    result += "## ⚠️ Common Mistakes to Avoid\n\n"
                    for mistake_key, mistake_info in schema["common_mistakes_to_avoid"].items():
                        result += f"**{mistake_key}:**\n"
                        result += f"- ❌ Wrong: {mistake_info.get('wrong', 'N/A')}\n"
                        result += f"- ✅ Right: {mistake_info.get('right', 'N/A')}\n\n"
                
                # Best practices
                if "best_practices" in schema:
                    result += "## ✅ Best Practices\n\n"
                    practices = schema["best_practices"]
                    if "do" in practices:
                        result += "**DO:**\n"
                        for practice in practices["do"]:
                            result += f"- {practice}\n"
                        result += "\n"
                    if "dont" in practices:
                        result += "**DON'T:**\n"
                        for practice in practices["dont"]:
                            result += f"- {practice}\n"
                        result += "\n"
                
                result += "\n---\n"
                
                self.log(f"Schema read successfully")
                self.status = "Schema loaded"
                
                return result
            
            except Exception as e:
                error_msg = f"Error reading schema: {e}"
                self.log(error_msg)
                self.status = "Error"
                return f"❌ {error_msg}"
        
        return StructuredTool.from_function(
            func=read_schema,
            name="read_schema",
            description=(
                "Read the complete data schema (column names, types, ranges) for both tables: "
                "results.csv (historical matches) and tactical_data.csv (tactical metrics). "
                "Call this ONLY when you are unsure of an exact column name before using query_csv. "
                "Do NOT call on every query — use the known column names from the system prompt first."
            )
        )

# Made with Bob