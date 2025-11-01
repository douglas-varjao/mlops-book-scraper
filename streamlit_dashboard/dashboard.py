import streamlit as st
import pandas as pd
import sqlalchemy
import os
import plotly.express as px
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

st.set_page_config(
    page_title="Books Dashboard",
    page_icon="📚",
    layout="wide"
)

@st.cache_resource
def get_db_engine():
    """Returns a database connection engine."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        st.error("The environment variable DATABASE_URL could not be found!")
        logger.error("DATABASE_URL not found. Check the .env file.")
        return None
    
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    try:
        engine_args = {}
        if db_url.startswith("sqlite"):
            engine_args["connect_args"] = {"check_same_thread": False}

        engine = sqlalchemy.create_engine(db_url, **engine_args)
        logger.info("")
        return engine
    except Exception as e:
        st.error(f"Error connecting to the database : {e}")
        logger.error(f"Error connecting to the database : {e}")
        return None
    
engine = get_db_engine()

@st.cache_data(ttl=600)
def load_data(_engine):
    """Loads the data from the 'books' table."""
    if _engine is None:
        logger.warning("The database engine is set to None. This returns an empty DataFrame.")
        return pd.DataFrame()
    
    try:
        with _engine.connect() as conn:
            query = "SELECT title, price, rating, availability, category FROM books"
            df = pd.read_sql(query, conn)
        logger.info(f"Data loaded successfully: {len(df)} rows.")
        return df
    except Exception as e:
        logger.error(f"Error loading data (table 'books' may not exist):{e}")
        return pd.DataFrame()

df = load_data(engine)

st.title("📚 Books API Metrics Dashboard")

if df.empty:
    st.warning("No data loaded. Is the database empty?")
    st.warning("If this is the first local execution, run: `python scripts/load_to_db.py`")
else:
    st.markdown(f"Analysis of **{len(df)}** books in the database.")

    st.header("Overview")

    avg_price = df['price'].mean()
    avg_rating = df['rating'].mean()
    total_categories = df['category'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total books", f"{len(df)}")
    col2.metric("Average price", f"£{avg_price:.2f}")
    col3.metric("Average rating", f"{avg_rating:.1f}⭐")

    st.divider()

    #----------------------------------------------------------------------------------------------------------------------------#

    st.header("Visual Analysis")

    col_left, col_right = st.columns(2)

    with col_left:
        #Price
        st.subheader("Price Distribution")
        fig_price = px.histogram(df, x='price', nbins=50, title="Frequency by Price Range")
        fig_price.update_layout(xaxis_title= "Preço (£)")
        st.plotly_chart(fig_price, use_container_width=True)

        #Rating
        st.subheader("Rating Distribution")
        rating_counts = df['rating'].value_counts().sort_index()
        fig_rating = px.bar(
            rating_counts,
            x=rating_counts.index,
            y=rating_counts.values,
            title="Book Count by Rating",
            labels={'x': 'Rating (Stars)', 'y': 'Number of Books'}
        )
        st.plotly_chart(fig_rating, use_container_width=True)

        with col_right:
            # top 15 categories
            st.subheader("Top 15 Categories with the Most Books")
            category_counts = df['category'].value_counts().nlargest(15).sort_values(ascending=True)
            fig_cat = px.bar(
                category_counts,
                x=category_counts.values,
                y=category_counts.index,
                orientation='h',
                title="Top 15 Categories",
                labels={'x':'Number of Books', 'y':'Category'}
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        st.divider()

        st.header("Explore Data")
        st.dataframe(df, use_container_width=True)





    