from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ----------------------------------------------------------------------
# Lifespan (lines 20–23)
# ----------------------------------------------------------------------
def test_lifespan_runs():
    with TestClient(app) as c:
        assert True

# ----------------------------------------------------------------------
# Health (line 37)
# ----------------------------------------------------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

