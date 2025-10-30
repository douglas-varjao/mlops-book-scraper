from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from api import models, schemas
from typing import List, Optional
from api.security import get_password_hash

def get_book_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def search_books(db: Session, title: Optional[str], category: Optional[str], limit: int = 100):
    query = db.query(models.Book)
    filters = []
    if title:
        filters.append(models.Book.title.ilike(f"%{title}%"))
    if category:
        filters.append(models.Book.category.ilike(f"%{category}%"))
    if filters:
        query = query.filter(and_(*filters))
    
    return query.limit(limit).all()

def get_categories(db: Session):
    query_result  = db.query(models.Book.category).distinct().order_by(models.Book.category).all()
    return [category[0] for category in query_result]

#------------------------------------------------------------------------------------------------------#

def get_stats_overview(db: Session) -> schemas.StatsOverview:
    total_books = db.query(models.Book).count()
    avg_price = db.query(func.avg(models.Book.price)).scalar()

    rating_dist_query = db.query(
        models.Book.rating, func.count(models.Book.rating).label('count')).group_by(models.Book.rating).order_by(
            models.Book.rating).all()
    rating_distribution = [
        schemas.RatingDistribution(rating=r.rating, count=r.count)
        for r in rating_dist_query if r.rating is not None
    ]
    return schemas.StatsOverview(
        total_books=total_books,
        average_price=round(avg_price, 2) if avg_price else 0.0,
        rating_distribution=rating_distribution
    )

def get_stats_categories(db: Session) -> List[schemas.CategoryStats]:
    query_result = db.query(
        models.Book.category,
        func.count(models.Book.id).label('book_count')
    ,
    func.avg(models.Book.price).label('average_price')
    ).group_by(models.Book.category).order_by(desc('book_count')).all()

    stats = [
        schemas.CategoryStats(
            category=r.category,
            book_count=r.book_count,
            average_price=round(r.average_price, 2) if r.average_price else None
        ) for r in query_result
    ]
    return stats

def get_top_rated_books(db: Session, limit: int = 10):
    return db.query(models.Book).order_by(desc(models.Book.rating)).limit(limit).all()

def get_get_books_by_price_range(db: Session, min_price: float, max_price: float, limit: int = 100):
    return db.query(models.Book).filter(
        models.Book.price.between(min_price, max_price)
        ).ordey_by(models.Book.price).limit(limit).all()

#------------------------------------------------------------------------------------------------------#

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db:Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password,
        is_admin = user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#------------------------------------------------------------------------------------------------------#

def get_ml_features(db: Session, limit: int = 1000) -> List[schemas.MLFeatures]:
    """Returns formatted data for features."""
    books = db.query(models.Book).filter(
        models.Book.price.isnot(None),
        models.Book.rating.isnot(None)
    ).limit(limit).all()

    features = [
        schemas.MLFeatures(
            book_id = b.id,
            price= b.price,
            rating= b.rating,
            availability= b.availability,
            category= b.category
        ) for b in books
    ]
    return features

def get_ml_training_data(db: Session, limit: int = 1000):
    """Returns raw data for ML training."""
    return db.query(models.Book).limit(limit).all()

