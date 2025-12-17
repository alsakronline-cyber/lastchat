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
class QuotationItem(BaseModel):
    sku: str
    name: Optional[str] = "Product"
    qty: int = 1

class QuotationRequest(BaseModel):
    customer_name: str     # Added customer name
    customer_email: EmailStr
    items: List[QuotationItem]

@router.post("/quotations", summary="Generate a PDF Quotation")
async def generate_quotation(request: QuotationRequest):
    try:
        data = request.dict()
        # Normalization for generator
        for item in data['items']:
             # Ensure correct keys for generator if needed
             pass

        filepath = generator.generate_quotation(data)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
            
        return FileResponse(filepath, media_type="application/pdf", filename=os.path.basename(filepath))
    except Exception as e:
        logger.error(f"Error generating quotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
