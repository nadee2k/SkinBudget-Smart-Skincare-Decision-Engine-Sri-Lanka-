from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RecommendRequest(BaseModel):
    skin_type_id: str = Field(..., min_length=1)
    concern_ids: List[str] = Field(..., min_length=1)
    budget: float = Field(..., gt=0)

    @field_validator('skin_type_id')
    @classmethod
    def normalize_skin_type(cls, v):
        # Strip whitespace
        v = v.strip()
        if not v:
            raise ValueError('skin_type_id cannot be blank')
        return v

    @field_validator('concern_ids')
    @classmethod
    def normalize_concerns(cls, v):
        # Trim each concern and remove duplicates while preserving order
        trimmed = [concern.strip() for concern in v]
        return list(dict.fromkeys(trimmed))


class ProductRecommendation(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    score: float
    reasoning: Optional[str] = None
