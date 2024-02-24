# Test Configurations File
import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database.connector import Base, get_db
from app.main import app


# Setup database for tests to use an external test.db
# SQLalchmey with FastAPI Initialization
@pytest.fixture(scope="session")
def init_app() -> app:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
                            poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()          
    app.dependency_overrides[get_db] = override_get_db
    
    yield app, override_get_db

    Base.metadata.drop_all(bind=engine)


# Client Initialization
@pytest.fixture
def init_client(init_app) -> TestClient:

    client = TestClient(init_app[0])
    session = next(init_app[1]())
    session.execute(text("DELETE FROM pages"))
    session.execute(text("DELETE FROM buckets;"))
    session.execute(text("DELETE FROM users;"))

    session.commit()
    session.close()

    yield client
