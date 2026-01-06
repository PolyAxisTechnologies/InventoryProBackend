from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Supplier
from app.schemas.purchase import SupplierCreate, SupplierUpdate, Supplier as SupplierSchema
from app.utils.audit_logger import log_operation
from app.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[SupplierSchema])
def get_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all suppliers"""
    try:
        suppliers = db.query(Supplier).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(suppliers)} suppliers")
        return suppliers
    except Exception as e:
        logger.error(f"Error retrieving suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{supplier_id}", response_model=SupplierSchema)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Get a specific supplier by ID"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierSchema, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    """Create a new supplier"""
    try:
        db_supplier = Supplier(**supplier.model_dump())
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        
        log_operation(
            db=db,
            table_name="suppliers",
            record_id=db_supplier.id,
            operation="INSERT",
            new_data=supplier.model_dump()
        )
        
        logger.info(f"Created supplier: {db_supplier.name} (ID: {db_supplier.id})")
        return db_supplier
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{supplier_id}", response_model=SupplierSchema)
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    """Update a supplier"""
    try:
        db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not db_supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        old_data = {
            "name": db_supplier.name,
            "contact_person": db_supplier.contact_person,
            "phone": db_supplier.phone,
            "email": db_supplier.email,
            "address": db_supplier.address
        }
        
        update_data = supplier.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_supplier, field, value)
        
        db.commit()
        db.refresh(db_supplier)
        
        log_operation(
            db=db,
            table_name="suppliers",
            record_id=db_supplier.id,
            operation="UPDATE",
            old_data=old_data,
            new_data=update_data
        )
        
        logger.info(f"Updated supplier: {db_supplier.name} (ID: {db_supplier.id})")
        return db_supplier
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Delete a supplier"""
    try:
        db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not db_supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        old_data = {"name": db_supplier.name}
        db.delete(db_supplier)
        db.commit()
        
        log_operation(
            db=db,
            table_name="suppliers",
            record_id=supplier_id,
            operation="DELETE",
            old_data=old_data
        )
        
        logger.info(f"Deleted supplier: {old_data['name']} (ID: {supplier_id})")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
