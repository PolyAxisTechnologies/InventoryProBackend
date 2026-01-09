from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime

from app.database import get_db
from app.utils.audit_logger import get_audit_logs as fetch_audit_logs
from app.models.models import AuditLog
from pydantic import BaseModel, ConfigDict

router = APIRouter(
    tags=["Audit Logs"]
)

# Schema for Audit Log Response
class AuditLogSchema(BaseModel):
    id: int
    table_name: str
    record_id: int
    operation: str
    old_data: Optional[Union[dict, str]] = None
    new_data: Optional[Union[dict, str]] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[AuditLogSchema])
def get_audit_logs(
    table_name: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering
    """
    logs = fetch_audit_logs(
        db=db,
        table_name=table_name,
        operation=operation,
        limit=limit,
        offset=offset
    )
    return logs
