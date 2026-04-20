from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    title: str
    desc:Optional[str]
    price:float


class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True