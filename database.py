from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch the connection URL
DATABASE_URL = "sqlite:///./app.db"

Base = declarative_base()

class CountryDB(Base):
        __tablename__ = "countries"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), unique=True, nullable=False, index=True)
        capital = Column(String(255))
        region = Column(String(255), index=True)
        population = Column(Integer, nullable=False)
        currency_code = Column(String(6), index=True)
        exchange_rate = Column(Float)
        estimated_gdp = Column(Float)
        flag_url = Column(String(512))
        last_refreshed_at = Column(DateTime, default=func.now(), onupdate=func.now())

        def __repr__(self):
                return f"<Country(name='{self.name}', population={self.population})>"

engine = create_engine(DATABASE_URL, #sconnect_args={"check_same_thread": False}, 
    future=True)
   
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
# Function to create tables (called once at startup)
def create_db_tables():
    """Creates all tables defined in Base (like CountryDB) in the database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    
def get_db():
    """Provides a database session to a FastAPI endpoint and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # The session is closed, ensuring resources are released
        db.close()
