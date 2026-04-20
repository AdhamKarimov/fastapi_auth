from pydantic import BaseModel
from typing import Optional


class OrderBase(BaseModel):
    product_id: int
    quantity: int
