# PostgreSQL connection with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Look for .env in backend/ or the project root
_HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(_HERE, "..", ".env"))       # backend/.env
load_dotenv(os.path.join(_HERE, "..", "..", ".env"))  # project root

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that injects the DB session into each endpoint."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()