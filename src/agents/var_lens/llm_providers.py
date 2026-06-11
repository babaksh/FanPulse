"""
LLM Provider Factory for VAR-Lens Agent
Supports multiple LLM providers with easy extensibility
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    IBM_GRANITE = "ibm_granite"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"


class LLMFactory:
    """
    Factory class for creating LLM instances from different providers.
    Supports IBM Granite, OpenAI, HuggingFace, and more.
    """
    
    @staticmethod
    def create_llm(
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Create an LLM instance based on the specified provider.
        
        Args:
            provider: LLM provider name (ibm_granite, openai, huggingface, etc.)
            model_name: Specific model to use (provider-dependent)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            api_key: API key for the provider (if not in env)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM instance compatible with LangChain
            
        Raises:
            ValueError: If provider is not supported or configuration is invalid
            ImportError: If required provider library is not installed
        """
        provider = provider.lower()
        
        # IBM Granite (watsonx.ai)
        if provider == LLMProvider.IBM_GRANITE.value:
            return LLMFactory._create_ibm_granite(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
        
        # OpenAI
        elif provider == LLMProvider.OPENAI.value:
            return LLMFactory._create_openai(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
        
        # HuggingFace
        elif provider == LLMProvider.HUGGINGFACE.value:
            return LLMFactory._create_huggingface(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
        
        # Anthropic Claude
        elif provider == LLMProvider.ANTHROPIC.value:
            return LLMFactory._create_anthropic(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
        
        # Google (Gemini/PaLM)
        elif provider == LLMProvider.GOOGLE.value:
            return LLMFactory._create_google(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                **kwargs
            )
        
        # Ollama (Local LLMs)
        elif provider == LLMProvider.OLLAMA.value:
            return LLMFactory._create_ollama(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {[p.value for p in LLMProvider]}"
            )
    
    @staticmethod
    def _create_ibm_granite(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Create IBM Granite LLM via watsonx.ai"""
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from langchain_ibm import WatsonxLLM
        except ImportError:
            raise ImportError(
                "IBM watsonx.ai library not installed. "
                "Install with: pip install ibm-watsonx-ai langchain-ibm"
            )
        
        # Get credentials from environment or parameters
        api_key = api_key or os.getenv("IBM_WATSONX_API_KEY")
        project_id = kwargs.get("project_id") or os.getenv("IBM_WATSONX_PROJECT_ID")
        url = kwargs.get("url") or os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        if not api_key:
            raise ValueError(
                "IBM watsonx.ai API key required. "
                "Set IBM_WATSONX_API_KEY environment variable or pass api_key parameter."
            )
        
        if not project_id:
            raise ValueError(
                "IBM watsonx.ai project ID required. "
                "Set IBM_WATSONX_PROJECT_ID environment variable or pass project_id parameter."
            )
        
        # Default to Granite 13B Chat model
        model_name = model_name or "ibm/granite-13b-chat-v2"
        
        # Configure model parameters
        parameters = {
            GenParams.DECODING_METHOD: kwargs.get("decoding_method", "greedy"),
            GenParams.MAX_NEW_TOKENS: max_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.TOP_K: kwargs.get("top_k", 50),
            GenParams.TOP_P: kwargs.get("top_p", 1.0),
        }
        
        logger.info(f"Initializing IBM Granite model: {model_name}")
        
        # Create WatsonxLLM instance
        llm = WatsonxLLM(
            model_id=model_name,
            url=url,
            apikey=api_key,
            project_id=project_id,
            params=parameters
        )
        
        return llm
    
    @staticmethod
    def _create_openai(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Create OpenAI LLM"""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. "
                "Install with: pip install langchain-openai"
            )
        
        # Get API key from environment or parameters
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Default to GPT-4
        model_name = model_name or "gpt-4"
        
        logger.info(f"Initializing OpenAI model: {model_name}")
        
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,  # type: ignore
            **kwargs
        )
        
        return llm
    
    @staticmethod
    def _create_huggingface(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Create HuggingFace LLM"""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
        except ImportError:
            raise ImportError(
                "HuggingFace library not installed. "
                "Install with: pip install langchain-huggingface"
            )
        
        # Get API key from environment or parameters
        api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        
        # Default to a good open-source model
        model_name = model_name or "mistralai/Mistral-7B-Instruct-v0.2"
        
        logger.info(f"Initializing HuggingFace model: {model_name}")
        
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            temperature=temperature,
            max_new_tokens=max_tokens,
            huggingfacehub_api_token=api_key,
            **kwargs
        )
        
        return llm
    
    @staticmethod
    def _create_anthropic(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Create Anthropic Claude LLM"""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "Anthropic library not installed. "
                "Install with: pip install langchain-anthropic"
            )
        
        # Get API key from environment or parameters
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Anthropic API key required. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )
        
        # Default to Claude 3
        model_name = model_name or "claude-3-sonnet-20240229"
        
        logger.info(f"Initializing Anthropic model: {model_name}")
        
        llm = ChatAnthropic(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,  # type: ignore
            **kwargs
        )
        
        return llm
    
    @staticmethod
    def _create_google(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Create Google Gemini/PaLM LLM"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "Google GenAI library not installed. "
                "Install with: pip install langchain-google-genai"
            )
        
        # Get API key from environment or parameters
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Google API key required. "
                "Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )
        
        # Default to Gemini Pro
        model_name = model_name or "gemini-pro"
        
        logger.info(f"Initializing Google model: {model_name}")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key,
            **kwargs
        )
        
        return llm
    
    @staticmethod
    def _create_ollama(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """Create Ollama LLM for local models"""
        try:
            from langchain_ollama import OllamaLLM
        except ImportError:
            raise ImportError(
                "Ollama library not installed. "
                "Install with: pip install langchain-ollama"
            )
        
        # Default to Granite 4.1 8B (IBM's model via Ollama)
        model_name = model_name or "granite4.1:8b"
        
        # Get base URL from environment or use default
        base_url = kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        logger.info(f"Initializing Ollama model: {model_name} at {base_url}")
        
        llm = OllamaLLM(
            model=model_name,
            temperature=temperature,
            num_predict=max_tokens,
            base_url=base_url,
            **kwargs
        )
        
        return llm
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """
        Get information about available providers and their requirements.
        
        Returns:
            Dictionary with provider info including required env vars and default models
        """
        return {
            "ibm_granite": {
                "name": "IBM Granite (watsonx.ai)",
                "env_vars": ["IBM_WATSONX_API_KEY", "IBM_WATSONX_PROJECT_ID"],
                "default_model": "ibm/granite-13b-chat-v2",
                "install": "pip install ibm-watsonx-ai langchain-ibm",
                "description": "IBM's Granite models via watsonx.ai platform"
            },
            "openai": {
                "name": "OpenAI",
                "env_vars": ["OPENAI_API_KEY"],
                "default_model": "gpt-4",
                "install": "pip install langchain-openai",
                "description": "OpenAI's GPT models (GPT-4, GPT-3.5-turbo)"
            },
            "huggingface": {
                "name": "HuggingFace",
                "env_vars": ["HUGGINGFACE_API_KEY"],
                "default_model": "mistralai/Mistral-7B-Instruct-v0.2",
                "install": "pip install langchain-huggingface",
                "description": "Open-source models via HuggingFace Inference API"
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "env_vars": ["ANTHROPIC_API_KEY"],
                "default_model": "claude-3-sonnet-20240229",
                "install": "pip install langchain-anthropic",
                "description": "Anthropic's Claude models"
            },
            "google": {
                "name": "Google Gemini",
                "env_vars": ["GOOGLE_API_KEY"],
                "default_model": "gemini-pro",
                "install": "pip install langchain-google-genai",
                "description": "Google's Gemini models"
            },
            "ollama": {
                "name": "Ollama (Local)",
                "env_vars": [],
                "default_model": "granite4.1:8b",
                "install": "pip install langchain-ollama",
                "description": "Run LLMs locally via Ollama (Llama, Gemma, Mistral, etc.)"
            }
        }


def print_provider_info():
    """Print information about available LLM providers"""
    providers = LLMFactory.get_available_providers()
    
    print("\n" + "="*70)
    print("Available LLM Providers")
    print("="*70)
    
    for provider_id, info in providers.items():
        print(f"\n{info['name']} ({provider_id})")
        print(f"  Default Model: {info['default_model']}")
        print(f"  Required Env Vars: {', '.join(info['env_vars'])}")
        print(f"  Install: {info['install']}")
        print(f"  Description: {info['description']}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Print provider information
    print_provider_info()

# Made with Bob
