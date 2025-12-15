from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Request Model
class QuotationItem(BaseModel):
    sku: str
    quantity: int = 1

class QuotationRequest(BaseModel):
    contact_email: EmailStr
    items: List[QuotationItem]
    notes: str | None = None

# Response Model
class QuotationResponse(BaseModel):
    success: bool
    message: str
    quotation_ref: str

@router.post("/quotations", response_model=QuotationResponse)
async def request_quotation(quote: QuotationRequest):
    """
    Submit a request for quotation (RFQ).
    """
    try:
        logger.info(f"New RFQ from {quote.contact_email} for {len(quote.items)} items.")
        
        # In real app: Validate SKUs, save to DB, trigger email workflow.
        
        mock_ref = f"RFQ-{int(datetime.now().timestamp())}"
        
        return QuotationResponse(
            success=True,
            message=f"Quotation request received. Reference: {mock_ref}",
            quotation_ref=mock_ref
        )
    except Exception as e:
        logger.error(f"Error processing RFQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to process quotation request.")
