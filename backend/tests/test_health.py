from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "not_ready"]


def test_docs_available():
    response = client.get("/docs")

    assert response.status_code == 200