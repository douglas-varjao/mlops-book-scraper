from sqlalchemy import column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from api.database import Base

class Book(Base):
    __tablename__ = "books"

    id = column(Integer, primary_key=True, index=True)
    title = column(String, index=True)
    price = column(Float)
    rating = column(Integer)
    availability = column(String)
    category = column(String, index=True)
    image_url = column(String)
    product_url = column(String, unique=True, index=True)
    created_at = column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = column(Integer, primary_key=True, index=True)
    username = column(String, unique=True, index=True)
    email = column(String, unique=True, index=True)
    hashed_password = column(String)
    is_admin = column(Boolean, default=False)
    created_at = column(DateTime(timezone=True), server_default=func.now())
