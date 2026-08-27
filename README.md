# Neuro-Marketing System — Component 1 + Component 3 Integration

This is the merged project combining:
- **Component 1** — Dual-System Reasoning Agent
- **Component 3** — Scarcity Optimization Agent

connected through one FastAPI backend at `api/main.py`, via a new
`POST /generate-strategy` endpoint that runs both agents in sequence.

## Folder structure

```
neuromarketing-system/
├── config/
│   └── .env.example          → rename to .env, add XAI_API_KEY and GROQ_API_KEY
├── models/                   → YOU MUST COPY THESE IN (see below)
│   ├── roberta_checkpoint/            (Component 1)
│   ├── demographic_classifier.pkl     (Component 1)
│   ├── fusion_meta_model.pkl          (Component 1)
│   ├── demographic_feature_cols.pkl   (Component 1)
│   ├── roberta_emotion_model/         (Component 2) ⚠️ NOT YET PROVIDED
│   ├── scarcity_intensity_regressor.pkl   (Component 3, auto-trains on first run)
│   └── scarcity_scaler.pkl                (Component 3, auto-trains on first run)
├── src/
│   ├── component1/
│   │   ├── agent.py
│   │   ├── schemas.py
│   │   └── generator.py
│   ├── component2/
│   │   ├── emotion_agent.py      ← from her utils/emotion_agent.py (unchanged)
│   │   └── model_loader.py       ← from her utils/model_loader.py (path fixed)
│   ├── component3/
│   │   ├── scarcity_agent.py
│   │   ├── pain_point_extractor.py
│   │   └── review_reader.py
│   ├── component4/
│   │   └── loss_framing_agent.py ← from her utils/loss_framing_agent.py (import fixed)
│   └── component24_pipeline.py   ← from her pipeline.py (imports fixed) — orchestrates C2 -> C4
├── api/
│   ├── schemas.py            ← shared contract for all 4 components
│   └── main.py                ← unified FastAPI app — the actual C1+C2+C3+C4 connection point
├── ui/
│   ├── components.py
│   ├── app_component1.py     (Streamlit)
│   └── app_component3.py     (Streamlit)
├── dataset/
│   └── sample_products.json
├── requirements.txt
└── README.md
```

Note: your friend's original `app.py` (Flask) is **not** included — its two routes
(`/health`, `/api/pipeline`) were ported directly into the unified `api/main.py`
as `/health` and `/component24/pipeline`, so there's only one backend server now,
not two. Her React frontend (`frontend/`) isn't merged yet — see the note at the
bottom of this file.

## What you need to add before running

1. **`models/roberta_checkpoint/`** — Component 1's trained RoBERTa classifier folder
2. **`models/demographic_classifier.pkl`, `fusion_meta_model.pkl`, `demographic_feature_cols.pkl`** — Component 1 (optional)
3. **`models/roberta_emotion_model/`** — Component 2's trained RoBERTa emotion classifier folder (not yet uploaded — ask your friend for this folder, it should contain the same kind of files as Component 1's checkpoint: config, model weights, tokenizer files, plus a `label_mapping.json`)
4. **`config/.env`** — copy from `.env.example`, fill in both `XAI_API_KEY` (Component 1) and `GROQ_API_KEY` (Components 2 & 4)
5. **`dataset/sample_products.json`** (optional, Component 3 UI only)

Everything else — all four components' code, the orchestrator, and both existing
Streamlit UIs — is in place and verified working (Component 2 and 4's non-LLM
logic — prompt building, sentiment scoring, FOMO detection, emotion selection —
was tested directly against this file structure).

Component 3's own `.pkl` model files (`scarcity_intensity_regressor.pkl`, `scarcity_scaler.pkl`) don't need to be copied — `ScarcityAgent` trains and saves them automatically into `models/` the first time it runs if they're not already there.

## How all four components are actually connected

`api/main.py` loads all agents/models once at startup:

```python
agent1 = DualSystemAgent(...)               # Component 1
agent3 = ScarcityAgent(...)                 # Component 3
load_emotion_model(...)                     # Component 2's RoBERTa
```

`POST /generate-strategy` is the full pipeline:

