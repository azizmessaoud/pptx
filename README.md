# ALIA PPTX Agent

Standalone Python agent that generates pharmaceutical product presentation decks (.pptx) powered by **Groq LLaMA 3.3 70B** + **MckEngine** layouts.

Scores **99/100** on QA with 0 errors after autofix pipeline.

---

## What It Does

Given a product name + context (text), the agent:
1. Calls an LLM to produce a structured JSON slide plan
2. Renders it into a fully formatted `.pptx` file using McKinsey-style layouts
3. Runs an autofix QA pass (font overflow, whitespace, narrative density)

### Two Modes
| Mode | Use Case | Layouts Used |
|------|----------|-------------|
| `mode1` | Rep training recap (scores + XAI + coaching) | data_table, pros_cons, vertical_steps, key_takeaway |
| `mode2` | Doctor-facing product sheet (indication, dosage, safety) | bullet_2col, vertical_steps, data_table, pros_cons, key_takeaway |

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/azizmessaoud/pptx.git
cd pptx
```

### 2. Install dependencies
```bash
pip install openai python-pptx lxml python-dotenv
```

### 3. Get a free Groq API key
Go to [console.groq.com](https://console.groq.com) → API Keys → Create Key

### 4. Create `.env`
```
GROQ_API_KEY=your-groq-key-here
```

### 5. Run
```bash
python agent.py
```

Output: `output/fersang_mode2.pptx`

---

## Project Structure

```
pptx/
├── agent.py           # Orchestrator — call generate_deck() from here
├── slide_planner.py   # LLM call → JSON slide plan
├── renderer.py        # JSON plan → .pptx via MckEngine
├── prompts/
│   ├── mode1.txt      # System prompt: training recap
│   └── mode2.txt      # System prompt: doctor-facing product sheet
├── mck_ppt/           # Local MckEngine layout library
└── output/            # Generated .pptx files (gitignored)
```

---

## Generating a Deck

```python
from agent import generate_deck

generate_deck(
    topic="Fersang — Fiche Produit",
    context="""
    Product: Fersang (Cholécalciférol — Vitamin D3 1000 UI)
    Indication: Vitamin D deficiency, osteoporosis prevention
    Dosage: Adults 1 tablet/day, Elderly 2 tablets/day
    Contraindications: Hypercalcemia, severe renal insufficiency
    """,
    mode="mode2",               # or "mode1" for training recap
    output="output/deck.pptx"
)
```

---

## RAG Integration (ALIA Backend)

The agent is designed to be context-agnostic — `context` is just a string.
When plugged into ALIA's RAG pipeline, replace the hardcoded context with retrieved chunks.

### Option A — Direct Python call (simplest)

```python
# In your LangGraph SlideDeckAgent node:
from agent import generate_deck

def slide_deck_node(state: ALIAState) -> ALIAState:
    # 1. Retrieve context from RAG
    product_chunks = pinecone_retriever.query(
        query=f"{state['product']} indication dosage safety",
        top_k=8
    )
    context = "\n".join([c["text"] for c in product_chunks])

    # 2. Generate deck
    output_path = f"output/{state['rep_id']}_{state['product']}.pptx"
    generate_deck(
        topic=f"{state['product']} — Fiche Produit",
        context=context,
        mode="mode2",
        output=output_path
    )

    # 3. Upload to S3 and store URL
    state["deck_url"] = upload_to_s3(output_path)
    return state
```

### Option B — FastAPI microservice

Wrap the agent as an endpoint the ALIA gateway can call:

```python
# pptx_service.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import generate_deck

app = FastAPI()

class DeckRequest(BaseModel):
    topic: str
    context: str        # RAG-retrieved text, passed from gateway
    mode: str = "mode2"
    output: str = "output/deck.pptx"

@app.post("/generate")
def generate(req: DeckRequest):
    path = generate_deck(req.topic, req.context, req.mode, req.output)
    return {"path": path}
```

Run with:
```bash
pip install fastapi uvicorn
uvicorn pptx_service:app --port 8001
```

Call from ALIA gateway:
```python
import httpx
resp = httpx.post("http://localhost:8001/generate", json={
    "topic": "Fersang — Fiche Produit",
    "context": rag_context,   # from Pinecone retriever
    "mode": "mode2",
    "output": f"output/{rep_id}_fersang.pptx"
})
```

### Context Format (what to feed from RAG)

For **mode2** (product sheet), retrieve and concatenate:
- Product monograph sections: indication, mechanism, dosage, contraindications
- Clinical study summaries (keep under 12 words per item)

For **mode1** (training recap), pass:
- Session scores JSON stringified
- Last 5 objections from transcript
- Rep performance summary from analytics layer

---

## QA Results

| Metric | Value |
|--------|-------|
| Layout score | 99/100 |
| Errors | 0 |
| Warnings | 1 (cover whitespace — expected) |
| Slides generated | 8 |
| Generation time | ~3–5s (Groq) |

---

## Notes

- `.env` is gitignored — never commit your API key
- `output/` is gitignored — decks are not versioned
- MckEngine `autofix` runs up to 5 rounds of font size correction automatically
- To switch LLM provider, edit `slide_planner.py` — the rest is unchanged
