from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Size
from app.schemas.category import SizeCreate, SizeUpdate, Size as SizeSchema, SizeBulkCreate
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[SizeSchema])
def get_sizes(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all sizes, optionally filtered by category"""
    try:
        query = db.query(Size)
        if category_id:
            query = query.filter(Size.category_id == category_id)
        sizes = query.order_by(Size.sort_order).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(sizes)} sizes")
        return sizes
    except Exception as e:
        logger.error(f"Error retrieving sizes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{size_id}", response_model=SizeSchema)
def get_size(size_id: int, db: Session = Depends(get_db)):
    """Get a specific size by ID"""
    size = db.query(Size).filter(Size.id == size_id).first()
    if not size:
        raise HTTPException(status_code=404, detail="Size not found")
    return size


@router.post("/", response_model=SizeSchema, status_code=status.HTTP_201_CREATED)
def create_size(size: SizeCreate, db: Session = Depends(get_db)):
    """Create a new size"""
    try:
        db_size = Size(**size.model_dump())
        db.add(db_size)
        db.commit()
        db.refresh(db_size)
        
        log_operation(
            db=db,
            table_name="sizes",
            record_id=db_size.id,
            operation="INSERT",
            new_data=size.model_dump()
        )
        
        logger.info(f"Created size: {db_size.size_display} (ID: {db_size.id})")
        return db_size
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[SizeSchema], status_code=status.HTTP_201_CREATED)
def create_sizes_bulk(bulk_data: SizeBulkCreate, db: Session = Depends(get_db)):
    """Create multiple sizes from a range"""
    try:
        sizes = []
        current = bulk_data.start_value
        sort_order = 0
        
        while current <= bulk_data.end_value:
            size_value = str(current)
            size_display = bulk_data.display_format.format(value=current, unit=bulk_data.unit)
            
            db_size = Size(
                category_id=bulk_data.category_id,
                size_value=size_value,
                size_display=size_display,
                sort_order=sort_order
            )
            db.add(db_size)
            sizes.append(db_size)
            
            current += bulk_data.increment
            sort_order += 1
        
        db.commit()
        
        for size in sizes:
            db.refresh(size)
        
        logger.info(f"Created {len(sizes)} sizes in bulk for category {bulk_data.category_id}")
        return sizes
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sizes in bulk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{size_id}", response_model=SizeSchema)
def update_size(
    size_id: int,
    size: SizeUpdate,
    db: Session = Depends(get_db)
):
    """Update a size"""
    try:
        db_size = db.query(Size).filter(Size.id == size_id).first()
        if not db_size:
            raise HTTPException(status_code=404, detail="Size not found")
        
        old_data = {
            "size_value": db_size.size_value,
            "size_display": db_size.size_display,
            "sort_order": db_size.sort_order
        }
        update_data = size.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_size, field, value)
        
        db.commit()
        db.refresh(db_size)
        
        log_operation(
            db=db,
            table_name="sizes",
            record_id=db_size.id,
            operation="UPDATE",
            old_data=old_data,
            new_data=update_data
        )
        
        logger.info(f"Updated size: {db_size.size_display} (ID: {db_size.id})")
        return db_size
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{size_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_size(size_id: int, db: Session = Depends(get_db)):
    """Delete a size"""
    try:
        db_size = db.query(Size).filter(Size.id == size_id).first()
        if not db_size:
            raise HTTPException(status_code=404, detail="Size not found")
        
        old_data = {
            "size_value": db_size.size_value,
            "size_display": db_size.size_display
        }
        db.delete(db_size)
        db.commit()
        
        log_operation(
            db=db,
            table_name="sizes",
            record_id=size_id,
            operation="DELETE",
            old_data=old_data
        )
        
        logger.info(f"Deleted size: {old_data['size_display']} (ID: {size_id})")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
