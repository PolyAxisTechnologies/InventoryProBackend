from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, Category as CategorySchema
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[CategorySchema])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all categories"""
    try:
        categories = db.query(Category).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    try:
        # Check if category with same name already exists
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        db_category = Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        # Log the operation
        log_operation(
            db=db,
            table_name="categories",
            record_id=db_category.id,
            operation="INSERT",
            new_data=category.model_dump()
        )
        
        logger.info(f"Created category: {db_category.name} (ID: {db_category.id})")
        return db_category
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    try:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Store old data for audit
        old_data = {
            "name": db_category.name,
            "description": db_category.description
        }
        
        # Update fields
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        
        # Log the operation
        log_operation(
            db=db,
            table_name="categories",
            record_id=db_category.id,
            operation="UPDATE",
            old_data=old_data,
            new_data=update_data
        )
        
        logger.info(f"Updated category: {db_category.name} (ID: {db_category.id})")
        return db_category
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    try:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Store data for audit
        old_data = {
            "name": db_category.name,
            "description": db_category.description
        }
        
        db.delete(db_category)
        db.commit()
        
        # Log the operation
        log_operation(
            db=db,
            table_name="categories",
            record_id=category_id,
            operation="DELETE",
            old_data=old_data
        )
        
        logger.info(f"Deleted category: {old_data['name']} (ID: {category_id})")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
