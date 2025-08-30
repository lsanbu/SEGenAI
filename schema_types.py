from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class IdeaSchema(BaseModel):
    idea_title: Optional[str] = Field(None, description="Short title or name for the idea")
    one_liner: Optional[str] = Field(None, description="One sentence description")
    problem: Optional[str] = Field(None, description="Problem being solved")
    target_customer: Optional[str] = Field(None, description="Who is it for")
    solution: Optional[str] = Field(None, description="How it solves the problem")
    business_model: Optional[str] = Field(None, description="How money is made (subscription, ads, etc.)")

    # Optional good-to-haves
    pricing: Optional[str] = None
    gtm: Optional[str] = None
    competition: Optional[str] = None
    moat: Optional[str] = None
    key_risks: Optional[str] = None

    def missing_required_fields(self) -> List[str]:
        order = ["problem", "target_customer", "solution", "business_model"]
        return [f for f in order if (getattr(self, f) is None or str(getattr(self, f)).strip() == "")]
