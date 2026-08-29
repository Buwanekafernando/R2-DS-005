# NeuroMark AI — Agentic Neuro-Marketing Strategy System

An AI system that turns a single product description into a complete marketing
strategy, built around four psychology-backed AI agents that each specialize
in a different principle of consumer behavior:

| # | Agent (research name) | Product-facing name | Theory | What it does |
|---|---|---|---|---|
| 1 | Dual-System Reasoning Agent | **Buying Psychology** | Dual Process Theory | Classifies whether a product is bought emotionally (System 1) or rationally (System 2), and writes marketing copy matched to that |
| 2 | Emotion Propagation Agent | **Emotional Appeal** | Emotional Contagion | Infuses a target emotion (joy, trust, confidence, etc.) into the copy, verified against its own RoBERTa emotion classifier |
| 3 | Scarcity Optimization Agent | **Urgency & Scarcity** | Scarcity Principle | Adds urgency (limited stock, time pressure) calibrated to the product, with a trust-safety check |
| 4 | Loss Framing Agent | **Loss-Framed Messaging** | Loss Aversion | Reframes the message around what the customer risks missing out on |

A fifth AI step — the **Final Recommendation** — reviews all four agents'
output together and writes one blended, ready-to-use message with a
plain-English rationale. This is the literal implementation of the original
proposal's workflow step: *"Outputs are synthesized into a final marketing
strategy."*

