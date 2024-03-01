import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

load_dotenv()

if "dbtype" in os.environ and os.environ["dbtype"] == "postgres":
    dbname = os.environ["dbname"]
    user = os.environ["user"]
    password = os.environ["password"]
    url = os.environ["url"]

    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{url}/{dbname}"
    print(SQLALCHEMY_DATABASE_URL)
    print("Using PostgreSQL as backend")

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
    print("Using SQLite as backend")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
