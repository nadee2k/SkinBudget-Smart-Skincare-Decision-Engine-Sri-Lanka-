from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class RecommendRequest(BaseModel):
    skin_type_id: str = Field(..., min_length=1)
    concern_ids: List[str] = Field(..., min_length=1)
    budget: float = Field(..., gt=0)

    @field_validator('skin_type_id')
    @classmethod
    def normalize_skin_type(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('skin_type_id cannot be blank')
        return v

    @field_validator('concern_ids')
    @classmethod
    def normalize_concerns(cls, v):
        trimmed = [concern.strip() for concern in v]
        return list(dict.fromkeys(trimmed))

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


class ProfileUpsertRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    skin_type_id: str = Field(..., min_length=1)
    concern_ids: List[str] = Field(..., min_length=1)
    confidence_score: float = Field(default=0.8, ge=0, le=1)

    @model_validator(mode="after")
    def ensure_unique_concerns(self):
        self.concern_ids = list(dict.fromkeys(self.concern_ids))
        return self


class ProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    skin_type_id: str
    concern_ids: List[str]
    confidence_score: float
    recorded_at: datetime


class UserRecommendRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    budget: float = Field(..., gt=0)