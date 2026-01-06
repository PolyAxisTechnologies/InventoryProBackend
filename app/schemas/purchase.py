from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Purchase Item Schemas
class PurchaseItemBase(BaseModel):
    item_id: int
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., ge=0)


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItem(PurchaseItemBase):
    id: int
    purchase_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Purchase Schemas
class PurchaseBase(BaseModel):
    supplier_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    purchase_date: datetime
    notes: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[datetime] = None
    notes: Optional[str] = None


class Purchase(PurchaseBase):
    id: int
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseDetail(Purchase):
    items: List[PurchaseItem] = []
    supplier_name: Optional[str] = None