1. **Component 1** classifies the product (System 1 / System 2) and generates `recommended_copy`
2. **Component 3** takes that `recommended_copy` as its `base_copy`, layers on scarcity messaging using `price`, `category`, and extracted pain points
3. **Component 2 → Component 4** run as a connected pipeline fed directly by Component 1's `recommended_copy`: Component 2 infuses the target emotion into that existing copy (rather than writing unrelated copy from scratch) via a generate-verify-refine loop against its own RoBERTa emotion classifier, then Component 4 reframes *that* output as loss-averse messaging and re-checks with Component 2's classifier whether the target emotion survived
4. All four components' outputs are returned together in one JSON response, and the response includes `component24.base_copy_used` so you can see exactly what Component 1 output was fed forward

This now matches your original proposal's architecture: Component 1 → parallel fan-out to Components 2, 3, and 4, all building on the same cognitively-aligned base copy.

Individual endpoints are also available if you need to call one component's pipeline directly:
- `POST /component1/analyze`, `/component1/classify-only`, `/component1/batch-analyze`
- `POST /component3/analyze`
- `POST /component24/pipeline` — matches your friend's original `/api/pipeline` contract exactly (`product_name`, `category`, `target_audience`, `features`, `target_emotion`), so her React frontend can call this unified backend without changes to its request format — just update its base URL if it currently points at a separate Flask server.

## Running it

```bash
pip install -r requirements.txt --break-system-packages   # if needed
cp config/.env.example config/.env                        # then edit in your real keys
uvicorn api.main:app --reload
```

Then test the full four-agent orchestrator:

```bash
curl -X POST http://localhost:8000/generate-strategy \
  -H "Content-Type: application/json" \
  -d '{
        "product_name": "Sony WH-1000XM5 Headphones",
        "product_text": "Sony WH-1000XM5 with 30hr battery. Stock sells out fast.",
        "category": "Electronics",
        "price": 899.00,
        "target_audience": "commuters and remote workers",
        "features": "active noise cancellation, 30h battery, comfortable fit"
      }'
```

Or visit `http://localhost:8000/docs` for interactive Swagger docs of every endpoint.

## Frontend — unified React app

All four components now share **one React frontend** (`frontend/`), replacing
the two Streamlit UIs and the standalone C2+4 React app with a single
tabbed application:

```
frontend/
├── src/
│   ├── App.jsx                    ← tab navigation, shares Component 1's
│   │                                 result across pages
│   ├── api.js                     ← single API_BASE constant (localhost:8000)
│   ├── index.css                  ← shared design system (ported from the
│   │                                 original Component 1 Streamlit CSS)
│   ├── components/
│   │   └── Nav.jsx                ← top nav, tabs, live API health pill
│   └── pages/
│       ├── Component1Page.jsx     ← React port of ui/app_component1.py
│       ├── Component3Page.jsx     ← React port of ui/app_component3.py
│       ├── Component24Page.jsx    ← your friend's Integrate.jsx, endpoint
│       │                             updated to /component24/pipeline
│       └── FullPipelinePage.jsx   ← NEW — calls /generate-strategy and
│                                     shows all four agents' output together
```

**Component 1 → 2/3/4 connection now works in the UI too:** once you run an
analysis on the Component 1 tab, its `recommended_copy` is held in React
state and offered as the pre-filled starting point on the Component 3 and
Component 2+4 tabs (editable, not forced) — mirroring what the backend
orchestrator already does automatically on the Full Pipeline tab.

Two small backend additions were needed to support this (both in `api/main.py`):
- `GET /dataset/sample-products` — serves `sample_products.json` so the
  Component 3 page's product picker works without bundling the dataset
  into the frontend separately
- `POST /component3/extract-pain-points` — exposes pain-point extraction
  as its own endpoint, since the React page can't call Python functions
  directly the way Streamlit could
- `POST /component3/analyze` was also fixed to accept a proper JSON body
  (it previously took a bare `list[str]` parameter, which doesn't parse
  correctly from a JSON POST)

### Running the frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. Make sure the backend is running first
(`uvicorn api.main:app --reload` from the project root, in a separate
terminal) — the top-right pill in the nav bar shows live API status.

**Scope note:** this covers the core single-product flow for each
component. Component 1's batch-analysis mode (multiple products at once)
from the original Streamlit app wasn't ported — say the word if you want
that added too.

The two original Streamlit UIs (`ui/app_component1.py`, `ui/app_component3.py`)
are left in place and still work standalone if you ever want them, but the
React app is now the primary frontend for the full system.
