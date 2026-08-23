"""
Shared Pydantic contract for the unified API.

Re-exports Component 1's original schemas unchanged (so its existing
endpoints keep working exactly as before) and adds the extra schemas
needed for the /generate-strategy orchestrator endpoint that connects
Component 1 -> Component 3.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# ── Re-export Component 1's schemas unchanged ──────────────────
from src.component1.schemas import (
    DemographicsInput,
    ProductInput,
    CopyQuality,
    GeneratedCopy,
    Classification,
    Recommendation,
    AgentOutput,
    AnalysisResult,
    HealthResponse,
)


# ── New: orchestrator-level schemas ─────────────────────────────
class ScarcityProductInfo(BaseModel):
    """Extra product metadata Component 3 needs that Component 1 doesn't track."""
    price: Optional[float] = 0.0
    category: Optional[str] = "general"


class OrchestratorInput(BaseModel):
    """
    Input for POST /generate-strategy.
    Extends Component 1's ProductInput with the price field Component 3 needs.
    """
    product_name : str
    product_text : str
    category     : Optional[str] = "unknown"
    price        : Optional[float] = 0.0
    demographics : Optional[DemographicsInput] = None

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Sony WH-1000XM5 Noise Cancelling Headphones",
                "product_text": "Sony WH-1000XM5 with 30hr battery. Stock sells out fast.",
                "category": "Electronics",
                "price": 899.00,
                "demographics": None
            }
        }


class Component1Summary(BaseModel):
    cognitive_mode    : str
    confidence        : float
    strategy          : str
    recommended_copy  : str


class Component3Summary(BaseModel):
    suitability_score      : float
    pain_points_detected   : List[str]
    recommended_intensity  : str
    intensity_score        : float
    reason                 : str
    final_copy              : str
    trust_status            : str
    trust_score              : float


class OrchestratorResult(BaseModel):
    """Full response for POST /generate-strategy"""
    product      : str
    component1   : Component1Summary
    component3   : Component3Summary
