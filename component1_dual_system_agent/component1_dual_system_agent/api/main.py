import sys
import os
import time

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import ProductInput, AnalysisResult, HealthResponse
from src.agent import DualSystemAgent

# Create FastAPI app 
app = FastAPI(
    title       = "Dual System Reasoning Agent API",
    description = (
        "Component 1 of the Neuro-Marketing Multi-Agent System. "
        "Classifies products as System 1 (emotional) or System 2 "
        "(rational) and generates psychologically aligned marketing copy."
    ),
    version = "1.0.0"
)

# Allow all origins so teammates can call this API 
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Load agent once when server starts 
print("Loading DualSystemAgent...")
agent = DualSystemAgent(model_path="models/roberta_checkpoint")
print("Agent ready. Server starting...")


@app.get("/", response_model=HealthResponse)
def root():
    """Health check — confirms server is running"""
    return {
        "status":  "running",
        "model":   "RoBERTa + Grok-3",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for teammates to ping"""
    return {
        "status":  "healthy",
        "model":   "RoBERTa + Grok-3",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=AnalysisResult)
def analyze_product(input_data: ProductInput):
    """
    Main endpoint — analyzes a product and returns
    cognitive classification + marketing copy.

    This is the endpoint Components 2, 3, 4 will call.

    Request body:
        product_text : str  — product name/description
        category     : str  — product category (optional)

    Returns:
        Full analysis result with emotional + rational copy
        and recommended strategy
    """
    try:
        result = agent.run(
            product_text = input_data.product_text,
            category     = input_data.category
        )

        if "error" in result:
            raise HTTPException(
                status_code = 503,
                detail      = result["error"]
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail      = f"Agent error: {str(e)}"
        )


@app.post("/classify-only")
def classify_only(input_data: ProductInput):
    """
    Lightweight endpoint — returns only the classification,
    no copy generation. Faster response for cases where
    teammates only need the cognitive mode label.
    """
    try:
        result = agent.classify(
            product_text = input_data.product_text,
            category     = input_data.category
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail      = f"Classification error: {str(e)}"
        )


@app.post("/batch-analyze")
def batch_analyze(items: list[ProductInput]):
    """
    Batch endpoint — analyze multiple products at once.
    Maximum 10 products per request.
    """
    if len(items) > 10:
        raise HTTPException(
            status_code = 400,
            detail      = "Maximum 10 products per batch request"
        )

    results = []
    for item in items:
        try:
            result = agent.run(
                product_text = item.product_text,
                category     = item.category
            )
            results.append({"success": True,  "data": result})
        except Exception as e:
            results.append({"success": False, "error": str(e),
                            "product": item.product_text})
        time.sleep(0.5)

    return {"results": results, "total": len(results)}