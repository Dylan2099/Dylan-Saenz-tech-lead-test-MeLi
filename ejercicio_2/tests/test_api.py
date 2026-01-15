from fastapi.testclient import TestClient
from src.api import app_api

client = TestClient(app_api)

def test_read_leaderboard():
    """Verifica que el endpoint de leaderboard responda 200 y sea una lista."""
    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_root_404():
    """Verifica que la raíz no exista (sanity check)."""
    response = client.get("/")
    assert response.status_code == 404