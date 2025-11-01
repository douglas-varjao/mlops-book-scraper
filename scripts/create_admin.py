import os
import logging
import sys
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


load_dotenv(os.path.join(BASE_DIR, ".env"))


from api.database import SessionLocal, engine
from api.models import Base, User
from api.security import get_password_hash 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_admin():
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:

        username = os.getenv("INIT_ADMIN_USERNAME")
        email = os.getenv("INIT_ADMIN_EMAIL")
        password = os.getenv("INIT_ADMIN_PASSWORD")

        if not all([username, email, password]):
            logger.error("ERROR: Admin variables (INIT_ADMIN_...) are not in .env.")
            logger.error("Please copy .env.example to .env and fill it in.")
            return


        existing_admin = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_admin:
            logger.warning(f"Username '{username}' or email address '{email}' already exists. No action taken.")
            return


        logger.info(f"Creating an admin user: {username} ({email})")
        hashed_password = get_password_hash(password)
        
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"User admin '{username}' created successfully.")
        
    except Exception as e:
        logger.error(f"Error creating initial admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()