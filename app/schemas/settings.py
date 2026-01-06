from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SettingsBase(BaseModel):
    shop_name: str = Field(..., min_length=1, max_length=200)
    shop_address: Optional[str] = None
    shop_phone: Optional[str] = None
    shop_email: Optional[str] = None
    shop_gstin: Optional[str] = None


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    shop_name: Optional[str] = Field(None, min_length=1, max_length=200)
    shop_address: Optional[str] = None
    shop_phone: Optional[str] = None
    shop_email: Optional[str] = None
    shop_gstin: Optional[str] = None


class Settings(SettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
