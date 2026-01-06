from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Quality
from app.schemas.category import QualityCreate, QualityUpdate, Quality as QualitySchema
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[QualitySchema])
def get_qualities(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all qualities, optionally filtered by category"""
    try:
        query = db.query(Quality)
        if category_id:
            query = query.filter(Quality.category_id == category_id)
        qualities = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(qualities)} qualities")
        return qualities
    except Exception as e:
        logger.error(f"Error retrieving qualities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quality_id}", response_model=QualitySchema)
def get_quality(quality_id: int, db: Session = Depends(get_db)):
    """Get a specific quality by ID"""
    quality = db.query(Quality).filter(Quality.id == quality_id).first()
    if not quality:
        raise HTTPException(status_code=404, detail="Quality not found")
    return quality


@router.post("/", response_model=QualitySchema, status_code=status.HTTP_201_CREATED)
def create_quality(quality: QualityCreate, db: Session = Depends(get_db)):
    """Create a new quality"""
    try:
        db_quality = Quality(**quality.model_dump())
        db.add(db_quality)
        db.commit()
        db.refresh(db_quality)
        
        log_operation(
            db=db,
            table_name="qualities",
            record_id=db_quality.id,
            operation="INSERT",
            new_data=quality.model_dump()
        )
        
        logger.info(f"Created quality: {db_quality.name} (ID: {db_quality.id})")
        return db_quality
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{quality_id}", response_model=QualitySchema)
def update_quality(
    quality_id: int,
    quality: QualityUpdate,
    db: Session = Depends(get_db)
):
    """Update a quality"""
    try:
        db_quality = db.query(Quality).filter(Quality.id == quality_id).first()
        if not db_quality:
            raise HTTPException(status_code=404, detail="Quality not found")
        
        old_data = {"name": db_quality.name, "description": db_quality.description}
        update_data = quality.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_quality, field, value)
        
        db.commit()
        db.refresh(db_quality)
        
        log_operation(
            db=db,
            table_name="qualities",
            record_id=db_quality.id,
            operation="UPDATE",
            old_data=old_data,
            new_data=update_data
        )
        
        logger.info(f"Updated quality: {db_quality.name} (ID: {db_quality.id})")
        return db_quality
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{quality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quality(quality_id: int, db: Session = Depends(get_db)):
    """Delete a quality"""
    try:
        db_quality = db.query(Quality).filter(Quality.id == quality_id).first()
        if not db_quality:
            raise HTTPException(status_code=404, detail="Quality not found")
        
        old_data = {"name": db_quality.name, "description": db_quality.description}
        db.delete(db_quality)
        db.commit()
        
        log_operation(
            db=db,
            table_name="qualities",
            record_id=quality_id,
            operation="DELETE",
            old_data=old_data
        )
        
        logger.info(f"Deleted quality: {old_data['name']} (ID: {quality_id})")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
