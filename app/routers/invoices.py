from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
import os

from app.database import get_db
from app.models.models import Sale, SaleItem, Item, Category, Quality, Size, Settings as SettingsModel
from app.schemas.invoice import InvoiceResponse, InvoiceItemResponse, ShopInfo
from app.utils.pdf_generator import generate_invoice_pdf

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/{sale_id}", response_model=InvoiceResponse)
def get_invoice_data(sale_id: int, db: Session = Depends(get_db)):
    """
    Get invoice data for a sale
    """
    # Fetch shop settings
    settings = db.query(SettingsModel).first()
    if not settings:
        # Create default settings if none exist
        settings = SettingsModel(
            shop_name="Hardware Point",
            shop_address="Shop Address Line 1\nCity, State - PIN Code",
            shop_phone="+91 XXXXXXXXXX",
            shop_email="info@hardwarepoint.com",
            shop_gstin="22AAAAA0000A1Z5"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    shop_info = ShopInfo(
        name=settings.shop_name,
        address=settings.shop_address or "",
        phone=settings.shop_phone or "",
        email=settings.shop_email or "",
        gstin=settings.shop_gstin
    )
    
    # Fetch sale with items
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Fetch sale items with related data
    sale_items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    
    if not sale_items:
        raise HTTPException(status_code=404, detail="No items found for this sale")
    
    # Build invoice items
    invoice_items = []
    subtotal = 0
    gst_breakdown: Dict[str, float] = {}
    
    for sale_item in sale_items:
        # Get item details
        item = db.query(Item).filter(Item.id == sale_item.item_id).first()
        if not item:
            continue
        
        # Get category, quality, size
        category = db.query(Category).filter(Category.id == item.category_id).first()
        quality = db.query(Quality).filter(Quality.id == item.quality_id).first()
        size = db.query(Size).filter(Size.id == item.size_id).first()
        
        # Build description
        description = f"{category.name} > {quality.name} > {size.size_display}"
        
        # Calculate amounts
        line_total = sale_item.quantity * sale_item.unit_price
        gst_amount = line_total * (sale_item.gst_percentage / 100)
        
        invoice_items.append(InvoiceItemResponse(
            description=description,
            quantity=sale_item.quantity,
            unit=item.unit,
            unit_price=sale_item.unit_price,
            gst_percentage=sale_item.gst_percentage,
            amount=line_total,
            gst_amount=gst_amount
        ))
        
        subtotal += line_total
        
        # Add to GST breakdown
        gst_key = f"{sale_item.gst_percentage}%"
        if gst_key in gst_breakdown:
            gst_breakdown[gst_key] += gst_amount
        else:
            gst_breakdown[gst_key] = gst_amount
    
    total_gst = sum(gst_breakdown.values())
    grand_total = subtotal + total_gst - sale.discount
    
    # Generate invoice number
    invoice_number = f"INV-{sale.sale_date.strftime('%Y')}-{sale.id:04d}"
    
    return InvoiceResponse(
        invoice_number=invoice_number,
        invoice_date=sale.sale_date.strftime('%d-%b-%Y'),
        sale_id=sale.id,
        shop=shop_info,
        items=invoice_items,
        subtotal=round(subtotal, 2),
        gst_breakdown={k: round(v, 2) for k, v in gst_breakdown.items()},
        total_gst=round(total_gst, 2),
        discount=round(sale.discount, 2),
        grand_total=round(grand_total, 2)
    )


@router.get("/{sale_id}/pdf")
def download_invoice_pdf(sale_id: int, db: Session = Depends(get_db)):
    """
    Generate and download invoice PDF
    """
    # Get invoice data
    invoice_data = get_invoice_data(sale_id, db)
    
    # Generate PDF
    pdf_path = generate_invoice_pdf(invoice_data)
    
    # Return as downloadable file
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"invoice-{sale_id}.pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice-{sale_id}.pdf"}
    )
