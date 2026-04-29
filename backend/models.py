from pydantic import BaseModel, conlist
from typing import List, Optional

class RecommendRequest(BaseModel):
    skin_type_id: str
    concern_ids: List[str]
    budget: float

class ProductRecommendation(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    score: float
    reasoning: Optional[str] = None
