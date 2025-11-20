from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_read_hello():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
