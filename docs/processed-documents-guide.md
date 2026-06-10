# Processed FIFA Documents Guide

## Overview

This guide explains the FIFA documents that have been processed using Docling and how to use them in the VAR-Lens Agent.

## Processed Documents

### 1. Changes to the Laws of the Game 2026/27
**File**: `data/processed_documents/Changes to the Laws of the Game 2026_27.md`

**Content**:
- Recent changes to FIFA Laws of the Game
- VAR protocol updates
- Player equipment rules
- Referee guidelines
- Substitution rules

**Key VAR-Related Content**:
- Line 24-25: VAR review capabilities including incorrect red cards
- Line 29-30: VAR can review wrongly identified players
- Line 30: Optional corner kick reviews

**Use Case**: Explaining recent rule changes and VAR protocol updates

---

### 2. Laws of the Game 2026/27 (Main Document)
**File**: `data/processed_documents/Laws of the Game 2026_27.md` (Processing...)

**Expected Content**:
- Complete FIFA Laws of the Game
- All 17 laws in detail
- Detailed VAR protocols
- Offside rules
- Penalty kick procedures

**Use Case**: Primary reference for all game rules and VAR decisions

---

### 3. VAR Protocol
**File**: `data/processed_documents/Video Assistant Referee (VAR) protocol _ IFAB.md` (Processing...)

**Expected Content**:
- Complete VAR protocol
- Reviewable incidents
- VAR decision-making process
- Communication protocols
- Review procedures

**Use Case**: Core document for VAR-Lens Agent - explains all VAR decisions

---

### 4. FIFA World Cup 2026 Regulations
**File**: `data/processed_documents/FWC26_regulations_EN.md` (Processing...)

**Expected Content**:
- Tournament-specific rules
- Competition format
- Player eligibility
- Match procedures

**Use Case**: Tournament-specific context for World Cup matches

---

### 5. Protocol Documents
**Files**:
- `Off-field treatment and assessment protocol.md` (Processing...)
- `Throw-in and goal-kick countdown protocol.md` (Processing...)
- `Time-limited substitution protocol.md` (Processing...)

**Expected Content**:
- Specific protocols for various game situations
- Medical treatment procedures
- Time management rules

**Use Case**: Detailed explanations for specific game situations

---

## Document Structure

All processed documents follow this structure:

```markdown
# Headings (H1, H2, H3)
- Bullet points for lists
- Numbered lists for procedures
- Tables for comparisons
- Code blocks for specific rules
```

## Using Documents in VAR-Lens Agent

### Step 1: Load Documents into Vector Store

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Load all markdown files
loader = DirectoryLoader(
    "data/processed_documents",
    glob="**/*.md",
    show_progress=True
)
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

# Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector store
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("data/vector_stores/fifa_rules")
```

### Step 2: Query in Langflow

In Langflow, use the FAISS vector store component:

1. **Vector Store Component**:
   - Type: FAISS
   - Path: `data/vector_stores/fifa_rules`
   - Embeddings: HuggingFace (all-MiniLM-L6-v2)

2. **Retriever Component**:
   - Search Type: Similarity
   - K (number of results): 4-6
   - Score Threshold: 0.7

3. **Prompt Template**:
```
You are a VAR (Video Assistant Referee) expert explaining decisions to fans.

Context from FIFA Rules:
{context}

User Question: {question}

Provide a clear, accurate explanation based on the official FIFA rules above.
Include:
1. The relevant rule/law
2. Why the decision was made
3. Any exceptions or special cases

Answer:
```

### Step 3: Example Queries

**Query 1**: "Why was the goal disallowed for offside?"
- Retrieves: Offside rules, VAR protocol for offside
- Explains: Offside position, when VAR intervenes, how decision is made

**Query 2**: "Can VAR review a yellow card?"
- Retrieves: VAR reviewable incidents, card protocols
- Explains: What VAR can/cannot review regarding cards

**Query 3**: "What happens if the goalkeeper moves before a penalty?"
- Retrieves: Penalty kick laws, goalkeeper rules
- Explains: Legal goalkeeper movement, consequences of violations

---

## Document Quality

### Strengths
✅ Clean markdown formatting
✅ Preserved structure (headings, lists, tables)
✅ Accurate text extraction
✅ Maintained references and cross-links

### Limitations
⚠️ Some images converted to `<!-- image -->` placeholders
⚠️ Complex diagrams may need manual review
⚠️ Tables might need formatting adjustments

---

## Next Steps

1. ✅ Wait for all PDFs to finish processing
2. ⏳ Review processed documents for quality
3. ⏳ Create vector store from all documents
4. ⏳ Build Langflow flow with vector store
5. ⏳ Test queries and refine prompts
6. ⏳ Integrate with FastAPI backend

---

## Troubleshooting

### Issue: Memory errors during processing
**Solution**: Use `process_fifa_docs_simple.py` with optimized settings

### Issue: Poor quality extraction
**Solution**: Check original PDF quality, may need OCR for scanned documents

### Issue: Missing content
**Solution**: Verify PDF is text-based, not image-based

---

## References

- Docling Documentation: https://github.com/DS4SD/docling
- IFAB Laws of the Game: https://www.theifab.com/laws
- VAR Protocol: https://www.theifab.com/laws/var-protocol