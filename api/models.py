from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
# The declarative base that Alembic will use
Base = declarative_base()
# ----------------------------------------------------------------------
# Example model definitions – adapt the columns to match your schema
# ----------------------------------------------------------------------
class Product(Base):
    __tablename__ = "products"
    sku_id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    manufacturer = Column(String)
    specifications = Column(JSON)
    relationships = Column(JSON)
    embedding_text = Column(String)
    datasheet_url = Column(String)
    images = Column(JSON)
    pricing = Column(JSON)
    confidence_score = Column(Float)
    language = Column(String)
    source = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
class Contact(Base):
    __tablename__ = "contacts"
    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String)
    phone = Column(String)
    industry = Column(String)
    country = Column(String)
    preferences = Column(JSON)
    created_at = Column(DateTime)
class Quotation(Base):
    __tablename__ = "quotations"
    quotation_id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer)  # foreign key can be added later
    sku_list = Column(JSON)
    quantities = Column(JSON)
    delivery_country = Column(String)
    status = Column(String)
    total_price_estimate = Column(Float)
    expiry_date = Column(DateTime)
    created_at = Column(DateTime)
class InteractionLog(Base):
    __tablename__ = "interaction_logs"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    session_id = Column(String)
    query = Column(String)
    recommended_sku = Column(String)
    confidence_score = Column(Float)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime)
