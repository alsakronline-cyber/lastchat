from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# The declarative base that Alembic will use
Base = declarative_base()

# ----------------------------------------------------------------------
# User & Auth Models
# ----------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")

# ----------------------------------------------------------------------
# Chat History Models
# ----------------------------------------------------------------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False) # user, assistant, system
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

# ----------------------------------------------------------------------
# Product & Business Models
# ----------------------------------------------------------------------
class Product(Base):
    __tablename__ = "products"
    sku_id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    category = Column(String, index=True)
    family_group = Column(String) # E.g., "G6"
    manufacturer = Column(String, default="SICK")
    description = Column(String)
    
    # Rich Data Fields
    specifications = Column(JSON) # Detailed Key-Value pairs
    images = Column(JSON) # List of image URLs
    technical_drawings = Column(JSON) # List of drawing URLs
    documents = Column(JSON) # List of {title, url} for PDF datasheets etc
    custom_data = Column(JSON) # Any extra scraped data
    
    datasheet_url = Column(String) # Keep for backward compatibility or main datasheet
    
    # Search & RAG fields
    embedding_text = Column(String) # Content used for embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Quotation(Base):
    __tablename__ = "quotations"
    quotation_id = Column(Integer, primary_key=True, autoincrement=True)
    # If users are logged in, link it, otherwise allow guest quotes
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    customer_name = Column(String)
    customer_email = Column(String)
    
    items = Column(JSON) # List of {sku, name, qty, brand}
    status = Column(String, default="DRAFT") # DRAFT, GENERATED
    created_at = Column(DateTime, default=datetime.utcnow)

class InteractionLog(Base):
    __tablename__ = "interaction_logs"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    query = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

