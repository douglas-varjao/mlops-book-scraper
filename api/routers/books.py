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

@router.get("/books/search", response_model=List[schemas.Book])
def search_books(
    # 2. Removemos o 'min_length' da validação automática
    title: Optional[str] = Query(None, description="Busca por título (parcial)"),
    category: Optional[str] = Query(None, description="Busca por categoria (parcial)"),
    db: Session = Depends(get_db)
):
    """
    Busca livros por título e/ou categoria.
    """
    
    # 3. Convertemos strings vazias "" para None
    if title == "":
        title = None
    if category == "":
        category = None

    # 4. Verificamos se pelo menos um foi fornecido
    if not title and not category:
        raise HTTPException(
            status_code=400, 
            detail="Forneça ao menos um critério de busca (title ou category)"
        )
        
    # 5. Fazemos a validação do min_length aqui dentro (muito mais robusto)
    if title and len(title) < 3:
        raise HTTPException(
            status_code=422, 
            detail="O 'title' deve ter pelo menos 3 caracteres"
        )
    if category and len(category) < 3:
        raise HTTPException(
            status_code=422, 
            detail="A 'category' deve ter pelo menos 3 caracteres"
        )
        
    books = crud.search_books(db, title=title, category=category)
    if not books:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado com esses critérios")
    return books

@router.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by its ID"""
    db_book = crud.get_book_id(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book



@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """List all unique book categories"""
    categories = crud.get_categories(db)
    return categories