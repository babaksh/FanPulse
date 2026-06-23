"""
VAR-Lens Agent Component for FanPulse
Specialized agent for FIFA VAR rules and Video Assistant Referee decisions
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


class VARLensAgent(ToolCallingAgentComponent):
    """
    VAR-Lens Agent: FIFA VAR rules expert.
    
    Data Source:
    - FAISS Vector Store: 658 rule vectors from 7 official FIFA/IFAB documents
      * Laws of the Game 2026-27
      * VAR Protocol (IFAB)
      * FIFA World Cup 2026 Regulations
      * Changes to Laws 2026-27
      * Off-field treatment protocol
      * Time-limited substitution protocol
      * Throw-in and goal-kick countdown protocol
    
    Available Tools (2):
    1. query_fifa_documents: Search official FIFA/IFAB documents for general rules
    2. query_referee_decisions: Query referee decisions and VAR reviews from matches
    
    When to Use:
    - User asks about VAR, offside, fouls, penalties, handballs, red cards, referee procedures, FIFA rules
    """
    
    display_name: str = "VAR-Lens Agent"
    description: str = "Agent that explains FIFA rules, VAR decisions, offside, fouls, penalties, and referee procedures for World Cup 2026"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon = "brain"
    beta = False
    name = "VARLensAgent"

    inputs = [
        ModelInput(
            name="model",
            display_name="Language Model",
            info="Select Ollama Granite 4.1 8B for VAR analysis",
            real_time_refresh=True,
            required=True,
        ),
        MessageTextInput(
            name="input_value",
            display_name="User Question",
            info="VAR-related question from the user",
            tool_mode=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="System prompt to guide the agent's behavior. Connect VAR_LENS_SYSTEM_PROMPT.md for detailed instructions.",
            value="You are VAR-Lens, a FIFA VAR rules expert. You have 2 tools: query_fifa_documents (general rules) and query_referee_decisions (match incidents). Always use appropriate tool(s) to retrieve data, then analyze and explain clearly. Never answer from training data - only from retrieved data.",
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
            info="Maximum response length (recommended: 1500 for detailed VAR explanations)",
            value=1500,
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
            display_name="VAR Analysis",
            method="message_response"
        ),
        Output(
            name="toolset",
            display_name="Toolset",
            method="_get_tools"
        ),
    ]

    def _get_llm(self):
        """Get configured language model for VAR analysis."""
        max_tokens = getattr(self, "max_tokens", 1500)
        if max_tokens in {"", 0}:
            max_tokens = 1500
            
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
        await logger.adebug(f"VAR-Lens: Retrieved {len(self.chat_history)} chat history messages")
        if isinstance(self.chat_history, Message):
            self.chat_history = [self.chat_history]

        # Validate tools
        if not self.tools:
            await logger.awarning("VAR-Lens: No tools configured. Agent should have 2 tools: query_fifa_documents and query_referee_decisions")
            self.tools = []

        # Set shared callbacks for tool tracing
        self.set_tools_callbacks(self.tools, self._get_shared_callbacks())

        return llm_model, self.chat_history, self.tools

    async def message_response(self) -> Message:
        """Execute VAR-Lens agent and return response."""
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
            
            await logger.adebug(f"VAR-Lens: Successfully processed query")
            return result

        except (ValueError, TypeError, KeyError) as e:
            await logger.aerror(f"VAR-Lens {type(e).__name__}: {e!s}")
            raise
        except ExceptionWithMessageError as e:
            await logger.aerror(f"VAR-Lens ExceptionWithMessageError: {e}")
            raise
        except Exception as e:
            await logger.aerror(f"VAR-Lens unexpected error: {e!s}")
            raise

    async def get_memory_data(self):
        """Retrieve chat history from memory, avoiding message duplication."""
        import uuid
        
        # Create unique session_id for this agent to completely isolate its memory
        # This prevents chat history contamination when multiple agents are called
        unique_session_id = f"{self.graph.session_id}_var_lens_{uuid.uuid4().hex[:8]}"
        
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
        """Expose VAR-Lens agent as a tool for other components."""
        component_toolkit = get_component_toolkit()
        agent_description = self.get_tool_description()
        
        tools = component_toolkit(component=self).get_tools(
            tool_name="VAR_Lens_Agent",
            tool_description=(
                f"{agent_description} "
                "Data: 658 vectors from 7 FIFA/IFAB documents + Referee Decisions Database. "
                "Tools: query_fifa_documents, query_referee_decisions."
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
