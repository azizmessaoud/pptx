# ALIA PPTX Agent

Standalone Python agent that generates pharmaceutical product presentation decks (.pptx) powered by **Groq LLaMA 3.3 70B** + **MckEngine** layouts.

Scores **97–99/100** on QA with 0 errors after autofix pipeline.

---

## ⚠️ Important — Mock Data Notice

The current built-in contexts (`fersang`, `fersang_training`) are **mock/hardcoded data for development and testing only**.

- `fersang` → static product facts (indication, dosage, mechanism)
- `fersang_training` → fake rep session (Ahmed Ben Ali, hardcoded scores)

**In production, these must be replaced by real context retrieved from the ALIA RAG pipeline** (Pinecone + LangGraph). The agent itself is context-agnostic — `context` is just a string. See [RAG Integration](#rag-integration-alia-backend) below.

---

## What It Does

Given a product name + context (text) + language, the agent:
1. Calls an LLM to produce a structured JSON slide plan in the selected language
2. Renders it into a fully formatted `.pptx` file using McKinsey-style layouts
3. Runs an autofix QA pass (font overflow, whitespace, narrative density)

### Two Modes
| Mode | Use Case | Layouts Used |
|------|----------|-------------|
| `mode1` | Rep training recap (scores + XAI + coaching) | data_table, pros_cons, vertical_steps, key_takeaway |
| `mode2` | Doctor-facing product sheet (indication, dosage, safety) | bullet_2col, vertical_steps, data_table, pros_cons, key_takeaway |

### Four Languages
| Code | Language | Status |
|------|----------|--------|
| `FR` | French | ✅ Default |
| `EN` | English | ✅ |
| `AR` | Arabic | ✅ |
| `ES` | Spanish | ✅ |

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/azizmessaoud/pptx.git
cd pptx
```

### 2. Install dependencies
```bash
pip install openai python-pptx lxml python-dotenv json-repair
```

### 3. Get a free Groq API key
Go to [console.groq.com](https://console.groq.com) → API Keys → Create Key

### 4. Create `.env` (never commit this)
```
GROQ_API_KEY=your-groq-key-here
```

> Use Python to create it on Windows to avoid encoding issues:
> ```powershell
> python -c "f=open('.env','w',encoding='utf-8'); f.write('GROQ_API_KEY=your-key'); f.close()"
> ```

### 5. Run
```bash
# product sheet (French, default)
python agent.py Fersang FR mode2

# training recap (English)
python agent.py fersang_training EN mode1

# all 4 languages
python agent.py Fersang FR mode2
python agent.py Fersang EN mode2
python agent.py Fersang AR mode2
python agent.py Fersang ES mode2
```

Output saved to: `output/<product>_<mode>_<timestamp>.pptx`

---

## Project Structure

```
pptx/
├── agent.py           # CLI entry point + mock contexts (DEV ONLY)
├── slide_planner.py   # Groq API call → JSON slide plan
├── renderer.py        # JSON plan → .pptx via MckEngine
├── prompts/
│   ├── mode1.txt      # System prompt: training recap (FR/EN/AR/ES)
│   └── mode2.txt      # System prompt: doctor-facing product sheet (FR/EN/AR/ES)
├── mck_ppt/           # McKinsey-style layout engine
├── products/          # (future) Per-product RAG context files
└── output/            # Generated .pptx files (gitignored)
```

---

## Adding a New Product (Development)

Create `products/<product_name>.txt` with medical context:

```
Product: Amoxil (Amoxicillin 500mg)
Indication: Bacterial infections
Mechanism: Beta-lactam antibiotic — inhibits cell wall synthesis
Dosage: Adults 500mg every 8h, Children 25mg/kg/day
Contraindications: Penicillin allergy
Side effects: Diarrhea, rash, nausea
```

Then run:
```bash
python agent.py Amoxil FR mode2
```

The agent auto-discovers files in `products/` — no code changes needed.

---

## RAG Integration (ALIA Backend)

The agent is context-agnostic — `context` is just a string.
When plugged into ALIA's RAG pipeline, replace mock contexts with retrieved chunks.

### Option A — Direct Python call (simplest)

```python
from agent import generate_deck

def slide_deck_node(state: ALIAState) -> ALIAState:
    # 1. Retrieve context from RAG
    product_chunks = pinecone_retriever.query(
        query=f"{state['product']} indication dosage safety",
        top_k=8
    )
    context = "\n".join([c["text"] for c in product_chunks])

    # 2. Generate deck in rep's language
    output_path = f"output/{state['rep_id']}_{state['product']}.pptx"
    generate_deck(
        topic=f"{state['product']} — Fiche Produit",
        context=f"Language: {state['lang']}\n\n{context}",
        mode="mode2",
        output=output_path
    )

    state["deck_url"] = upload_to_s3(output_path)
    return state
```

### Option B — FastAPI microservice

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agent import generate_deck

app = FastAPI()

class DeckRequest(BaseModel):
    topic: str
    context: str        # RAG-retrieved text from ALIA gateway
    lang: str = "FR"    # FR / EN / AR / ES
    mode: str = "mode2"
    output: str = "output/deck.pptx"

@app.post("/generate")
def generate(req: DeckRequest):
    path = generate_deck(
        req.topic,
        f"Language: {req.lang}\n\n{req.context}",
        req.mode,
        req.output
    )
    return {"path": path}
```

### Context Format (what to pass from RAG)

**mode2** (product sheet) — retrieve:
- Product monograph: indication, mechanism, dosage, contraindications
- Clinical study summaries (keep under 12 words per bullet)

**mode1** (training recap) — pass:
- Session scores (JSON stringified)
- Last 3–5 objections from call transcript
- XAI strengths/weaknesses from analytics layer
- Rep name + session date

---

## QA Results (latest runs)

| Language | Mode | Score | Errors |
|----------|------|-------|--------|
| FR | mode2 | 99/100 | 0 |
| EN | mode2 | 99/100 | 0 |
| AR | mode2 | 98/100 | 0 |
| ES | mode2 | 94–99/100 | 0 |
| FR | mode1 | 97/100 | 0 |
| ES | mode1 | 97/100 | 0 |

---

## Notes

- `.env` is gitignored — never commit your API key
- `output/` is gitignored — decks are never versioned
- `fersang` and `fersang_training` contexts in `agent.py` are **mock data** — replace with RAG in production
- MckEngine `autofix` runs up to 5 rounds of font correction automatically
- To switch LLM provider, only edit `slide_planner.py` — everything else stays the same
