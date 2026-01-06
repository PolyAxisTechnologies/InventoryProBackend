from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Item, Category, Quality, Size
from app.schemas.item import ItemCreate, ItemUpdate, ItemStockUpdate, Item as ItemSchema, ItemDetail, ItemBulkCreate
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[ItemSchema])
def get_items(
    category_id: Optional[int] = None,
    quality_id: Optional[int] = None,
    size_id: Optional[int] = None,
    low_stock_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    try:
        query = db.query(Item)
        
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if quality_id:
            query = query.filter(Item.quality_id == quality_id)
        if size_id:
            query = query.filter(Item.size_id == size_id)
        if low_stock_only:
            query = query.filter(Item.stock_quantity <= Item.low_stock_threshold)
        
        items = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(items)} items")
        return items
    except Exception as e:
        logger.error(f"Error retrieving items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category_id}/table")
def get_items_table(category_id: int, db: Session = Depends(get_db)):
    """Get items in table format (qualities x sizes) for a category"""
    try:
        # Get all qualities and sizes for this category
        qualities = db.query(Quality).filter(Quality.category_id == category_id).all()
        sizes = db.query(Size).filter(Size.category_id == category_id).order_by(Size.sort_order).all()
        
        # Get all items for this category
        items = db.query(Item).filter(Item.category_id == category_id).all()
        
        # Create a lookup dictionary
        item_lookup = {}
        for item in items:
            key = f"{item.quality_id}_{item.size_id}"
            item_lookup[key] = {
                "id": item.id,
                "sku": item.sku,
                "stock_quantity": item.stock_quantity,
                "selling_price": item.selling_price,
                "unit": item.unit,
                "gst_percentage": item.gst_percentage,
                "low_stock_threshold": item.low_stock_threshold,
                "is_low_stock": item.stock_quantity <= item.low_stock_threshold
            }
        
        # Build table structure
        table_data = {
            "category_id": category_id,
            "qualities": [{"id": q.id, "name": q.name} for q in qualities],
            "sizes": [{"id": s.id, "size_value": s.size_value, "size_display": s.size_display} for s in sizes],
            "items": item_lookup
        }
        
        return table_data
    except Exception as e:
        logger.error(f"Error getting items table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/low-stock", response_model=List[ItemSchema])
def get_low_stock_items(db: Session = Depends(get_db)):
    """Get all items with stock below threshold"""
    try:
        items = db.query(Item).filter(Item.stock_quantity <= Item.low_stock_threshold).all()
        logger.info(f"Found {len(items)} low stock items")
        return items
    except Exception as e:
        logger.error(f"Error retrieving low stock items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=ItemSchema)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    try:
        db_item = Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        log_operation(
            db=db,
            table_name="items",
            record_id=db_item.id,
            operation="INSERT",
            new_data=item.model_dump()
        )
        
        logger.info(f"Created item: {db_item.sku} (ID: {db_item.id})")
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[ItemSchema], status_code=status.HTTP_201_CREATED)
def create_items_bulk(bulk_data: ItemBulkCreate, db: Session = Depends(get_db)):
    """Create multiple items (all combinations of qualities and sizes)"""
    try:
        items = []
        for quality_id in bulk_data.quality_ids:
            for size_id in bulk_data.size_ids:
                # Check if item already exists
                existing = db.query(Item).filter(
                    Item.category_id == bulk_data.category_id,
                    Item.quality_id == quality_id,
                    Item.size_id == size_id
                ).first()
                
                if existing:
                    continue  # Skip if already exists
                
                # Get quality and size for SKU generation
                quality = db.query(Quality).filter(Quality.id == quality_id).first()
                size = db.query(Size).filter(Size.id == size_id).first()
                
                sku = f"ITM-{quality.name[:3].upper()}-{size.size_value}"
                
                db_item = Item(
                    category_id=bulk_data.category_id,
                    quality_id=quality_id,
                    size_id=size_id,
                    sku=sku,
                    unit=bulk_data.unit,
                    selling_price=bulk_data.default_price,
                    gst_percentage=bulk_data.default_gst,
                    stock_quantity=0,
                    low_stock_threshold=bulk_data.default_threshold
                )
                db.add(db_item)
                items.append(db_item)
        
        db.commit()
        
        for item in items:
            db.refresh(item)
        
        logger.info(f"Created {len(items)} items in bulk for category {bulk_data.category_id}")
        return items
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating items in bulk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=ItemSchema)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        old_data = {
            "sku": db_item.sku,
            "unit": db_item.unit,
            "selling_price": db_item.selling_price,
            "gst_percentage": db_item.gst_percentage,
            "stock_quantity": db_item.stock_quantity,
            "low_stock_threshold": db_item.low_stock_threshold
        }
        
        update_data = item.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        
        log_operation(
            db=db,
            table_name="items",
            record_id=db_item.id,
            operation="UPDATE",
            old_data=old_data,
            new_data=update_data
        )
        
        logger.info(f"Updated item: {db_item.sku} (ID: {db_item.id})")
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{item_id}/stock", response_model=ItemSchema)
def update_item_stock(item_id: int, stock_update: ItemStockUpdate, db: Session = Depends(get_db)):
    """Update item stock quantity (manual adjustment)"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        old_stock = db_item.stock_quantity
        db_item.stock_quantity = stock_update.stock_quantity
        
        db.commit()
        db.refresh(db_item)
        
        log_operation(
            db=db,
            table_name="items",
            record_id=db_item.id,
            operation="UPDATE",
            old_data={"stock_quantity": old_stock},
            new_data={"stock_quantity": stock_update.stock_quantity}
        )
        
        logger.info(f"Updated stock for item {db_item.sku}: {old_stock} -> {stock_update.stock_quantity}")
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item stock: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        old_data = {"sku": db_item.sku, "stock_quantity": db_item.stock_quantity}
        db.delete(db_item)
        db.commit()
        
        log_operation(
            db=db,
            table_name="items",
            record_id=item_id,
            operation="DELETE",
            old_data=old_data
        )
        
        logger.info(f"Deleted item: {old_data['sku']} (ID: {item_id})")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
