from fastapi.testclient import TestClient

from backend.main import app


def test_health_returns_ok():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_symbol_returns_documented_safe_error():
    response = TestClient(app).get("/api/research/NOT%20VALID")
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Use a short market symbol such as AAPL, NVDA, or XAUUSD.",
        "code": "invalid_symbol",
    }
