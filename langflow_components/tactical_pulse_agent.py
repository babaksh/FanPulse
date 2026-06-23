"""
Tactical Pulse Agent Component for FanPulse
Specialized agent for international football match analysis and team performance
Covers all matches (1872-2026) with detailed tactical data for major tournaments
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.base.agents.events import ExceptionWithMessageError
from lfx.base.models.unified_models import get_llm
from lfx.components.agentics.helpers.model_config import validate_model_selection
from lfx.components.langchain_utilities.tool_calling import ToolCallingAgentComponent
from lfx.components.models_and_agents.memory import MemoryComponent
from lfx.custom.custom_component.component import get_component_toolkit
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, ModelInput
from lfx.io import IntInput, MessageTextInput, MultilineInput, Output
from lfx.log.logger import logger
from lfx.schema.message import Message

if TYPE_CHECKING:
    from langchain_core.tools import Tool


class TacticalPulseAgent(ToolCallingAgentComponent):
    """
    Tactical Pulse Agent: Expert football analyst for FIFA World Cup 2026.
    
    Data Sources:
    - results.csv: All international matches (1872-2026, ~49,000 matches)
    - tactical_stats.csv: Major tournaments with prefix system (WC_2022*, WC_2026*, etc.)
    
    Available Tools (5):
    1. analyze_team: Returns JSON with comprehensive team analysis (overall + tournament data)
    2. get_team_data: Returns JSON with quick statistics (matches, wins, goals, form)
    3. compare_teams: Returns JSON with head-to-head comparison
    4. get_tactical_data: Returns JSON with tournament tactical stats (possession, xG, shots)
    5. query_csv: Custom queries for specific data needs
    
    Agent Role:
    - Receives JSON data from tools
    - Analyzes and interprets the data
    - Provides expert insights and predictions
    - Formats responses as professional tactical analysis (not robotic reports)
    """
    
    display_name: str = "Tactical Pulse Agent"
    description: str = "Agent that analyzes team performance, compares teams head-to-head, and provides tactical insights for World Cup 2026"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon = "brain"
    beta = False
    name = "TacticalPulseAgent"

    inputs = [
        ModelInput(
            name="model",
            display_name="Language Model",
            info="Select Ollama Granite 3.1 8B for tactical analysis",
            real_time_refresh=True,
            required=True,
        ),
        MessageTextInput(
            name="input_value",
            display_name="User Question",
            info="Tactical or statistical question from the user",
            tool_mode=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="System prompt to guide the agent's behavior. Connect TACTICAL_PULSE_SYSTEM_PROMPT.md for detailed instructions.",
            value="You are Tactical Pulse, an expert football analyst for FIFA World Cup 2026. Tools return JSON data - your job is to analyze, interpret, and provide insights (not just report numbers). Data: results.csv (1872-2026) + tactical_stats.csv (WC_2022/WC_2026 with prefix). Tools: analyze_team, get_team_stats, compare_teams, get_tactical_data, query_csv. Write like a professional analyst, not a robot.",
            advanced=False,
        ),
        MessageTextInput(
            name="context_id",
            display_name="Context ID",
            info="Chat context identifier for memory management",
            value="",
            advanced=True,
        ),
        IntInput(
            name="n_messages",
            display_name="Chat History Messages",
            value=50,
            info="Number of previous messages to include for context",
            advanced=True,
            show=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            info="Maximum response length (recommended: 2000 for detailed tactical analysis)",
            value=2000,
            advanced=True,
            range_spec=RangeSpec(min=100, max=4000, step=100, step_type="int"),
        ),
        BoolInput(
            name="verbose",
            display_name="Verbose Logging",
            info="Enable detailed logging for debugging",
            value=False,
            advanced=True,
        ),
        *LCToolsAgentComponent.get_base_inputs(),
    ]
    
    outputs = [
        Output(
            name="response",
            display_name="Tactical Analysis",
            method="message_response"
        ),
        Output(
            name="toolset",
            display_name="Toolset",
            method="_get_tools"
        ),
    ]

    def _get_llm(self):
        """Get configured language model for tactical analysis."""
        max_tokens = getattr(self, "max_tokens", 2000)
        if max_tokens in {"", 0}:
            max_tokens = 2000
            
        return get_llm(
            model=self.model,
            user_id=self.user_id,
            max_tokens=max_tokens,
            temperature=0.3,  # Low temperature for precise tool calling
        )

    async def get_agent_requirements(self):
        """Prepare agent requirements: LLM, chat history, and tools."""
        # Validate model selection
        selected_model = self.model
        try:
            from langchain_core.language_models import BaseLanguageModel
            is_connected_model = isinstance(selected_model, BaseLanguageModel)
        except ImportError:
            is_connected_model = False

        if not is_connected_model:
            validate_model_selection(selected_model)

        # Get LLM
        llm_model = self._get_llm()
        if llm_model is None:
            msg = "No language model selected. Please configure Ollama Granite 3.1 8B."
            raise ValueError(msg)

        # Get chat history from memory
        self.chat_history = await self.get_memory_data()
        await logger.adebug(f"Tactical Pulse: Retrieved {len(self.chat_history)} chat history messages")
        if isinstance(self.chat_history, Message):
            self.chat_history = [self.chat_history]

        # Validate tools
        if not self.tools:
            await logger.awarning(
                "Tactical Pulse: No tools configured. "
                "Agent should have 5 tools: analyze_team, get_team_stats, compare_teams, get_tactical_data, query_csv"
            )
            self.tools = []

        # Set shared callbacks for tool tracing
        self.set_tools_callbacks(self.tools, self._get_shared_callbacks())

        return llm_model, self.chat_history, self.tools

    async def message_response(self) -> Message:
        """Execute Tactical Pulse agent and return response."""
        try:
            # Get agent requirements
            llm_model, self.chat_history, self.tools = await self.get_agent_requirements()
            
            # Configure agent
            self.set(
                llm=llm_model,
                tools=self.tools or [],
                chat_history=self.chat_history,
                input_value=self.input_value,
                system_prompt=self.system_prompt,
            )
            
            # Create and run agent
            agent = self.create_agent_runnable()
            result = await self.run_agent(agent)
            
            await logger.adebug(f"Tactical Pulse: Successfully processed query")
            return result

        except (ValueError, TypeError, KeyError) as e:
            await logger.aerror(f"Tactical Pulse {type(e).__name__}: {e!s}")
            raise
        except ExceptionWithMessageError as e:
            await logger.aerror(f"Tactical Pulse ExceptionWithMessageError: {e}")
            raise
        except Exception as e:
            await logger.aerror(f"Tactical Pulse unexpected error: {e!s}")
            raise

    async def get_memory_data(self):
        """Retrieve chat history from memory, avoiding message duplication."""
        import uuid
        
        # Create unique session_id for this agent to completely isolate its memory
        # This prevents chat history contamination when multiple agents are called
        unique_session_id = f"{self.graph.session_id}_tactical_pulse_{uuid.uuid4().hex[:8]}"
        
        messages = (
            await MemoryComponent(**self.get_base_args())
            .set(
                session_id=unique_session_id,  # Use unique session_id for complete isolation
                context_id=self.context_id,
                order="Ascending",
                n_messages=self.n_messages,
            )
            .retrieve_messages()
        )
        
        # Filter out current input message to avoid duplication
        return [
            message
            for message in messages
            if getattr(message, "id", None) != getattr(self.input_value, "id", None)
        ]

    async def _get_tools(self) -> list[Tool]:
        """Expose Tactical Pulse agent as a tool for other components."""
        component_toolkit = get_component_toolkit()
        agent_description = self.get_tool_description()
        
        tools = component_toolkit(component=self).get_tools(
            tool_name="Tactical_Pulse_Agent",
            tool_description=(
                f"{agent_description} "
                "Expert football analyst that interprets JSON data from tools and provides tactical insights. "
                "Data: results.csv (1872-2026) + tactical_stats.csv (WC_2022/WC_2026 prefix system). "
                "Tools return JSON for analysis, not formatted reports."
            ),
            callbacks=self.get_langchain_callbacks(),
        )
        
        if hasattr(self, "tools_metadata"):
            tools = component_toolkit(
                component=self,
                metadata=self.tools_metadata
            ).update_tools_metadata(tools=tools)

        return tools

# Made with Bob
