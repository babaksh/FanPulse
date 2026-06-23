"""
FanPulse Orchestrator Agent
Intelligent coordinator for VAR-Lens and Tactical Pulse agents
Handles single and multiple intent queries with sequential execution
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.base.agents.events import ExceptionWithMessageError
from lfx.base.models.unified_models import get_llm, get_language_model_options, handle_model_input_update
from lfx.components.agentics.helpers.model_config import validate_model_selection
from lfx.components.langchain_utilities.tool_calling import ToolCallingAgentComponent
from lfx.components.models_and_agents.memory import MemoryComponent
from lfx.custom.custom_component.component import get_component_toolkit
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, ModelInput
from lfx.io import IntInput, MessageTextInput, MultilineInput, Output
from lfx.log.logger import logger
from lfx.schema.dotdict import dotdict
from lfx.schema.message import Message

if TYPE_CHECKING:
    from langchain_core.tools import Tool


class FanPulseOrchestrator(ToolCallingAgentComponent):
    """
    FanPulse Orchestrator: Intelligent coordinator for FIFA World Cup 2026.
    
    This agent:
    - Analyzes user questions (single or multiple intents)
    - Routes to appropriate specialized agents (VAR-Lens, Tactical Pulse)
    - Executes agents sequentially (one at a time)
    - Synthesizes results into unified responses
    """
    
    display_name: str = "FanPulse Orchestrator"
    description: str = "Intelligent coordinator for VAR-Lens and Tactical Pulse agents. Handles single and multiple intent queries with sequential execution."
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon = "network"
    beta = False
    name = "FanPulseOrchestrator"

    inputs = [
        ModelInput(
            name="model",
            display_name="Language Model",
            info="Select Ollama Granite 3.1 8B for orchestration",
            real_time_refresh=True,
            required=True,
        ),
        MessageTextInput(
            name="input_value",
            display_name="User Question",
            info="World Cup question (single or multiple intents)",
            tool_mode=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="Orchestration strategy and instructions. Connect a Prompt Template component here for the full prompt.",
            value="You are the FanPulse Orchestrator for World Cup 2026 questions. Use VAR_Lens_Agent for rules and Tactical_Pulse_Agent for statistics.",
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
            info="Maximum response length (recommended: 2500 for comprehensive synthesis)",
            value=2500,
            advanced=True,
            range_spec=RangeSpec(min=500, max=4000, step=100, step_type="int"),
        ),
        BoolInput(
            name="verbose",
            display_name="Verbose Logging",
            info="Enable detailed logging for debugging",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="add_current_date_tool",
            display_name="Current Date Tool",
            info="Add current date tool to the orchestrator",
            value=False,
            advanced=True,
        ),
        *LCToolsAgentComponent.get_base_inputs(),
    ]
    
    outputs = [
        Output(
            name="response",
            display_name="Orchestrated Response",
            method="message_response"
        ),
    ]

    def _resolve_selected_model(self):
        """Resolve the selected model."""
        try:
            from langchain_core.language_models import BaseLanguageModel
            if isinstance(self.model, BaseLanguageModel):
                return self.model
        except ImportError:
            pass

        if isinstance(self.model, list) and self.model:
            return self.model

        return self.model

    def _get_max_tokens_value(self):
        """Return the user-supplied max_tokens or None when unset/zero."""
        val = getattr(self, "max_tokens", None)
        if val in {"", 0}:
            return 2500  # Default for orchestrator
        return val

    def _get_llm(self):
        """Get configured language model for orchestration."""
        return get_llm(
            model=self.model,
            user_id=self.user_id,
            max_tokens=self._get_max_tokens_value(),
            temperature=0.2,  # Low temperature for precise tool calling
        )

    async def get_agent_requirements(self):
        """Prepare agent requirements: LLM, chat history, and tools."""
        from langchain_core.tools import StructuredTool
        
        # Validate model selection
        if not self.model:
            msg = "No language model selected. Please select Ollama Granite 4.1 8B from the Language Model dropdown."
            raise ValueError(msg)
            
        selected_model = self._resolve_selected_model()
        try:
            from langchain_core.language_models import BaseLanguageModel
            is_connected_model = isinstance(selected_model, BaseLanguageModel)
        except ImportError:
            is_connected_model = False

        if not is_connected_model:
            validate_model_selection(selected_model)

        # Ensure _get_llm() uses the resolved model
        self.model = selected_model
        llm_model = self._get_llm()
        if llm_model is None:
            msg = "No language model selected. Please configure Ollama Granite 3.1 8B."
            raise ValueError(msg)

        # Get chat history from memory
        self.chat_history = await self.get_memory_data()
        await logger.adebug(f"FanPulse Orchestrator: Retrieved {len(self.chat_history)} chat history messages")
        if isinstance(self.chat_history, Message):
            self.chat_history = [self.chat_history]

        # Add current date tool if enabled
        if self.add_current_date_tool:
            from lfx.components.helpers import CurrentDateComponent
            if not isinstance(self.tools, list):
                self.tools = []
            current_date_tool = (await CurrentDateComponent(**self.get_base_args()).to_toolkit()).pop(0)
            if not isinstance(current_date_tool, StructuredTool):
                msg = "CurrentDateComponent must be converted to a StructuredTool"
                raise TypeError(msg)
            self.tools.append(current_date_tool)

        # Validate tools (should have VAR-Lens and Tactical Pulse agents)
        if not self.tools:
            await logger.awarning(
                "FanPulse Orchestrator: No agent tools configured. "
                "Please connect VAR-Lens Agent and Tactical Pulse Agent as tools."
            )
            self.tools = []

        # Set shared callbacks for tool tracing
        self.set_tools_callbacks(self.tools, self._get_shared_callbacks())

        return llm_model, self.chat_history, self.tools

    async def message_response(self) -> Message:
        """Execute orchestrator and return response."""
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
            # The agent will automatically:
            # 1. Analyze the question
            # 2. Decide which tool(s) to call
            # 3. Execute tools (parallel)
            # 4. Synthesize the results
            agent = self.create_agent_runnable()
            result = await self.run_agent(agent)
            
            await logger.adebug("FanPulse Orchestrator: Successfully processed query")
            return result

        except (ValueError, TypeError, KeyError) as e:
            await logger.aerror(f"FanPulse Orchestrator {type(e).__name__}: {e!s}")
            raise
        except ExceptionWithMessageError as e:
            await logger.aerror(f"FanPulse Orchestrator ExceptionWithMessageError: {e}")
            raise
        except Exception as e:
            await logger.aerror(f"FanPulse Orchestrator unexpected error: {e!s}")
            raise

    async def get_memory_data(self):
        """Retrieve chat history from memory, avoiding message duplication."""
        messages = (
            await MemoryComponent(**self.get_base_args())
            .set(
                session_id=self.graph.session_id,
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

    def update_input_types(self, build_config: dotdict) -> dotdict:
        """Update input types for all fields in build_config."""
        for key, value in build_config.items():
            if isinstance(value, dict):
                if value.get("input_types") is None:
                    build_config[key]["input_types"] = []
            elif hasattr(value, "input_types") and value.input_types is None:
                value.input_types = []
        return build_config

    async def update_build_config(
        self,
        build_config: dotdict,
        field_value: list[dict],
        field_name: str | None = None,
    ) -> dotdict:
        # Update model options with caching
        build_config = handle_model_input_update(
            component=self,
            build_config=dict(build_config),
            field_value=field_value,
            field_name=field_name,
            cache_key_prefix="language_model_options_tool_calling",
            get_options_func=lambda user_id=None: get_language_model_options(user_id=user_id, tool_calling=True),
        )
        build_config = dotdict(build_config)

        if field_name == "model":
            build_config = self.update_input_types(build_config)

        return dotdict({k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in build_config.items()})

    async def _get_tools(self) -> list[Tool]:
        """Expose FanPulse Orchestrator as a tool for other components."""
        component_toolkit = get_component_toolkit()
        agent_description = self.get_tool_description()
        
        tools = component_toolkit(component=self).get_tools(
            tool_name="FanPulse_Orchestrator",
            tool_description=(
                f"{agent_description} "
                "Intelligent coordinator for World Cup 2026 questions. "
                "Handles VAR rules and tactical analysis with sequential execution."
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
