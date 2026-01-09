from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Nested schemas for relationships
class CategoryNested(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class QualityNested(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class SizeNested(BaseModel):
    id: int
    size_value: str
    size_display: str
    
    model_config = ConfigDict(from_attributes=True)


# Item Schemas
class ItemBase(BaseModel):
    category_id: int
    quality_id: int
    size_id: int
    sku: Optional[str] = Field(None, max_length=100)
    unit: str = Field("pcs", max_length=50)
    selling_price: float = Field(0.0, ge=0)
    gst_percentage: float = Field(0.0, ge=0, le=100)
    stock_quantity: float = Field(0.0, ge=0)
    low_stock_threshold: float = Field(10.0, ge=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    selling_price: Optional[float] = Field(None, ge=0)
    gst_percentage: Optional[float] = Field(None, ge=0, le=100)
    stock_quantity: Optional[float] = Field(None, ge=0)
    low_stock_threshold: Optional[float] = Field(None, ge=0)


class ItemStockUpdate(BaseModel):
    stock_quantity: float = Field(..., ge=0)


class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryNested] = None
    quality: Optional[QualityNested] = None
    size: Optional[SizeNested] = None

    model_config = ConfigDict(from_attributes=True)


# Item with related data for display
class ItemDetail(Item):
    category_name: Optional[str] = None
    quality_name: Optional[str] = None
    size_display: Optional[str] = None


# Bulk Item Creation
class ItemBulkCreate(BaseModel):
    category_id: int
    quality_ids: list[int]
    size_ids: list[int]
    unit: str = "pcs"
    default_price: float = 0.0
    default_gst: float = 0.0
    default_threshold: float = 10.0
