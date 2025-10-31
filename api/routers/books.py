from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from api import crud, models, schemas
from api.database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["Books (Core)"]
)

@router.get("/books", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all books avaliable in th database(paginated)"""
    books = crud.get_books(db, skip=skip, limit=limit)
    return books

@router.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by its ID"""
    db_book = crud.get_book_id(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/books/search", response_model=List[schemas.Book])
def search_books(
    title: Optional[str] = Query(None, min_length=3, description="Search books by title"),
    category: Optional[str] = Query(None, min_length=3, description="Search books by category"),
    db: Session = Depends(get_db)
):
    """Search books by title or category"""
    if not title and not category:
        raise HTTPException(status_code=400, detail="Please provide at least a 'title' or 'category'.")
    
    books = crud.search_books(db, title=title, category=category)
    if not books:
        raise HTTPException(status_code=404, detail="No books found matching the criteria.")
    return books

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """List all unique book categories"""
    categories = crud.get_categories(db)
    return categories