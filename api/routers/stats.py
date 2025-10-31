from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from api import schemas, crud
from api.database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["Stats & insights (Optional)"]
)

@router.get("/stats/overview", response_model=schemas.StatsOverview)
def get_stats_overview(db: Session = Depends(get_db)):
    """Returns an overview of book statistics including total , average price, and rating distribution."""
    return crud.get_stats_overview(db)

@router.get("/stats/categories", response_model=List[schemas.CategoryStats])
def get_stats_categories(db: Session = Depends(get_db)):
    """Returns statistics for each book category including book count and average price."""
    return crud.get_stats_categories(db)

@router.get("/books/top-rated", response_model=List[schemas.Book])
def get_top_rated_books(limit: int = 10, db: Session = Depends(get_db)):
    """Returns the top-rated books limited by the specified number."""
    return crud.get_top_rated_books(db, limit=limit)

@router.get("/books/price-range", response_model=List[schemas.Book])
def get_books_by_price_range(
    min: float = Query(0.0, description="Minimum price"),
    max: float = Query(100.0, description="Maximum price"),
    db: Session = Depends(get_db)):
    """Returns books within the specified price range."""
    if min > max:
        raise HTTPException(status_code=400, detail="Minimum price cannot be greater than maximum price.")
    return crud.get_books_by_price_range(db, min_price=min, max_price=max)