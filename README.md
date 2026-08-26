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
│   └── .env.example          → rename to .env, add your XAI_API_KEY
├── models/                   → YOU MUST COPY THESE IN (see below)
│   ├── roberta_checkpoint/
│   ├── demographic_classifier.pkl
│   ├── fusion_meta_model.pkl
│   ├── demographic_feature_cols.pkl
│   ├── scarcity_intensity_regressor.pkl   (auto-trains on first run if missing)
│   └── scarcity_scaler.pkl                (auto-trains on first run if missing)
├── src/
│   ├── component1/
│   │   ├── agent.py          ← from Component 1's src/agent.py (paths fixed)
│   │   ├── schemas.py        ← from Component 1's schemas.py
│   │   └── generator.py      ← from Component 1's src/generator.py (BASE_DIR path fixed)
│   └── component3/
│       ├── scarcity_agent.py       ← from Component 3's utils/scarcity_agent.py (paths fixed)
│       ├── pain_point_extractor.py ← from Component 3's utils/pain_point_extractor.py
│       └── review_reader.py        ← from Component 3's utils/review_reader.py
├── api/
│   ├── schemas.py            ← shared contract (Component 1's schemas + new orchestrator schemas)
│   └── main.py                ← NEW unified FastAPI app — this is where C1 and C3 connect
├── ui/
│   ├── components.py         ← from Component 1's components.py (not currently imported by app_component1.py — it renders its own HTML/CSS inline; kept in case you use it elsewhere)
│   ├── app_component1.py     ← from Component 1's ui/app.py (API routes updated to /component1/analyze and /component1/batch-analyze)
│   └── app_component3.py     ← from Component 3's app.py (imports fixed)
├── dataset/
│   └── sample_products.json  ⚠️ NOT PROVIDED — needed by ui/app_component3.py's product picker
├── requirements.txt          ← merged from both projects
└── README.md                 ← this file
```

## What you need to add before running

1. **`models/roberta_checkpoint/`** — your trained RoBERTa classifier folder from Component 1
2. **`models/demographic_classifier.pkl`, `fusion_meta_model.pkl`, `demographic_feature_cols.pkl`** — from Component 1 (optional — the agent falls back to RoBERTa-only if these aren't found)
3. **`config/.env`** — copy from `.env.example` and fill in your real `XAI_API_KEY`
4. **`dataset/sample_products.json`** (optional) — only needed if you want Component 3's UI product-search feature; without it, the UI falls back to manual product-name entry

Everything else — `generator.py`, both Streamlit UIs, all of Component 3 — is in place and verified working (prompt builders, pain-point extraction, and scarcity copy generation were all tested against this exact file structure).

Component 3's own `.pkl` model files (`scarcity_intensity_regressor.pkl`, `scarcity_scaler.pkl`) don't need to be copied — `ScarcityAgent` trains and saves them automatically into `models/` the first time it runs if they're not already there.

## How the two components are actually connected

`api/main.py` loads both agents once at startup:

```python
agent1 = DualSystemAgent(model_path=".../models/roberta_checkpoint")
agent3 = ScarcityAgent(model_dir=".../models")
```

The new `/generate-strategy` endpoint is the real integration point:

1. Calls `agent1.run(product_text, category, demographics)` → gets `agent_output` (cognitive mode, confidence, strategy, `recommended_copy`)
2. Extracts pain points from `product_text` using Component 3's `extract_pain_points_detailed()`
3. Passes Component 1's `recommended_copy` into Component 3 as `base_copy`, along with `price` (supplied in the request, since Component 1 doesn't track price) and `category`
4. Calls `agent3.generate_all_intensities()` → `agent3.recommend_best_intensity()` → `agent3.calibrate_trust_level()`
5. Returns one combined JSON response with both agents' contributions

Component 1's original endpoints (`/component1/analyze`, `/component1/classify-only`) and new Component 3 endpoints (`/component3/analyze`) are also exposed individually, in case your teammates or other components need to call each agent independently rather than through the combined pipeline.

## Running it

```bash
pip install -r requirements.txt --break-system-packages   # if needed
cp config/.env.example config/.env                        # then edit in your real key
uvicorn api.main:app --reload
```

Then test the orchestrator:

```bash
curl -X POST http://localhost:8000/generate-strategy \
  -H "Content-Type: application/json" \
  -d '{
        "product_name": "Sony WH-1000XM5 Headphones",
        "product_text": "Sony WH-1000XM5 with 30hr battery. Stock sells out fast.",
        "category": "Electronics",
        "price": 899.00
      }'
```

Or visit `http://localhost:8000/docs` for interactive Swagger docs of every endpoint.

## Streamlit UIs

Each component's UI still runs as its own Streamlit app for now
(`streamlit run ui/app_component1.py` / `streamlit run ui/app_component3.py`).
`app_component1.py` talks to the unified API over HTTP (`/component1/analyze`,
`/component1/batch-analyze`), so start `uvicorn api.main:app --reload` first,
then run the Streamlit app in a second terminal.

Merging both into a single UI that calls `/generate-strategy` directly is a
reasonable next step — just ask and I can build that combined UI too.
