from sqlalchemy.orm import Session
from app.models.models import AuditLog
from app.utils.logger_config import get_logger
from datetime import datetime
import json

logger = get_logger()


def log_operation(
    db: Session,
    table_name: str,
    record_id: int,
    operation: str,  # INSERT, UPDATE, DELETE
    old_data: dict = None,
    new_data: dict = None,
    user_id: int = None,
    ip_address: str = None
):
    """
    Log database operations to audit_logs table
    
    Args:
        db: Database session
        table_name: Name of the table being modified
        record_id: ID of the record being modified
        operation: Type of operation (INSERT, UPDATE, DELETE)
        old_data: Previous state of the record (for UPDATE/DELETE)
        new_data: New state of the record (for INSERT/UPDATE)
        user_id: ID of the user performing the operation (optional)
        ip_address: IP address of the request (optional)
    """
    try:
        # Convert datetime objects to strings for JSON serialization
        if old_data:
            old_data = _serialize_data(old_data)
        if new_data:
            new_data = _serialize_data(new_data)
        
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            old_data=old_data,
            new_data=new_data,
            user_id=user_id,
            ip_address=ip_address
        )
        
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Audit log created: {operation} on {table_name} (ID: {record_id})")
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        db.rollback()


def _serialize_data(data: dict) -> dict:
    """Convert datetime and other non-serializable objects to strings"""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif hasattr(value, '__dict__'):
            # Skip SQLAlchemy relationship objects
            continue
        else:
            serialized[key] = value
    return serialized


def get_audit_logs(
    db: Session,
    table_name: str = None,
    operation: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Retrieve audit logs with optional filters
    
    Args:
        db: Database session
        table_name: Filter by table name
        operation: Filter by operation type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of audit log records
    """
    query = db.query(AuditLog)
    
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    
    if operation:
        query = query.filter(AuditLog.operation == operation)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    query = query.order_by(AuditLog.timestamp.desc())
    query = query.limit(limit).offset(offset)
    
    return query.all()
