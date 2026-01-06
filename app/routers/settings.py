from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Settings as SettingsModel
from app.schemas.settings import Settings, SettingsCreate, SettingsUpdate
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=Settings)
def get_settings(db: Session = Depends(get_db)):
    """
    Get shop settings. Creates default settings if none exist.
    """
    settings = db.query(SettingsModel).first()
    
    if not settings:
        # Create default settings
        settings = SettingsModel(
            shop_name="Hardware Point",
            shop_address="Shop Address Line 1\nCity, State - PIN Code",
            shop_phone="+91 XXXXXXXXXX",
            shop_email="info@hardwarepoint.com",
            shop_gstin="22AAAAA0000A1Z5"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        logger.info("Created default settings")
    
    return settings


@router.put("/", response_model=Settings)
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    """
    Update shop settings
    """
    settings = db.query(SettingsModel).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found. Please get settings first to create defaults.")
    
    # Update only provided fields
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    logger.info(f"Updated settings: {update_data.keys()}")
    return settings
