# LLM Setup Guide for FanPulse

This guide explains how to set up and use different LLM providers with the VAR-Lens agent.

## Overview

FanPulse supports multiple LLM providers through a unified factory pattern:

- **IBM Granite** (watsonx.ai) - Recommended for IBM Challenge
- **OpenAI** (GPT-4, GPT-3.5) - For quick testing
- **HuggingFace** - Free open-source models
- **Anthropic Claude** - Optional alternative
- **Google Gemini** - Optional alternative

## Quick Start

### 1. Install LLM Dependencies

```powershell
# Install all LLM provider packages
pip install -r requirements-llm.txt

# Or install specific providers only:
pip install langchain langchain-core

# For IBM Granite
pip install ibm-watsonx-ai langchain-ibm

# For OpenAI
pip install langchain-openai

# For HuggingFace
pip install langchain-huggingface
```

### 2. Configure Environment Variables

Copy the example environment file:

```powershell
cp .env.example .env
```

Edit `.env` and add your API keys (see provider-specific sections below).

### 3. Test Your Setup

```powershell
# Check available providers
python -c "from src.agents.var_lens.llm_providers import print_provider_info; print_provider_info()"

# Test with configured providers
python scripts/test_var_lens_with_llm.py
```

---

## Provider Setup

### IBM Granite (watsonx.ai) - Recommended

IBM's Granite models are the official choice for the IBM Challenge.

#### Getting Started

