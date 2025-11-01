from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any


class BookBase(BaseModel):
    title: str
    price: Optional[float] = None
    rating: Optional[int] = None
    availability: Optional[int] = None
    category: str
    image_url: Optional[str] = None
    product_url: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    created_at: datetime


    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    is_admin: bool = False


class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class HealthCheck(BaseModel):
    status: str
    database: str


class RatingDistribution(BaseModel):
    rating: int
    count: int


class StatsOverview(BaseModel):
    total_books: int
    average_price: float
    rating_distribution: List[RatingDistribution]


class CategoryStats(BaseModel):
    category: str
    book_count: int
    average_price: Optional[float]= None


class MLFeatures(BaseModel):
    book_id: int
    price: float
    rating: int
    availability: int
    category: str


class MLPredictionRequest(BaseModel):
    price: float
    rating: int


class MLPredictionResponse(BaseModel):
    book_id: Optional[int] = None
    predicted_sales_cluster: str
    confidence_score: float