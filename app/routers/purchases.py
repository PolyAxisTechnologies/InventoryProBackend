from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.models import Purchase, PurchaseItem, Item
from app.schemas.purchase import PurchaseCreate, PurchaseUpdate, Purchase as PurchaseSchema, PurchaseDetail
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[PurchaseSchema])
def get_purchases(
    supplier_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all purchases with optional filters"""
    try:
        query = db.query(Purchase)
        
        if supplier_id:
            query = query.filter(Purchase.supplier_id == supplier_id)
        if start_date:
            query = query.filter(Purchase.purchase_date >= start_date)
        if end_date:
            query = query.filter(Purchase.purchase_date <= end_date)
        
        purchases = query.order_by(Purchase.purchase_date.desc()).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(purchases)} purchases")
        return purchases
    except Exception as e:
        logger.error(f"Error retrieving purchases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{purchase_id}", response_model=PurchaseDetail)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """Get a specific purchase by ID with items"""
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


@router.post("/", response_model=PurchaseSchema, status_code=status.HTTP_201_CREATED)
def create_purchase(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    """Create a new purchase and add stock"""
    try:
        # Calculate total
        total_amount = sum(item.quantity * item.purchase_price for item in purchase.items)
        
        # Validate items exist
        for item_data in purchase.items:
            item = db.query(Item).filter(Item.id == item_data.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        
        # Create purchase
        db_purchase = Purchase(
            supplier_id=purchase.supplier_id,
            invoice_number=purchase.invoice_number,
            purchase_date=purchase.purchase_date,
            total_amount=total_amount,
            notes=purchase.notes
        )
        db.add(db_purchase)
        db.flush()  # Get the purchase ID
        
        # Create purchase items and add stock
        for item_data in purchase.items:
            item = db.query(Item).filter(Item.id == item_data.item_id).first()
            
            purchase_item = PurchaseItem(
                purchase_id=db_purchase.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                purchase_price=item_data.purchase_price
            )
            db.add(purchase_item)
            
            # Add stock
            old_stock = item.stock_quantity
            item.stock_quantity += item_data.quantity
            
            # Log stock change
            log_operation(
                db=db,
                table_name="items",
                record_id=item.id,
                operation="UPDATE",
                old_data={"stock_quantity": old_stock},
                new_data={"stock_quantity": item.stock_quantity}
            )
        
        db.commit()
        db.refresh(db_purchase)
        
        # Log purchase creation
        log_operation(
            db=db,
            table_name="purchases",
            record_id=db_purchase.id,
            operation="INSERT",
            new_data={
                "total_amount": total_amount,
                "items_count": len(purchase.items)
            }
        )
        
        logger.info(f"Created purchase ID: {db_purchase.id}, Total: ₹{total_amount:.2f}")
        return db_purchase
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """Delete a purchase and deduct stock"""
    try:
        db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not db_purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")
        
        # Deduct stock for all items
        for purchase_item in db_purchase.purchase_items:
            item = db.query(Item).filter(Item.id == purchase_item.item_id).first()
            if item:
                old_stock = item.stock_quantity
                item.stock_quantity -= purchase_item.quantity
                
                # Prevent negative stock
                if item.stock_quantity < 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot delete purchase: would result in negative stock for item {item.sku}"
                    )
                
                log_operation(
                    db=db,
                    table_name="items",
                    record_id=item.id,
                    operation="UPDATE",
                    old_data={"stock_quantity": old_stock},
                    new_data={"stock_quantity": item.stock_quantity}
                )
        
        db.delete(db_purchase)
        db.commit()
        
        log_operation(
            db=db,
            table_name="purchases",
            record_id=purchase_id,
            operation="DELETE",
            old_data={"total_amount": db_purchase.total_amount}
        )
        
        logger.info(f"Deleted purchase ID: {purchase_id} and deducted stock")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
