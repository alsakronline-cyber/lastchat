from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from api.models import ChatSession, ChatMessage, User
from api.utils.auth import oauth2_scheme, decode_token
from api.database import get_db

router = APIRouter()

# Pydantic Models
class MessageBase(BaseModel):
    role: str
    content: str
    timestamp: datetime

class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime]

class ChatResponse(BaseModel):
    response: str
    session_id: int

# Auth Dependency
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ChatSession).filter(ChatSession.user_id == user.id).order_by(ChatSession.updated_at.desc()).all()

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_session = ChatSession(user_id=user.id, title=session.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{session_id}/messages", response_model=List[MessageBase])
def get_messages(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()

@router.post("/sessions/{session_id}/chat")
def chat_interaction(session_id: int, message: MessageBase, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Save User Message
    user_msg = ChatMessage(session_id=session_id, role="user", content=message.content)
    db.add(user_msg)
    
    # 2. Get AI Response from RAG Engine
    try:
        from api.dependencies import get_rag_chain
        chain = get_rag_chain()
        result = chain.get_recommendation(message.content)
        ai_response_text = result.get("answer", "I'm sorry, I couldn't process that.")
        
        # Optional: Append sources if helpful (for now just text)
        if result.get("source_documents"):
             ai_response_text += "\n\n**Sources:**\n" + "\n".join([f"- {doc.get('name')} ({doc.get('sku')})" for doc in result.get("source_documents")[:3]])

    except Exception as e:
        print(f"RAG Error: {e}")
        ai_response_text = "I encountered an error processing your request. Please try again."

    # 3. Save AI Response
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_response_text)
    db.add(ai_msg)
    
    # Update Session Timestamp
    session.updated_at = datetime.utcnow()
    
    db.commit()
    
    db.commit()
    
    return {
        "response": ai_response_text, 
        "session_id": session_id,
        "sources": result.get("source_documents", [])
    }
