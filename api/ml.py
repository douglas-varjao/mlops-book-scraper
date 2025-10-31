from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random

from api import schemas, models, crud
from api.database import get_db
from api.security import get_current_admin_user

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["ML Models & Predictions (Bônus)"],
    dependencies=[Depends(get_current_admin_user)]
)

@router.get("/features", response_model=List[schemas.MLFeatures])
def get_ml_features(limit: int = 1000, db: Session = Depends(get_db)):
    """[AUTH] Returns data formatted as 'features' for ML models."""
    return crud.get_ml_training_data(db, limit=limit)

@router.get("/training-data", response_model=List[schemas.Book])
def get_ml_training_data(limit: int = 1000, db: Session = Depends(get_db)):
    
    