1. **Create IBM Cloud Account**
   - Go to [IBM Cloud](https://cloud.ibm.com/)
   - Sign up or log in

2. **Get API Key**
   - Navigate to [API Keys](https://cloud.ibm.com/iam/apikeys)
   - Click "Create an IBM Cloud API key"
   - Copy and save your API key

3. **Get Project ID**
   - Go to [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/)
   - Create or select a project
   - Copy the Project ID from project settings

4. **Set Environment Variables**

```powershell
# PowerShell
$env:IBM_WATSONX_API_KEY="your_api_key_here"
$env:IBM_WATSONX_PROJECT_ID="your_project_id_here"
$env:IBM_WATSONX_URL="https://us-south.ml.cloud.ibm.com"

# Or add to .env file
```

#### Usage Example

```python
from src.agents.var_lens.rag_engine import VARLensRAG

# Initialize RAG engine
rag = VARLensRAG()
rag.load_vector_store()

# Create QA chain with IBM Granite
rag.create_qa_chain(
    provider="ibm_granite",
    model_name="ibm/granite-13b-chat-v2",  # Default
    temperature=0.7,
    max_tokens=500
)

# Ask questions
result = rag.query("What is VAR?")
print(result['answer'])
```

#### Available Models

- `ibm/granite-13b-chat-v2` (Default, recommended)
- `ibm/granite-13b-instruct-v2`
- `ibm/granite-20b-multilingual`

---

### OpenAI - For Quick Testing

OpenAI provides fast, high-quality responses ideal for development and testing.

#### Getting Started

1. **Get API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an API key
   - Copy and save it

2. **Set Environment Variable**

```powershell
# PowerShell
$env:OPENAI_API_KEY="sk-your_key_here"

# Or add to .env file
```

#### Usage Example

```python
from src.agents.var_lens.rag_engine import VARLensRAG

rag = VARLensRAG()
rag.load_vector_store()

# Create QA chain with OpenAI
rag.create_qa_chain(
    provider="openai",
    model_name="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.7,
    max_tokens=500
)

result = rag.query("When can VAR be used?")
print(result['answer'])
```

#### Available Models

- `gpt-4` - Most capable, higher cost
- `gpt-4-turbo` - Faster, lower cost
- `gpt-3.5-turbo` - Fast, economical

---

### HuggingFace - Free Alternative

Use open-source models via HuggingFace Inference API.

#### Getting Started

1. **Get API Token**
   - Go to [HuggingFace Settings](https://huggingface.co/settings/tokens)
   - Create a token with "Read" access
   - Copy and save it

2. **Set Environment Variable**

```powershell
$env:HUGGINGFACE_API_KEY="hf_your_token_here"
```

#### Usage Example

```python
from src.agents.var_lens.rag_engine import VARLensRAG

rag = VARLensRAG()
rag.load_vector_store()

# Create QA chain with HuggingFace
rag.create_qa_chain(
    provider="huggingface",
    model_name="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.7,
    max_tokens=500
)

result = rag.query("What are reviewable incidents?")
print(result['answer'])
```

#### Recommended Models

- `mistralai/Mistral-7B-Instruct-v0.2` (Default)
- `meta-llama/Llama-2-7b-chat-hf`
- `tiiuae/falcon-7b-instruct`

---

## Advanced Usage

### Using Multiple Providers

```python
from src.agents.var_lens.llm_providers import LLMFactory

# Create different LLM instances
granite_llm = LLMFactory.create_llm(
    provider="ibm_granite",
    model_name="ibm/granite-13b-chat-v2"
)

openai_llm = LLMFactory.create_llm(
    provider="openai",
    model_name="gpt-4"
)

# Use with RAG engine
rag = VARLensRAG()
rag.load_vector_store()

# Test with Granite
rag.create_qa_chain(llm=granite_llm)
result1 = rag.query("What is VAR?")

# Switch to OpenAI
rag.create_qa_chain(llm=openai_llm)
result2 = rag.query("What is VAR?")
```

### Custom LLM Parameters

```python
rag.create_qa_chain(
    provider="ibm_granite",
    model_name="ibm/granite-13b-chat-v2",
    temperature=0.5,        # Lower = more focused
    max_tokens=1000,        # Longer responses
    top_p=0.9,             # Nucleus sampling
    top_k=50,              # Top-k sampling
    decoding_method="sample"  # IBM-specific
)
```

### Error Handling

```python
try:
    rag.create_qa_chain(provider="ibm_granite")
except ValueError as e:
    print(f"Configuration error: {e}")
    # Missing API key or project ID
except ImportError as e:
    print(f"Missing dependency: {e}")
    # Need to install provider package
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Testing

### Test Individual Provider

```python
# Test IBM Granite
python scripts/test_var_lens_with_llm.py
```

The script will:
1. Check which providers are configured
2. Test each configured provider
3. Run sample questions
4. Display results and performance

### Test All Providers

Configure multiple providers in `.env`, then run:

```powershell
python scripts/test_var_lens_with_llm.py
```

---

## Troubleshooting

### "No module named 'ibm_watsonx_ai'"

```powershell
pip install ibm-watsonx-ai langchain-ibm
```

### "API key required"

Make sure environment variables are set:

```powershell
# Check if set
echo $env:IBM_WATSONX_API_KEY
echo $env:OPENAI_API_KEY

# Set if missing
$env:IBM_WATSONX_API_KEY="your_key"
```

### "Project ID required" (IBM Granite)

IBM Granite requires both API key and project ID:

```powershell
$env:IBM_WATSONX_PROJECT_ID="your_project_id"
```

### Rate Limits

If you hit rate limits:
- **OpenAI**: Upgrade to paid tier or reduce request frequency
- **HuggingFace**: Use Pro account or self-host models
- **IBM Granite**: Check your watsonx.ai plan limits

### Slow Responses

- Use faster models (e.g., `gpt-3.5-turbo` instead of `gpt-4`)
- Reduce `max_tokens` parameter
- Use local models for development

---

## Best Practices

### For Development
- Use OpenAI `gpt-3.5-turbo` for fast iteration
- Keep `max_tokens` low (200-500) for quick responses
- Use higher `temperature` (0.7-0.9) for creative answers

### For Production
- Use IBM Granite for the challenge submission
- Set `temperature` to 0.5-0.7 for consistent answers
- Implement caching for common questions
- Monitor API usage and costs

### For Testing
- Test with multiple providers to compare quality
- Use HuggingFace for free testing
- Validate answers against FIFA documents

---

## Next Steps

1. ✅ Set up at least one LLM provider (5 providers supported)
2. ✅ Test with `test_var_lens_with_llm.py` (All tests passing)
3. ✅ Integrate with Langflow (Template provided)
4. ✅ Build Tactical Pulse Agent (Complete with 10 metrics)
5. ✅ Create demo scenarios (5 comprehensive scenarios)
6. ✅ Deploy to GitHub (https://github.com/babaksh/FanPulse)
7. [ ] Submit to IBM Challenge

---

## Resources

- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review provider documentation
3. Check LangChain compatibility
4. Verify API keys and permissions