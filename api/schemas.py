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
    Extends Component 1's ProductInput with fields Components 3 and 2/4 need.
    """
    product_name : str
    product_text : str
    category     : Optional[str] = "unknown"
    price        : Optional[float] = 0.0
    demographics : Optional[DemographicsInput] = None

    # Component 2 / Component 4 need these; all optional with safe defaults
    target_audience : Optional[str] = ""
    features         : Optional[str] = ""
    target_emotion   : Optional[str] = None   # auto-selected from category if omitted

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Sony WH-1000XM5 Noise Cancelling Headphones",
                "product_text": "Sony WH-1000XM5 with 30hr battery. Stock sells out fast.",
                "category": "Electronics",
                "price": 899.00,
                "demographics": None,
                "target_audience": "commuters and remote workers",
                "features": "active noise cancellation, 30h battery, comfortable fit",
                "target_emotion": None
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
    all_copies                : Dict[str, str]  # low/medium/high — full detail for rich UI


class Component24Summary(BaseModel):
    """Combined Component 2 (emotion) + Component 4 (loss framing) output."""
    target_emotion       : str
    base_copy_used        : Optional[str] = None   # Component 1's recommended_copy, fed in as the starting point
    emotion_copy         : str
    emotion_detected     : Optional[str]
    emotion_matched      : bool
    attempts_used        : int
    emotion_after_loss   : Optional[str] = None
    emotion_after_score  : float
    loss_message         : str
    gain_sentiment       : float
    loss_sentiment       : float
    fomo_score           : int
    sentiment_change     : float
    tone_label           : str
    emotion_survived     : bool
    visual_suggestions   : Dict[str, str]


class ScarcityAnalyzeInput(BaseModel):
    product_name: str
    base_copy: str
    price: Optional[float] = 0.0
    category: Optional[str] = "general"
    pain_points: Optional[List[str]] = None


class PainPointExtractInput(BaseModel):
    text: str


class ChannelVariantsInput(BaseModel):
    product_text: str
    category: Optional[str] = "unknown"
    winning_copy: str


class OrchestratorResult(BaseModel):
    """Full response for POST /generate-strategy"""
    product      : str
    component1_full : AnalysisResult
    component1   : Component1Summary
    component3   : Component3Summary
    component24  : Component24Summary
