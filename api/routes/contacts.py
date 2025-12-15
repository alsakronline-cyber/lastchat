from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Request Model
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    message: str | None = None

# Response Model
class ContactResponse(BaseModel):
    success: bool
    message: str
    contact_id: str

@router.post("/contacts", response_model=ContactResponse)
async def create_contact(contact: ContactRequest):
    """
    Capture a new contact/lead.
    """
    try:
        # In a real app, save to DB here. 
        # For now, just log it.
        logger.info(f"New Contact Captured: {contact.name} ({contact.email})")
        
        # Mocking a saved ID
        mock_id = f"cont_{int(datetime.now().timestamp())}"
        
        return ContactResponse(
            success=True,
            message="Contact information saved successfully.",
            contact_id=mock_id
        )
    except Exception as e:
        logger.error(f"Error saving contact: {e}")
        raise HTTPException(status_code=500, detail="Failed to save contact.")
