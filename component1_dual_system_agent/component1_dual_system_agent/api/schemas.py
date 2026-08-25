from pydantic import BaseModel
from typing   import Optional, Dict, Any  
class DemographicsInput(BaseModel):
    """
    Optional consumer profile from the Google Form survey.
    Field values must match the exact answer strings from the form.
    """

    #  About You
    gender:           Optional[str] = None


    age_range:        Optional[str] = None
  

    district:         Optional[str] = None
    

    occupation:       Optional[str] = None
   

    monthly_spending: Optional[str] = None
    

    culture_influence: Optional[str] = None
   

    avg_emotional_appeal:    Optional[float] = 0.0


    emotional_reason_count:  Optional[int]   = 0
   

    rational_reason_count:   Optional[int]   = 0
   

    rational_check_total:    Optional[int]   = 0
   

    emotional_check_total:   Optional[int]   = 0
   

    class Config:
        json_schema_extra = {
            "example": {
                "gender":                  "Female",
                "age_range":               "18 – 24",
                "district":                "Kandy",
                "occupation":              "Student",
                "monthly_spending":        "Rs. 5,000 – Rs. 15,000",
                "culture_influence":       "Somewhat",
                "avg_emotional_appeal":    1.5,
                "emotional_reason_count":  5,
                "rational_reason_count":   1,
                "rational_check_total":    3,
                "emotional_check_total":   4
            }
        }




class ProductInput(BaseModel):
    """What the API receives from other components or the UI"""
    product_text : str
    category     : Optional[str]               = "unknown"
    demographics : Optional[DemographicsInput] = None  

    class Config:
        json_schema_extra = {
            "example": {
                "product_text": "Sony WH-1000XM5 Noise Cancelling Headphones 30hr battery",
                "category":     "Electronics",
                # demographics is omit it for product-only classification
                "demographics": {
                    "gender":                 "Male",
                    "age_range":              "25 – 34",
                    "district":               "Colombo",
                    "occupation":             "Private sector employee",
                    "monthly_spending":       "Rs. 15,001 – Rs. 30,000",
                    "culture_influence":      "Somewhat",
                    "avg_emotional_appeal":   0.5,
                    "emotional_reason_count": 3,
                    "rational_reason_count":  3,
                    "rational_check_total":   6,
                    "emotional_check_total":  2
                }
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
    cognitive_mode         : str
    label                  : int
    confidence             : float
    s1_probability         : float
    s2_probability         : float
    copy_type              : str
    reasoning              : str
    classification_method  : str = "product text only (RoBERTa)"  # ← NEW field




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