from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from api import crud, schemas, models
from api.database import get_db
from api.security import(
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_admin_user
)

from scripts.load_to_db import populate_database

router = APIRouter(
    prefix="/api/v1",
    tags=["Autentication & Admin (Bonus)"]
)


@router.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Obtain an token JWT by providing valid username and password."""
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/scraping/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_data_load(
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    current_admin: models.User = Depends(get_current_admin_user)
):
    """[ADMIN] Triggers the loading of data from 'books.csv' into the database.
Runs in the background to avoid blocking the API."""
    background_tasks.add_task(populate_database, overwrite=overwrite)

    return{"message": "Data loading process initiated in the background.",
           "admin_user": current_admin.username,
           "overwrite": overwrite}


@router.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_new_user(
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """ Registers a new regular user in the system. """
    db_user = crud.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered. Please try another."
        )

    # 2. Verifica se o e-mail já existe
    db_email = crud.get_user_by_email(db, email=user_data.email)
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already registered. Please try a different one."
        )
    user_data.is_admin = False

    new_user = crud.create_user(db=db, user=user_data)

    return new_user