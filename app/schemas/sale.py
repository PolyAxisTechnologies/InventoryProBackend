from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Sale Item Schemas
class SaleItemBase(BaseModel):
    item_id: int
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    gst_percentage: float = Field(..., ge=0, le=100)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    line_total: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Sale Schemas
class SaleBase(BaseModel):
    sale_date: datetime
    discount: float = Field(0.0, ge=0)


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    sale_date: Optional[datetime] = None
    discount: Optional[float] = Field(None, ge=0)


class Sale(SaleBase):
    id: int
    subtotal: float
    gst_amount: float
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SaleDetail(Sale):
    items: List[SaleItem] = []
