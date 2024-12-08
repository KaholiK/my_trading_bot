import pytest
from fastapi.testclient import TestClient
from src.chat_interface import app

client = TestClient(app)

def test_set_credentials():
    """
    Test setting credentials for a broker.
    """
    response = client.post("/set_credentials", json={
        "broker": "binance",
        "api_key": "test_api_key",
        "api_secret": "test_api_secret"
    }, auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for successful credential setting"

def test_set_credentials_existing():
    """
    Test setting credentials for a broker that already has credentials.
    """
    response = client.post("/set_credentials", json={
        "broker": "binance",
        "api_key": "new_api_key",
        "api_secret": "new_api_secret"
    }, auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for updating existing credentials"

def test_get_credentials():
    """
    Test retrieving credentials for a broker.
    """
    response = client.get("/get_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for existing credentials"
    assert "api_key" in response.json(), "API response should include 'api_key'"
    assert "api_secret" in response.json(), "API response should include 'api_secret'"

def test_get_credentials_nonexistent():
    """
    Test retrieving credentials for a broker with no stored credentials.
    """
    response = client.get("/get_credentials/unknown_broker", auth=("admin", "securepassword123"))
    assert response.status_code == 404, "API should return 404 for missing credentials"
    assert response.json()["detail"] == "Credentials for unknown_broker not found.", "Error message should end with a period"

def test_delete_credentials():
    """
    Test deleting credentials for a broker.
    """
    response = client.delete("/delete_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for successful credential deletion"

def test_list_exchanges():
    """
    Test listing available exchanges.
    """
    response = client.get("/list_exchanges", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for listing exchanges"
    assert isinstance(response.json(), list), "API response should be a list of exchanges"
