import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
import importlib
import sys

DATABASE_MODULE = "app.database"

@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to mock the settings.DATABASE_URL before app.database is imported."""
    mock_url = "postgresql://user:password@localhost:5432/test_db"
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = mock_url
    # Ensure 'app.database' is not loaded
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    # Patch settings in 'app.database'
    monkeypatch.setattr(f"{DATABASE_MODULE}.settings", mock_settings)
    return mock_settings

def reload_database_module():
    """Helper function to reload the database module after patches."""
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)

def test_base_declaration(mock_settings):
    """Test that Base is an instance of declarative_base."""
    database = reload_database_module()
    Base = database.Base
    assert isinstance(Base, database.declarative_base().__class__)

def test_get_engine_success(mock_settings):
    """Test that get_engine returns a valid engine."""
    database = reload_database_module()
    engine = database.get_engine()
    assert isinstance(engine, Engine)

def test_get_engine_failure(mock_settings):
    """Test that get_engine raises an error if the engine cannot be created."""
    database = reload_database_module()
    with patch("app.database.create_engine", side_effect=SQLAlchemyError("Engine error")):
        with pytest.raises(SQLAlchemyError, match="Engine error"):
            database.get_engine()

def test_get_sessionmaker(mock_settings):
    """Test that get_sessionmaker returns a valid sessionmaker."""
    database = reload_database_module()
    engine = database.get_engine()
    SessionLocal = database.get_sessionmaker(engine)
    assert isinstance(SessionLocal, sessionmaker)


from unittest.mock import MagicMock, patch
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db, get_engine, get_sessionmaker


# def test_get_db_yields_and_closes_session():
#     mock_session = MagicMock(spec=Session)

#     # Patch SessionLocal so get_db() uses our mock session
#     with patch("app.database.SessionLocal", return_value=mock_session):
#         gen = get_db()

#         # First yield gives us the session
#         db = next(gen)
#         assert db is mock_session

#         # Exhaust generator to trigger finally block
#         try:
#             next(gen)
#         except StopIteration:
#             pass

#         # Ensure close() was called
#         mock_session.close.assert_called_once()


def test_get_engine_creates_engine():
    engine = get_engine("sqlite:///:memory:")
    assert isinstance(engine, Engine)


def test_get_sessionmaker_creates_sessionmaker():
    engine = get_engine("sqlite:///:memory:")
    maker = get_sessionmaker(engine)

    session = maker()
    assert isinstance(session, Session)
    assert session.bind is engine
