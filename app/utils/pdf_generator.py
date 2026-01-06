from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os
import tempfile

from app.schemas.invoice import InvoiceResponse


def generate_invoice_pdf(invoice_data: InvoiceResponse) -> str:
    """
    Generate a PDF invoice from invoice data
    Returns the path to the generated PDF file
    """
    # Create temp file
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"invoice_{invoice_data.sale_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Shop Header
    story.append(Paragraph(invoice_data.shop.name, title_style))
    story.append(Paragraph(invoice_data.shop.address.replace('\n', '<br/>'), header_style))
    story.append(Paragraph(f"Phone: {invoice_data.shop.phone} | Email: {invoice_data.shop.email}", header_style))
    if invoice_data.shop.gstin:
        story.append(Paragraph(f"GSTIN: {invoice_data.shop.gstin}", header_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Title
    story.append(Paragraph("TAX INVOICE", invoice_title_style))
    
    # Invoice Details Table
    invoice_details_data = [
        ['Invoice No:', invoice_data.invoice_number, 'Date:', invoice_data.invoice_date]
    ]
    
    invoice_details_table = Table(invoice_details_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    invoice_details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ]))
    
    story.append(invoice_details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table Header
    items_data = [['Description', 'Qty', 'Unit', 'Price', 'GST%', 'Amount', 'GST Amt']]
    
    # Items Table Data
    normal_style = ParagraphStyle(
        'ItemDescription',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )
    
    for item in invoice_data.items:
        # Use Paragraph for description to enable text wrapping
        desc_paragraph = Paragraph(item.description, normal_style)
        
        items_data.append([
            desc_paragraph,  # Use Paragraph instead of plain string
            f"{item.quantity:.2f}",
            item.unit,
            f"Rs.{item.unit_price:.2f}",
            f"{item.gst_percentage}%",
            f"Rs.{item.amount:.2f}",
            f"Rs.{item.gst_amount:.2f}"
        ])
    
    # Create items table - description will auto-wrap to multiple lines
    items_table = Table(items_data, colWidths=[3*inch, 0.5*inch, 0.5*inch, 0.7*inch, 0.5*inch, 0.85*inch, 0.85*inch])
    
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ('WORDWRAP', (0, 1), (0, -1), True),  # Enable word wrap for description column
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals Table
    totals_data = [
        ['', 'Subtotal:', f"Rs.{invoice_data.subtotal:.2f}"]
    ]
    
    # Add GST breakdown
    for gst_rate, gst_amount in invoice_data.gst_breakdown.items():
        totals_data.append(['', f'GST {gst_rate}:', f"Rs.{gst_amount:.2f}"])
    
    if invoice_data.discount > 0:
        totals_data.append(['', 'Discount:', f"- Rs.{invoice_data.discount:.2f}"])
    
    totals_data.append(['', 'GRAND TOTAL:', f"Rs.{invoice_data.grand_total:.2f}"])
    
    totals_table = Table(totals_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
    
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (1, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (-1, -2), 10),
        ('FONTSIZE', (1, -1), (-1, -1), 12),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (1, -1), (-1, -1), colors.HexColor('#1e40af')),
        ('LINEABOVE', (1, -1), (-1, -1), 2, colors.HexColor('#2563eb')),
        ('TOPPADDING', (1, -1), (-1, -1), 12),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Thank you for your business!", footer_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%b-%Y %I:%M %p')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path
