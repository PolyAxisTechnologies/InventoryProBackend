from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Quality Schemas
class QualityBase(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class QualityCreate(QualityBase):
    pass


class QualityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class Quality(QualityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Size Schemas
class SizeBase(BaseModel):
    category_id: int
    size_value: str = Field(..., min_length=1, max_length=50)
    size_display: str = Field(..., min_length=1, max_length=100)
    sort_order: int = 0


class SizeCreate(SizeBase):
    pass


class SizeUpdate(BaseModel):
    size_value: Optional[str] = Field(None, min_length=1, max_length=50)
    size_display: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_order: Optional[int] = None


class Size(SizeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Bulk Size Creation
class SizeBulkCreate(BaseModel):
    category_id: int
    start_value: float
    end_value: float
    increment: float
    unit: str = "mm"  # mm, inch, etc.
    display_format: str = "{value}{unit}"  # Template for display
