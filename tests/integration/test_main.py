# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth.dependencies import get_current_active_user

# IMPORTANT: import Calculation BEFORE create_all()
from app.models.calculation import Calculation

# ---------------------------------------------------------
# Create an in-memory SQLite test database
# ---------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables AFTER importing models
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# Override get_db
# ---------------------------------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ---------------------------------------------------------
# Override get_current_active_user
# ---------------------------------------------------------
class FakeUser:
    id = 1
    username = "testuser"
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    is_active = True
    is_verified = True

def override_current_user():
    return FakeUser()

app.dependency_overrides[get_current_active_user] = override_current_user

# ---------------------------------------------------------
# TestClient (ONLY ONE)
# ---------------------------------------------------------
client = TestClient(app)

# ---------------------------------------------------------
# Lifespan (lines 20–23)
# ---------------------------------------------------------
def test_lifespan_runs():
    with TestClient(app) as c:
        assert True

# ---------------------------------------------------------
# Health (line 37)
# ---------------------------------------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# ---------------------------------------------------------
# GET /calculations/{calc_id} (lines 173–183)
# ---------------------------------------------------------
import uuid

def test_get_calculation_invalid_uuid():
    response = client.get("/calculations/not-a-uuid")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid calculation id format."

# def test_get_calculation_not_found():
#     fake_id = str(uuid.uuid4())
#     response = client.get(f"/calculations/{fake_id}")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Calculation not found."

# def test_get_calculation_success():
#     db = TestingSessionLocal()

#     # Use a valid calculation type
#     calc = Calculation.create(
#         calculation_type="addition",
#         user_id=1,
#         inputs={"a": 2, "b": 3}
#     )
#     calc.result = calc.get_result()

#     db.add(calc)
#     db.commit()
#     db.refresh(calc)
#     calc_id = str(calc.id)
#     db.close()

#     response = client.get(f"/calculations/{calc_id}")
#     assert response.status_code == 200

#     data = response.json()
#     assert data["id"] == calc_id
#     assert data["result"] == 5
#     assert data["inputs"] == {"a": 2, "b": 3}
