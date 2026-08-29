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

if not os.getenv("GROQ_API_KEY"):
    print(
        "WARNING: GROQ_API_KEY not found in config/.env — "
        "Component 2 (Emotion) and Component 4 (Loss Framing) will fail "
        "when called until it's set."
    )

import time
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ProductInput, AnalysisResult, HealthResponse,
    OrchestratorInput, OrchestratorResult,
    Component1Summary, Component3Summary, Component24Summary,
    ScarcityAnalyzeInput, PainPointExtractInput, ChannelVariantsInput,
)
from src.component1.agent import DualSystemAgent
from src.component1.generator import generate_channel_variants
from src.component3.scarcity_agent import ScarcityAgent
from src.component3.pain_point_extractor import extract_pain_points_detailed
from src.component2.model_loader import load_emotion_model
from src.component24_pipeline import run_component24_pipeline


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
print("Loading Component 2 (emotion RoBERTa model)...")
load_emotion_model(os.path.join(BASE_DIR, "models", "roberta_emotion_model"))
print("All agents ready. Server starting...")


# ── Health check ──────────────────────────────────────────────
@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "running", "model": "RoBERTa + Scarcity Regressor", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "healthy", "model": "RoBERTa + Scarcity Regressor", "version": "1.0.0"}


@app.get("/dataset/sample-products")
def get_sample_products():
    """Serves dataset/sample_products.json for the frontend's product picker."""
    try:
        dataset_path = os.path.join(BASE_DIR, "dataset", "sample_products.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="sample_products.json not found in dataset/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample products: {str(e)}")


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


@app.post("/component1/channel-variants")
def channel_variants(input_data: ChannelVariantsInput):
    """
    Reformats an already-chosen winning copy into Social Media, Product
    Listing, and Email variants — same core message, different format for
    each channel a small business actually needs to publish to.
    """
    try:
        return generate_channel_variants(
            product_text=input_data.product_text,
            category=input_data.category,
            winning_copy=input_data.winning_copy,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Channel variant generation error: {str(e)}")


# ── Component 3 endpoints (new — Component 3 had no API before) ──
@app.post("/component3/extract-pain-points")
def extract_pain_points(input_data: PainPointExtractInput):
    try:
        return extract_pain_points_detailed(input_data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pain point extraction error: {str(e)}")


@app.post("/component3/analyze")
def analyze_scarcity(input_data: ScarcityAnalyzeInput):
    try:
        product_info = {"price": input_data.price, "category": input_data.category}
        pain_points = input_data.pain_points or []

        suitability = agent3.analyze_suitability(product_info)
        all_copies = agent3.generate_all_intensities(
            input_data.product_name, input_data.base_copy,
            pain_points=pain_points, product_info=product_info
        )
        recommendation = agent3.recommend_best_intensity(
            input_data.product_name, input_data.base_copy, all_copies,
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


# ── Component 2+4 endpoint (matches original /api/pipeline contract) ──
@app.post("/component24/pipeline")
def component24_pipeline(payload: dict):
    try:
        result = run_component24_pipeline(
            product_name=payload.get("product_name", ""),
            category=payload.get("category", ""),
            target_audience=payload.get("target_audience", ""),
            features=payload.get("features", ""),
            target_emotion=payload.get("target_emotion") or None,
            base_copy=payload.get("base_copy") or None,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component 2/4 error: {str(e)}")


# ── Orchestrator: THIS is the actual C1 -> C2/C3/C4 connection ─────────
@app.post("/generate-strategy", response_model=OrchestratorResult)
def generate_strategy(input_data: OrchestratorInput):
    """
    Runs Component 1, then Component 3 and Component 2/4 (each using
    Component 1's classification context where relevant), and returns
    one combined marketing strategy synthesizing all four agents.
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

        # ── Component 2 -> Component 4 (now fed by Component 1's recommended_copy) ──
        c24_result = run_component24_pipeline(
            product_name=input_data.product_name,
            category=input_data.category,
            target_audience=input_data.target_audience,
            features=input_data.features,
            target_emotion=input_data.target_emotion,
            base_copy=base_copy,   # Component 1's recommended_copy feeds into Component 2
        )

        return {
            "product": input_data.product_name,
            "component1_full": c1_result,
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
                "all_copies": all_copies,
            },
            "component24": {
                "target_emotion": c24_result["target_emotion"],
                "base_copy_used": c24_result["base_copy_used"],
                "emotion_copy": c24_result["emotion_copy"],
                "emotion_detected": c24_result["emotion_detected"],
                "emotion_matched": c24_result["emotion_matched"],
                "attempts_used": c24_result["attempts_used"],
                "emotion_after_loss": c24_result["emotion_after_loss"],
                "emotion_after_score": c24_result["emotion_after_score"],
                "loss_message": c24_result["loss_message"],
                "gain_sentiment": c24_result["gain_sentiment"],
                "loss_sentiment": c24_result["loss_sentiment"],
                "fomo_score": c24_result["fomo_score"],
                "sentiment_change": c24_result["sentiment_change"],
                "tone_label": c24_result["tone_label"],
                "emotion_survived": c24_result["emotion_survived"],
                "visual_suggestions": c24_result["visual_suggestions"],
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")
