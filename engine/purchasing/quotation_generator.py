from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class QuotationGenerator:
    def __init__(self, output_dir="media/quotations"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()

    def generate_quotation(self, start_data: dict):
        """
        Generates a PDF quotation.
        
        Args:
            start_data (dict): Data for the quotation.
                {
                    "customer_name": "John Doe",
                    "customer_email": "john@example.com",
                    "items": [
                        {"sku": "123", "name": "Sensor", "qty": 2, "price": 100.0}
                    ]
                }
        Returns:
            str: Path to the generated PDF.
        """
        quote_id = f"Q-{int(datetime.now().timestamp())}"
        filename = f"{quote_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []

        # 1. Header
        header_text = f"QUOTATION: {quote_id}"
        elements.append(Paragraph(header_text, self.styles['Heading1']))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))

        # 2. Customer Info
        elements.append(Paragraph(f"<b>Customer:</b> {start_data.get('customer_name', 'Guest')}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Email:</b> {start_data.get('customer_email', 'N/A')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5 * inch))

        # 3. Items Table
        data = [['SKU', 'Product Name', 'Qty', 'Unit Price', 'Total']]
        total_amount = 0.0

        for item in start_data.get('items', []):
            qty = item.get('qty', 1)
            price = item.get('price', 0.0)
            line_total = qty * price
            total_amount += line_total
            
            data.append([
                item.get('sku', 'N/A'),
                Paragraph(item.get('name', 'Product'), self.styles['Normal']), # Wrap text
                str(qty),
                f"${price:,.2f}",
                f"${line_total:,.2f}"
            ])

        # Total Row
        data.append(['', '', '', '<b>TOTAL</b>', f"<b>${total_amount:,.2f}</b>"])

        # Table Styling
        table = Table(data, colWidths=[1.0*inch, 3.0*inch, 0.5*inch, 1.0*inch, 1.0*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Qty Center
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Price Right
            # Footer (Total)
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        
        # 4. Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_text = "Thank you for your business!"
        elements.append(Paragraph(footer_text, self.styles['Normal']))

        # Build
        doc.build(elements)
        logger.info(f"Generated quotation: {filepath}")
        return filepath
