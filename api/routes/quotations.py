from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.responses import FileResponse
from engine.purchasing.quotation_generator import QuotationGenerator
from typing import List, Optional
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)
generator = QuotationGenerator()

# Request Model
class BillTo(BaseModel):
    name: str
    company_name: Optional[str] = None
    address: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None

class QuotationItem(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 1
    sku: Optional[str] = None

class QuotationRequest(BaseModel):
    quotation_id: Optional[str] = None
    bill_to: BillTo
    items: List[QuotationItem]

@router.post("/quotations", summary="Generate a PDF Quotation")
async def generate_quotation(request: QuotationRequest):
    try:
        # Transform to generator format
        generator_data = {
            'customer_name': request.bill_to.name,
            'customer_email': request.bill_to.email,
            'company_name': request.bill_to.company_name,
            'phone': request.bill_to.phone,
            'address': request.bill_to.address,
            'items': [
                {
                    'name': item.name,
                    'sku': item.sku or '',
                    'qty': item.quantity,
                    'description': item.description
                }
                for item in request.items
            ]
        }

        filepath = generator.generate_quotation(generator_data)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
            
        return FileResponse(filepath, media_type="application/pdf", filename=os.path.basename(filepath))
    except Exception as e:
        logger.error(f"Error generating quotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