---

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │      React Frontend  (Vite dev server — localhost:5173)       │   │
│  │                                                                 │   │
│  │   Home · Main Application · Batch Mode · History ·             │   │
│  │   Buying Psychology · Urgency & Scarcity · Emotional Appeal    │   │
│  │                                                                 │   │
│  │   localStorage → saved form inputs, strategy history            │   │
│  └───────────────────────────┬─────────────────────────────────┘   │
└──────────────────────────────┼─────────────────────────────────────┘
                                │  HTTP / JSON (REST, CORS-enabled)
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend  (localhost:8000)                   │
│                          api/main.py                                 │
│                                                                       │
│   POST /generate-strategy   ← the orchestrator (calls all 4 agents)  │
│   POST /component1/*        POST /component3/*                      │
│   POST /component24/*       GET  /dataset/*   GET /health            │
└───┬──────────────┬──────────────────┬───────────────┬──────────────┘
    │               │                  │               │
    ▼               ▼                  ▼               ▼
┌─────────┐   ┌───────────┐     ┌───────────┐   ┌────────────┐
│Component1│   │ Component3│     │Component2 │   │ Component4 │
│ Buying   │   │  Urgency &│     │ Emotional │   │   Loss-    │
│Psychology│   │  Scarcity │     │  Appeal   │   │  Framed    │
│ (agent.py│   │ (scarcity_│     │(emotion_  │   │(loss_      │
│  .py)    │   │ agent.py) │     │agent.py)  │   │framing_    │
│          │   │           │     │           │   │agent.py)   │
└────┬─────┘   └─────┬─────┘     └─────┬─────┘   └─────┬──────┘
     │                │                 │               │
     ▼                ▼                 ▼               ▼
┌──────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│ RoBERTa   │   │ Decision   │   │ RoBERTa    │   │  VADER     │
│ Product   │   │ Tree       │   │ Emotion    │   │ Sentiment  │
│ Classifier│   │ Regressor  │   │ Classifier │   │ Analyzer   │
│ (local)   │   │ (local)    │   │ (local)    │   │ (local)    │
└──────────┘   └────────────┘   └─────┬──────┘   └────────────┘
     │                                 │
     └──────────────┬──────────────────┘
                     ▼
          ┌─────────────────────┐        ┌─────────────────────┐
          │   xAI / Grok API     │        │     Groq API         │
          │ (Component 1 copy +  │        │ (Components 2 & 4    │
          │  Final Recommendation│        │  copy generation)    │
          │  synthesis)          │        │                       │
          └─────────────────────┘        └─────────────────────┘
```

**Layers, top to bottom:**
- **Frontend (React + Vite)** — everything the user sees and interacts with. Talks to the backend only over HTTP; holds no business logic of its own beyond form state and display.
- **Backend (FastAPI)** — one process, one port (8000), one orchestrator endpoint that calls all four agents in the right order and returns one combined response. Also exposes each agent individually for standalone testing.
- **Agent layer** — four independent Python modules, each owning its own model-loading, prompting, and scoring logic. `component24_pipeline.py` chains Components 2 and 4 together since Component 4 always operates on Component 2's output.
- **Model layer** — two local RoBERTa models (loaded once at startup, run on CPU/GPU locally, no external call needed) and one local scikit-learn regressor (auto-trains on first run if missing), plus VADER (a rule-based library, not a trained model).
- **External AI services** — only copy *generation* leaves your machine: Component 1 and the Final Recommendation step call xAI's Grok API; Components 2 and 4 call Groq's API. Classification, scoring, and sentiment analysis all run locally and never touch either API.

---

## Agent Pipeline (Data Flow)

This is how a single product request actually flows through the four agents
and the synthesis step — showing what feeds into what, not just which
service each agent calls:

```
Product input
     │
     ▼
┌─────────────────────┐
│ 1. Buying Psychology │  classifies + writes base copy
└──────────┬───────────┘
           │  (base copy feeds forward into both branches below)
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌──────────────────┐
│ 3. Urgency│ │ 2. Emotional     │
│ & Scarcity│ │    Appeal        │
└─────────┘ └────────┬─────────┘
                      ▼
              ┌──────────────────┐
              │ 4. Loss-Framed    │
              │    Messaging      │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │ Final AI          │
              │ Recommendation    │  ← synthesizes all of the above
              └──────────────────┘
```

One FastAPI backend serves all four agents plus the synthesis step through a
single orchestrator endpoint (`POST /generate-strategy`). One React frontend
provides the full product experience — landing page, main application,
batch mode, history, and individual per-agent testing pages.

---

## Folder structure

```
neuromarketing-system/
├── .env.example / .gitignore / .gitattributes
├── requirements.txt
├── config/
│   └── .env                       ← you create this (see Setup)
├── models/                        ← you supply these (see Setup)
│   ├── roberta_checkpoint/            Component 1
│   ├── demographic_classifier.pkl     Component 1 (optional)
│   ├── fusion_meta_model.pkl          Component 1 (optional)
│   ├── demographic_feature_cols.pkl   Component 1 (optional)
│   ├── roberta_emotion_model/         Component 2
│   ├── scarcity_intensity_regressor.pkl   Component 3 (auto-trains if missing)
│   └── scarcity_scaler.pkl                Component 3 (auto-trains if missing)
├── dataset/
│   └── sample_products.json       ← used by Component 3's product picker
├── src/
│   ├── component1/         agent.py, generator.py, schemas.py
│   ├── component2/         emotion_agent.py, model_loader.py
│   ├── component3/         scarcity_agent.py, pain_point_extractor.py, review_reader.py
│   ├── component4/         loss_framing_agent.py
│   └── component24_pipeline.py    orchestrates Component 2 → Component 4
├── api/
│   ├── main.py             the unified FastAPI app — every endpoint lives here
│   └── schemas.py          shared Pydantic contract for all components
├── ui/                     original Streamlit prototypes (kept, not the primary UI)
│   ├── app_component1.py
│   ├── app_component3.py
│   └── components.py
└── frontend/                React app — the primary user-facing product
    └── src/
        ├── App.jsx                     tab routing
        ├── api.js                      API_BASE constant + fetch helpers
        ├── constants.js                categories, emotions, demographic
        │                                options — single source of truth,
        │                                mirrors backend mappings exactly
        ├── history.js                  localStorage strategy history
        ├── exportStrategy.js           downloadable .txt strategy export
        ├── usePersistedState.js        form-persistence hook
        ├── ErrorBoundary.jsx           catches runtime errors gracefully
        ├── components/
        │   ├── Nav.jsx                 top nav, live API health pill
        │   ├── Tooltip.jsx             inline "?" metric explanations
        │   ├── CopyButton.jsx          one-click copy-to-clipboard
        │   ├── ResultCode.jsx          collapsible raw JSON viewer
        │   ├── Component1Result.jsx    shared rich result card (Buying Psychology)
        │   ├── Component3Result.jsx    shared rich result card (Urgency & Scarcity)
        │   ├── Component24Result.jsx   shared rich result card (Emotional Appeal + Loss)
        │   └── FinalRecommendationCard.jsx  the synthesis step's display
        └── pages/
            ├── HomePage.jsx            landing page + results glossary
            ├── FullPipelinePage.jsx    "Main Application" — the primary flow
            ├── BatchPage.jsx           analyze up to 10 products at once
            ├── HistoryPage.jsx         browse/reopen/delete past strategies
            ├── Component1Page.jsx      standalone Buying Psychology testing
            ├── Component3Page.jsx      standalone Urgency & Scarcity testing
            └── Component24Page.jsx     standalone Emotional Appeal + Loss testing
```

---

## Setup

### 1. Python backend

```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
```

### 2. Environment variables

```bash
cp config/.env.example config/.env
```

Edit `config/.env`:
```
XAI_API_KEY=xai-your-key-here     # Component 1's copy generation (Grok)
GROQ_API_KEY=gsk-your-key-here    # Components 2 & 4 (Groq)
```

### 3. Model files

Copy these into `models/` (not included in the repo — see **Git setup** below):

| File/folder | Required for | Notes |
|---|---|---|
| `roberta_checkpoint/` | Component 1 | RoBERTa product classifier |
| `demographic_classifier.pkl`, `fusion_meta_model.pkl`, `demographic_feature_cols.pkl` | Component 1 | Optional — falls back to RoBERTa-only without them |
| `roberta_emotion_model/` | Component 2 | RoBERTa emotion classifier |
| `scarcity_intensity_regressor.pkl`, `scarcity_scaler.pkl` | Component 3 | **Don't copy these manually** — auto-trains on first run |

### 4. Frontend

```bash
cd frontend
npm install
```

---

## Running it

Two terminals:

```bash
# Terminal 1 — backend
uvicorn api.main:app --reload
```
```bash
# Terminal 2 — frontend
cd frontend
npm run dev
```

Backend: `http://localhost:8000` (Swagger docs at `/docs`)
Frontend: `http://localhost:5173`

The nav bar's top-right pill shows live API connection status.

---

## Using the app

- **Home** — explains the app and each agent in plain language, with a
  results glossary (what "confidence score," "sentiment," "FOMO score," etc.
  actually mean) for non-technical users.
- **Main Application** — the primary flow. One form (product details +
  customer profile) → calls `/generate-strategy` → shows all four agents'
  full output plus the Final Recommendation, all on one page. Auto-saves to
  History. Includes a downloadable `.txt` export and an AI-content
  disclaimer.
- **Batch Mode** — analyze up to 10 products at once (Buying Psychology
  only, for speed — not the full four-agent pipeline per product).
- **History** — every strategy generated on the Main Application page is
  saved locally (last 25) and can be reopened or deleted.
- **Buying Psychology / Urgency & Scarcity / Emotional Appeal + Loss** —
  standalone pages for testing one agent in isolation, useful for research
  documentation and debugging.

---

## API reference

All endpoints are on the single FastAPI app (`api/main.py`):

| Endpoint | Purpose |
|---|---|
| `POST /generate-strategy` | **The orchestrator.** Runs all four agents + the final synthesis in one call. |
| `POST /component1/analyze` | Buying Psychology only |
| `POST /component1/classify-only` | Classification without copy generation |
| `POST /component1/batch-analyze` | Up to 10 products at once |
| `POST /component1/channel-variants` | Reformats a winning copy into Social Media / Product Listing / Email versions |
| `POST /component3/analyze` | Urgency & Scarcity only |
| `POST /component3/extract-pain-points` | Keyword-based pain-point extraction from product text |
| `POST /component24/pipeline` | Emotional Appeal + Loss-Framed Messaging only |
| `GET /dataset/sample-products` | Serves `sample_products.json` for the product picker |
| `GET /health` | Health check |

Full interactive documentation: `http://localhost:8000/docs`

---

## Key design decisions (useful for your report/panel defense)

- **Components 1 → 3 and 1 → 2 → 4 are genuinely connected**, not just run
  in parallel from the same input. Component 1's `recommended_copy` is the
  literal `base_copy` both Component 3 and Component 2 build on — you can
  verify this in any `/generate-strategy` response via
  `component3.final_copy` containing Component 1's sentence, and
  `component24.base_copy_used` showing exactly what was fed forward.
- **The Final Recommendation is a real fifth AI call**, not a UI
  concatenation — it's prompted as "a lead strategist reviewing four
  specialist analysts' work" and asked to blend the strongest elements into
  something new, with a parsed rationale and usage guidance.
- **The scarcity model was recalibrated** after testing showed it almost
  always recommended HIGH intensity regardless of product — the root cause
  was price-bucket thresholds built for USD being applied to LKR prices,
  plus a category-matching bug that silently defaulted most real category
  names to a generic score. Both are fixed; the model now produces a
  realistic LOW/MEDIUM/HIGH spread, with MEDIUM as the common baseline and
  HIGH reserved for genuine urgency signals (detected pain points like
  stock instability).
- **Category-to-emotion mapping is unified** between frontend and backend
  (`frontend/src/constants.js` mirrors `src/component2/emotion_agent.py`'s
  `CATEGORY_EMOTION_MAP` exactly) — an earlier mismatch meant selecting
  "Pet Products" or "Grocery" silently fell back to Beauty's emotion list.
- **Error messages are plain-language**, not raw exception text — a
  `friendly_error()` helper in `api/main.py` logs the real technical error
  server-side but returns something a non-technical user can act on.

## Known scope limitations

- Batch Mode only runs Buying Psychology, not the full four-agent pipeline,
  to keep it fast and affordable for multiple products at once.
- Strategy export is plain text, not a formatted PDF/Word document —
  kept dependency-free rather than adding a PDF library.
- History and form persistence are stored in the browser's `localStorage`
  only — clearing browser data removes them; there's no server-side account
  system.

---

## Git / GitHub setup

`.gitignore` excludes `.env` and the entire `models/` folder (trained model
files are too large for a normal GitHub repo). `.gitattributes` routes
`.safetensors`/`.pkl` through Git LFS for the rare case you do commit one
deliberately.

**Because `models/` is gitignored, anyone who clones this repo — including
your panel — will need the model files supplied separately** (a shared
Drive link is the usual approach for a project this size). Worth noting
where they're hosted in your final report.
