from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from api import schemas
from api.database import get_db
import logging

router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health Check"]
)


@router.get("", response_model=schemas.HealthCheck)
def health_check(db: Session = Depends(get_db)):
    """health check endpoint to verify API is running"""
    try:
        db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        logging.error(f"Health check: Database connection failed: {e}")
        raise HTTPException(status_code=503, detail= f"database connection error: {e}")
    return {"status": "ok", "database": db_status}
