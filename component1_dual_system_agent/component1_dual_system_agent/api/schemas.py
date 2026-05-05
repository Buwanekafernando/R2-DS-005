

from pydantic import BaseModel
from typing import Optional

class ProductInput(BaseModel):
    """What the API receives from other components or the UI"""
    product_text : str
    category     : Optional[str] = "unknown"

    class Config:
        json_schema_extra = {
            "example": {
                "product_text": "Sony WH-1000XM5 Noise Cancelling Headphones 30hr battery",
                "category":     "Electronics"
            }
        }


class CopyQuality(BaseModel):
    sentiment_compound : float
    sentiment_positive : float
    word_count         : int
    mode_alignment     : float


class GeneratedCopy(BaseModel):
    text    : str
    quality : CopyQuality


class Classification(BaseModel):
    cognitive_mode  : str
    label           : int
    confidence      : float
    s1_probability  : float
    s2_probability  : float
    copy_type       : str
    reasoning       : str


class Recommendation(BaseModel):
    strategy      : str
    selected_copy : str
    explanation   : str


class AgentOutput(BaseModel):
    """Simplified output — what Components 2, 3, 4 receive"""
    cognitive_mode   : str
    confidence       : float
    strategy         : str
    emotional_copy   : str
    rational_copy    : str
    recommended_copy : str


class AnalysisResult(BaseModel):
    """Full API response"""
    input          : dict
    classification : Classification
    generated_copy : dict
    recommendation : Recommendation
    agent_output   : AgentOutput


class HealthResponse(BaseModel):
    status  : str
    model   : str
    version : str