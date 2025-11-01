import pandas as pd
import logging
import os
import sys

BASE_DIR = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)

from api.database import SessionLocal, engine
from api.models import Base, Book


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FINAL_CSV_PATH = os.path.join(BASE_DIR, "data", "books.csv")

def populate_database(overwrite: bool = False):
    Base.metadata.create_all(bind=engine)

    try:
        if not os.path.exists(FINAL_CSV_PATH):
            logger.error(f"CSV file not found at path: {FINAL_CSV_PATH}")
            return
        
        df = pd.read_csv(FINAL_CSV_PATH)
        
        if df.empty:
            logger.warning("The CSV file is empty. No data to populate.")
            return
    except Exception as e:
        logger.error(f"An error occurred while reading the CSV file: {e}")
        return

    db = SessionLocal()

    try:
        existing_books = db.query(Book).count()
        if existing_books > 0 and not overwrite:
            logger.warning("Database already populated. Use 'overwrite=True' to reload data.")
            logger.warning("skipping data population.")
            return
        
        if overwrite:
            logger.info("Overwriting mode enabled. Clearing existing data.")
            db.query(Book).delete()
            db.commit()
            logger.info("Existing data cleared.")
        
        logger.info("Populating database with data from CSV...")

        if 'id' in df.columns:
            logger.warning("Column 'id' found in CSV. Removing it.")
            df = df.drop(columns=['id'])

        books_data = df.to_dict(orient="records")

        db.bulk_insert_mappings(Book, books_data)
        db.commit()
        logger.info("Database population completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during database population: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":

    do_overwrite = "overwrite" in sys.argv
    populate_database(overwrite=do_overwrite)
