from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class RecommendRequest(BaseModel):
    skin_type_id: str = Field(..., min_length=1)
    concern_ids: List[str] = Field(..., min_length=1)
    budget: float = Field(..., gt=0)

    @model_validator(mode="after")
    def ensure_unique_concerns(self):
        self.concern_ids = list(dict.fromkeys(self.concern_ids))
        return self


class ProductRecommendation(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    score: float
    reasoning: Optional[str] = None
