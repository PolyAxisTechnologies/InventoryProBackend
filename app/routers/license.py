from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from app.license_manager import license_manager

router = APIRouter()

class LicenseVerifyRequest(BaseModel):
    key: str

class LicenseOverrideRequest(BaseModel):
    password: str
    expiry: str # YYYY-MM-DD
    features: List[str]

class LicenseStatusResponse(BaseModel):
    client: str
    expiry: Optional[date]
    features: List[str]
    is_expired: bool
    is_valid: bool
    clock_error: bool
    message: str

@router.get("/status", response_model=LicenseStatusResponse)
async def get_license_status():
    # 1. Check Clock
    clock_ok, clock_msg = license_manager.check_clock_tampering()
    if not clock_ok:
        return {
            "client": "Unknown",
            "expiry": None,
            "features": [],
            "is_expired": True,
            "is_valid": False,
            "clock_error": True,
            "message": clock_msg
        }

    # 2. Check License
    data = license_manager.load_license()
    if not data:
        # Default Trial / No License state
        return {
            "client": "Trial User",
            "expiry": None,
            "features": [],
            "is_expired": True,
            "is_valid": False,
            "clock_error": False,
            "message": "No valid license found."
        }
        
    # 3. Check Expiry
    expiry_date = datetime.strptime(data['expiry'], "%Y-%m-%d").date()
    is_expired = datetime.now().date() > expiry_date
    
    return {
        "client": data.get('client', 'Unknown'),
        "expiry": expiry_date,
        "features": data.get('features', []),
        "is_expired": is_expired,
        "is_valid": True,
        "clock_error": False,
        "message": "License Expired" if is_expired else "Active"
    }

@router.post("/verify")
async def verify_license(req: LicenseVerifyRequest):
    is_valid, result = license_manager.verify_license_key(req.key)
    
    if is_valid:
        license_manager.save_license(req.key)
        # Also clean clock tampering if it was an issue?
        return {"success": True, "message": "License activated successfully", "data": result}
@router.post("/override")
async def override_license(req: LicenseOverrideRequest):
    import os
    admin_pass = os.getenv("VITE_ADMIN_SAVE_PASSWORD", "securepass123")
    if req.password != admin_pass:
        raise HTTPException(status_code=403, detail="Invalid Admin Password")
        
    # Generate signed key internally
    # specific features for the override
    # calls license_manager to create key? 
    # For now, let's just use the valid format but we need the private method.
    
    # Let's import generate_license_key logic or move it to Manager.
    # Actually, simplest is to just construct the key here using manager's secret.
    
    import json
    import base64
    
    payload = {
        "expiry": req.expiry,
        "client": "MANUAL_OVERRIDE",
        "features": req.features,
        "issued_at": datetime.now().isoformat()
    }
    
    json_str = json.dumps(payload, separators=(',', ':'))
    b64_payload = base64.urlsafe_b64encode(json_str.encode()).decode()
    signature = license_manager._get_signature(b64_payload)
    key = f"{b64_payload}.{signature}"
    
    license_manager.save_license(key)
    return {"success": True, "message": "License Manually Updated"}
