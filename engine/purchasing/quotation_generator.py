from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch, cm
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class QuotationGenerator:
    def __init__(self, output_dir="media/quotations", assets_dir="assets"):
        self.output_dir = output_dir
        self.assets_dir = assets_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        
        # Custom Styles
        self.styles.add(ParagraphStyle(name='QuoteHeader', parent=self.styles['Heading1'], fontSize=24, spaceAfter=10, textColor=colors.HexColor('#003366')))
        self.styles.add(ParagraphStyle(name='CompanyInfo', parent=self.styles['Normal'], fontSize=9, leading=11, alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='CustomerInfo', parent=self.styles['Normal'], fontSize=10, leading=12))
        self.styles.add(ParagraphStyle(name='Terms', parent=self.styles['Normal'], fontSize=8, leading=10, textColor=colors.gray))

    def generate_quotation(self, start_data: dict):
        """
        Generates a Professional PDF quotation.
        """
        quote_id = f"Q-{int(datetime.now().timestamp())}"
        filename = f"{quote_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []

        # --- 1. HEADER SECTION ---
        # Logo (Left) | Company Info (Right)
        logo_path = os.path.join(self.assets_dir, "logo.png")
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2.5*inch, height=1.0*inch)
            logo.hAlign = 'LEFT'
        else:
            logo = Paragraph("<b>Alsakr Online</b>", self.styles['Heading2'])

        company_details = """
        <b>Alsakr Online Automation</b><br/>
        Cairo, Egypt<br/>
        Phone: +20 123 456 789<br/>
        Email: sales@alsakronline.com<br/>
        Web: www.alsakronline.com
        """
        company_info = Paragraph(company_details, self.styles['CompanyInfo'])

        header_table = Table([[logo, company_info]], colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5 * inch))

        # --- 2. TITLE & CUSTOMER ---
        elements.append(Paragraph("QUOTATION", self.styles['QuoteHeader']))
        elements.append(Spacer(1, 0.2 * inch))

        # Info Table: Date/Ref (Right) | Customer (Left)
        company = start_data.get('company_name', '')
        phone = start_data.get('phone', '')
        
        customer_text = f"""
        <b>BILL TO:</b><br/>
        {start_data.get('customer_name', 'Valued Customer')}<br/>
        """
        if company:
            customer_text += f"{company}<br/>"
        customer_text += f"{start_data.get('customer_email', '')}<br/>"
        if phone:
            customer_text += f"Phone: {phone}<br/>"
        
        meta_text = f"""
        <b>Date:</b> {datetime.now().strftime('%d %b, %Y')}<br/>
        <b>Quote #:</b> {quote_id}<br/>
        <b>Valid Until:</b> {datetime.now().replace(year=datetime.now().year + 1).strftime('%d %b, %Y')}
        """
        
        info_data = [[Paragraph(customer_text, self.styles['CustomerInfo']), Paragraph(meta_text, self.styles['CustomerInfo'])]]
        info_table = Table(info_data, colWidths=[4*inch, 2.5*inch])
        info_table.setStyle(TableStyle([
             ('VALIGN', (0,0), (-1,-1), 'TOP'),
             ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#EEEEEE')),
             ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.4 * inch))

        # --- 3. ITEMS TABLE ---
        # Columns: # | Description | Qty
        data = [['#', 'Description', 'Qty']]
        
        for i, item in enumerate(start_data.get('items', []), 1):
            qty = float(item.get('qty', 1))
            
            # Formatting Description
            desc = f"<b>{item.get('name', 'Product')}</b>"
            description = item.get('description')
            if description:
                desc += f"<br/><font size=9>{description}</font>"
            if item.get('sku'):
                desc += f"<br/><font size=8 color=gray>Part No: {item.get('sku')}</font>"
            
            data.append([
                str(i),
                Paragraph(desc, self.styles['Normal']),
                str(int(qty))
            ])

        # Styling
        # Styling
        t_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('ALIGN', (0, 1), (0, -1), 'CENTER'), # ID Center
            ('ALIGN', (2, 1), (2, -1), 'CENTER'), # Qty Center
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ])
        
        table = Table(data, colWidths=[0.5*inch, 4.5*inch, 0.7*inch])
        table.setStyle(t_style)
        elements.append(table)



        # --- 5. FOOTER & TERMS ---
        elements.append(Spacer(1, 1.0 * inch))
        terms_text = """
        <b>Terms and Conditions:</b><br/>
        1. Validity: This quotation is valid for 30 days from the date of issue.<br/>
        2. Delivery: Subject to prior sale.<br/>
        3. Payment: 100% Advance unless otherwise agreed.<br/>
        Thank you for your business!
        """
        elements.append(Paragraph(terms_text, self.styles['Terms']))

        # Build
        doc.build(elements)
        logger.info(f"Generated professional quotation: {filepath}")
        return filepath
