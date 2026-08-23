import sys
import os

# ── Must be first — loads .env before any other import ───
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

if not os.getenv("XAI_API_KEY"):
    raise RuntimeError(
        "XAI_API_KEY not found in config/.env\n"
        f"Looking in: {os.path.join(BASE_DIR, 'config', '.env')}\n"
        "Make sure the file exists with: XAI_API_KEY=xai-your-key"
    )

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ProductInput, AnalysisResult, HealthResponse,
    OrchestratorInput, OrchestratorResult,
    Component1Summary, Component3Summary,
)
from src.component1.agent import DualSystemAgent
from src.component3.scarcity_agent import ScarcityAgent
from src.component3.pain_point_extractor import extract_pain_points_detailed


app = FastAPI(
    title="Neuro-Marketing Multi-Agent System",
    description=(
        "Unified backend for the Agentic AI Framework for Neuro-Marketing "
        "Strategy Generation. Component 1 (Dual-System Reasoning) and "
        "Component 3 (Scarcity Optimization) are connected here via the "
        "/generate-strategy orchestrator endpoint."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load both agents once, at server start ──────────────────────
print("Loading Component 1 (DualSystemAgent)...")
agent1 = DualSystemAgent(
    model_path=os.path.join(BASE_DIR, "models", "roberta_checkpoint")
)
print("Loading Component 3 (ScarcityAgent)...")
agent3 = ScarcityAgent(model_dir=os.path.join(BASE_DIR, "models"))
print("Both agents ready. Server starting...")


# ── Health check ──────────────────────────────────────────────
@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "running", "model": "RoBERTa + Scarcity Regressor", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "healthy", "model": "RoBERTa + Scarcity Regressor", "version": "1.0.0"}


# ── Component 1 endpoints (unchanged behaviour, preserved as-is) ──
@app.post("/component1/analyze", response_model=AnalysisResult)
def analyze_product(input_data: ProductInput):
    try:
        result = agent1.run(
            product_text=input_data.product_text,
            category=input_data.category,
            demographics=(input_data.demographics.dict()
                          if input_data.demographics else None),
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component 1 error: {str(e)}")


@app.post("/component1/classify-only")
def classify_only(input_data: ProductInput):
    try:
        return agent1.classify(
            product_text=input_data.product_text,
            category=input_data.category,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@app.post("/component1/batch-analyze")
def batch_analyze(items: list[ProductInput]):
    if len(items) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 products per batch")

    results = []
    for item in items:
        try:
            result = agent1.run(
                product_text=item.product_text,
                category=item.category,
                demographics=(item.demographics.dict() if item.demographics else None),
            )
            results.append({"success": True, "data": result})
        except Exception as e:
            results.append({"success": False, "error": str(e),
                             "product": item.product_text})
        time.sleep(0.5)

    return {"results": results, "total": len(results)}


# ── Component 3 endpoints (new — Component 3 had no API before) ──
@app.post("/component3/analyze")
def analyze_scarcity(product_name: str, base_copy: str,
                      price: float = 0.0, category: str = "general",
                      pain_points: list[str] = None):
    try:
        product_info = {"price": price, "category": category}
        pain_points = pain_points or []

        suitability = agent3.analyze_suitability(product_info)
        all_copies = agent3.generate_all_intensities(
            product_name, base_copy, pain_points=pain_points, product_info=product_info
        )
        recommendation = agent3.recommend_best_intensity(
            product_name, base_copy, all_copies,
            pain_points=pain_points, product_info=product_info
        )
        final_copy = all_copies[recommendation["recommended_intensity"]]
        trust = agent3.calibrate_trust_level(final_copy)

        return {
            "suitability_score": suitability,
            "all_copies": all_copies,
            "recommendation": recommendation,
            "final_copy": final_copy,
            "trust": trust,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component 3 error: {str(e)}")


# ── Orchestrator: THIS is the actual C1 -> C3 connection ─────────
@app.post("/generate-strategy", response_model=OrchestratorResult)
def generate_strategy(input_data: OrchestratorInput):
    """
    Runs Component 1 then Component 3 in sequence, feeding Component 1's
    recommended copy into Component 3 as the base copy for scarcity
    optimization, and returns one combined marketing strategy.
    """
    try:
        # ── Component 1 ──
        c1_result = agent1.run(
            product_text=input_data.product_text,
            category=input_data.category,
            demographics=(input_data.demographics.dict()
                          if input_data.demographics else None),
        )
        if "error" in c1_result:
            raise HTTPException(status_code=503, detail=c1_result["error"])

        agent_output = c1_result["agent_output"]

        # ── Bridge: C1 output + price -> C3 input ──
        pain_analysis = extract_pain_points_detailed(input_data.product_text)
        pain_points = pain_analysis["pain_points"]
        product_info = {"price": input_data.price, "category": input_data.category}
        base_copy = agent_output["recommended_copy"]

        # ── Component 3 ──
        suitability = agent3.analyze_suitability(product_info)
        all_copies = agent3.generate_all_intensities(
            input_data.product_name, base_copy,
            pain_points=pain_points, product_info=product_info,
        )
        recommendation = agent3.recommend_best_intensity(
            input_data.product_name, base_copy, all_copies,
            pain_points=pain_points, product_info=product_info,
        )
        final_copy = all_copies[recommendation["recommended_intensity"]]
        trust = agent3.calibrate_trust_level(final_copy)

        return {
            "product": input_data.product_name,
            "component1": {
                "cognitive_mode": agent_output["cognitive_mode"],
                "confidence": agent_output["confidence"],
                "strategy": agent_output["strategy"],
                "recommended_copy": base_copy,
            },
            "component3": {
                "suitability_score": suitability,
                "pain_points_detected": pain_points,
                "recommended_intensity": recommendation["recommended_intensity"],
                "intensity_score": recommendation["intensity_score"],
                "reason": recommendation["reason"],
                "final_copy": final_copy,
                "trust_status": trust["status"],
                "trust_score": trust["score"],
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")
