from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.models import Sale, SaleItem, Item
from app.schemas.sale import SaleCreate, SaleUpdate, Sale as SaleSchema, SaleDetail
from app.schemas.common import PaginatedResponse
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=PaginatedResponse[SaleSchema])
def get_sales(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all sales with optional date filters and pagination"""
    try:
        query = db.query(Sale)
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            # If explicit time not provided, assume end of day for end_date
            # But the frontend usually sends specific times or dates. 
            # If standard date string, simple comparison might look for strict <=.
             query = query.filter(Sale.sale_date <= end_date)
        
        # Calculate total before pagination
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * limit
        sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
        
        return {
            "items": sales,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error retrieving sales: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sale_id}", response_model=SaleDetail)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale by ID with items"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.post("/", response_model=SaleSchema, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale and deduct stock"""
    try:
        # Calculate totals
        subtotal = 0.0
        gst_amount = 0.0
        
        # Validate items and check stock
        for item_data in sale.items:
            item = db.query(Item).filter(Item.id == item_data.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
            
            # Check stock availability
            if item.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for item {item.sku}. Available: {item.stock_quantity}, Requested: {item_data.quantity}"
                )
            
            # Calculate line total
            line_total = item_data.quantity * item_data.unit_price
            gst = line_total * (item_data.gst_percentage / 100)
            
            subtotal += line_total
            gst_amount += gst
        
        # Apply discount
        total_amount = subtotal + gst_amount - sale.discount
        
        # Create sale
        db_sale = Sale(
            sale_date=sale.sale_date,
            subtotal=subtotal,
            gst_amount=gst_amount,
            discount=sale.discount,
            total_amount=total_amount
        )
        db.add(db_sale)
        db.flush()  # Get the sale ID
        
        # Create sale items and deduct stock
        for item_data in sale.items:
            item = db.query(Item).filter(Item.id == item_data.item_id).first()
            
            line_total = item_data.quantity * item_data.unit_price
            gst = line_total * (item_data.gst_percentage / 100)
            
            sale_item = SaleItem(
                sale_id=db_sale.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                gst_percentage=item_data.gst_percentage,
                line_total=line_total + gst
            )
            db.add(sale_item)
            
            # Deduct stock
            old_stock = item.stock_quantity
            item.stock_quantity -= item_data.quantity
            
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
        db.refresh(db_sale)
        
        # Log sale creation
        log_operation(
            db=db,
            table_name="sales",
            record_id=db_sale.id,
            operation="INSERT",
            new_data={
                "total_amount": total_amount,
                "items_count": len(sale.items)
            }
        )
        
        logger.info(f"Created sale ID: {db_sale.id}, Total: ₹{total_amount:.2f}")
        return db_sale
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sale: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    """Delete a sale and restore stock"""
    try:
        db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not db_sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        
        # Restore stock for all items
        for sale_item in db_sale.sale_items:
            item = db.query(Item).filter(Item.id == sale_item.item_id).first()
            if item:
                old_stock = item.stock_quantity
                item.stock_quantity += sale_item.quantity
                
                log_operation(
                    db=db,
                    table_name="items",
                    record_id=item.id,
                    operation="UPDATE",
                    old_data={"stock_quantity": old_stock},
                    new_data={"stock_quantity": item.stock_quantity}
                )
        
        db.delete(db_sale)
        db.commit()
        
        log_operation(
            db=db,
            table_name="sales",
            record_id=sale_id,
            operation="DELETE",
            old_data={"total_amount": db_sale.total_amount}
        )
        
        logger.info(f"Deleted sale ID: {sale_id} and restored stock")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sale: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
