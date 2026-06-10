# Langflow Quick Start Guide

## What is Langflow?

Langflow is a visual tool for building AI workflows. Think of it as "drag and drop" for creating AI agents.

## Starting Langflow

```bash
# Start Langflow server
langflow run

# Opens at: http://localhost:7860
```

## Importing VAR-Lens Flow

### Option 1: Import JSON Template

1. Open Langflow at `http://localhost:7860`
2. Click "Import" button (top right)
3. Select: `langflow_flows/var_lens_agent_template.json`
4. Flow will load with all components

### Option 2: Build Manually

Follow the step-by-step guide in [`langflow-var-lens-guide.md`](langflow-var-lens-guide.md)

## Flow Components Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    VAR-Lens Flow                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [1] Directory Loader                                        │
│      ↓                                                        │
│  [2] Text Splitter                                           │
│      ↓                                                        │
│  [3] Embeddings ──→ [4] FAISS Vector Store                  │
│                          ↓                                    │
│  [5] Chat Input ──→ [6] Retriever                           │
│                          ↓                                    │
│                     [7] Prompt Template                      │
│                          ↓                                    │
│                     [8] LLM (OpenAI/Granite)                 │
│                          ↓                                    │
│                     [9] Chat Output                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Steps

### 1. Set API Keys

Before running, you need to set your API key:

**For OpenAI:**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

**For IBM Granite:**
```bash
# Windows PowerShell
$env:IBM_CLOUD_API_KEY="your-ibm-key"
$env:IBM_WATSONX_PROJECT_ID="your-project-id"

# Linux/Mac
export IBM_CLOUD_API_KEY="your-ibm-key"
export IBM_WATSONX_PROJECT_ID="your-project-id"
```

### 2. Update File Paths

In Langflow UI, update the Directory Loader path:
- Current: `data/processed_documents`
- Update to: Full path like `D:/MyPythonProjects/FanPulse/data/processed_documents`

### 3. Test the Flow

1. Click "Build" button (bottom right)
2. Wait for build to complete (~30 seconds)
3. Click "Playground" button
4. Type a question: "What is VAR?"
5. Press Enter
6. See the answer with sources!

## Sample Questions to Test

### Basic Questions
- "What is VAR?"
- "When can VAR be used?"
- "What are the reviewable incidents?"

### Specific Scenarios
- "Why was that goal disallowed for offside?"
- "Can VAR review a yellow card decision?"
- "What happens if the referee makes a clear and obvious error?"

### Rule Clarifications
- "Explain the offside rule"
- "What is handball in the penalty area?"
- "When is a foul considered violent conduct?"

## Troubleshooting

### Issue: "No documents loaded"
**Solution:** Check the file path in Directory Loader
```
Correct: D:/MyPythonProjects/FanPulse/data/processed_documents
Wrong: data/processed_documents (relative path may not work)
```

### Issue: "Embeddings taking too long"
**Solution:** First run takes 5-10 seconds to download model. Subsequent runs are fast.

### Issue: "LLM not responding"
**Solution:** Check API key is set correctly
```bash
# Test API key
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: "Vector store error"
**Solution:** Build vector store first
```bash
python scripts/build_var_lens_vectorstore.py
```

## Advanced: Using IBM Granite

To use IBM Granite instead of OpenAI:

1. In Langflow, replace "ChatOpenAI" node with "WatsonxLLM"
2. Configure:
   - Model: `ibm/granite-13b-chat-v2`
   - API Key: From environment variable
   - Project ID: From environment variable
3. Build and test

## Exporting Your Flow

After building and testing:

1. Click "Export" button
2. Choose "JSON"
3. Save as: `langflow_flows/var_lens_agent_v1.json`
4. This can be shared or version controlled

## Integration with FastAPI

Once your flow works in Langflow:

1. Get the Flow ID from URL
2. Use Langflow REST API:

```python
import requests

response = requests.post(
    "http://localhost:7860/api/v1/run/{flow_id}",
    json={
        "inputs": {"message": "What is VAR?"},
        "tweaks": {}
    }
)

print(response.json())
```

## Performance Tips

1. **First Query:** Slow (~10 seconds) - loading embeddings
2. **Subsequent Queries:** Fast (~2-3 seconds)
3. **Batch Processing:** Process multiple questions together
4. **Caching:** Langflow caches results automatically

## Next Steps

1. ✅ Import flow template
2. ✅ Set API keys
3. ✅ Test with sample questions
4. ⏳ Customize prompt for your needs
5. ⏳ Add more documents if needed
6. ⏳ Integrate with FastAPI
7. ⏳ Deploy to production

## Resources

- [Langflow Documentation](https://docs.langflow.org)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)

---

**Last Updated:** 2026-06-10  
**Status:** Ready to use 🚀