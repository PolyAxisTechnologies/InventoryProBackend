from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class InvoiceItemResponse(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    gst_percentage: float
    amount: float
    gst_amount: float


class ShopInfo(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    gstin: str = None


class InvoiceResponse(BaseModel):
    invoice_number: str
    invoice_date: str
    sale_id: int
    shop: ShopInfo
    items: List[InvoiceItemResponse]
    subtotal: float
    gst_breakdown: Dict[str, float]
    total_gst: float
    discount: float
    grand_total: float

    class Config:
        from_attributes = True
