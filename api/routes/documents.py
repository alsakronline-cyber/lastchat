from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import logging

from engine.multimodal.document_processor import DocumentProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

class DocumentAnalysisResponse(BaseModel):
    filename: str
    mime_type: str
    extracted_text: str

# Singleton
_processor = None

def get_processor():
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor

@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or Image) to extract text and technical specs.
    """
    logger.info(f"Receiving file upload: {file.filename}")
    
    try:
        content = await file.read()
        processor = get_processor()
        
        extracted_text, mime_type = processor.process_file(content, filename=file.filename)
        
        return DocumentAnalysisResponse(
            filename=file.filename,
            mime_type=mime_type,
            extracted_text=extracted_text
        )
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
