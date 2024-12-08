# tests/test_chat_interface.py

import pytest
from fastapi.testclient import TestClient
from src.chat_interface import app, CredentialStore, cipher_suite

client = TestClient(app)

@pytest.fixture
def mock_credentials():
    """
    Provide mock credentials for testing.
    """
    return {
        "exchange": "binance",
        "api_key": "test_api_key",
        "secret_key": "test_api_secret",
    }

def test_set_credentials(mock_credentials):
    """
    Test storing API credentials through the chat interface.
    """
    response = client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 on success"
    assert response.json() == {"status": "success", "message": "Credentials stored for binance"}

def test_set_credentials_existing(mock_credentials):
    """
    Test storing credentials for an already existing exchange.
    """
    # First, set the credentials
    client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    
    # Attempt to set again
    response = client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should allow updating existing credentials"
    assert response.json() == {"status": "success", "message": "Credentials stored for binance"}

def test_get_credentials(mock_credentials):
    """
    Test retrieving credentials through the chat interface.
    """
    # First, set the credentials
    client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    
    # Get the credentials
    response = client.get("/get_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 on success"
    creds = response.json()["credentials"]
    assert creds["api_key"] == mock_credentials["api_key"], "API key should match the stored value"
    assert creds["secret_key"] == mock_credentials["secret_key"], "Secret key should match the stored value"

def test_get_credentials_nonexistent():
    """
    Test retrieving credentials for a broker with no stored credentials.
    """
    response = client.get("/get_credentials/unknown_broker", auth=("admin", "securepassword123"))
    assert response.status_code == 404, "API should return 404 for missing credentials"
    assert response.json()["detail"] == "Credentials for unknown_broker not found"

def test_delete_credentials(mock_credentials):
    """
    Test deleting credentials through the chat interface.
    """
    # First, set the credentials
    client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    
    # Delete the credentials
    response = client.delete("/delete_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 on successful deletion"
    assert response.json() == {"status": "success", "message": "Credentials for binance deleted."}
    
    # Attempt to get deleted credentials
    response = client.get("/get_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 404, "API should return 404 for deleted credentials"

def test_list_exchanges(mock_credentials):
    """
    Test listing all exchanges with stored credentials.
    """
    # Ensure no exchanges initially
    response = client.get("/list_exchanges", auth=("admin", "securepassword123"))
    assert response.status_code == 200
    assert response.json()["exchanges"] == []
    
    # Set credentials for binance
    client.post("/set_credentials", json=mock_credentials, auth=("admin", "securepassword123"))
    
    # List exchanges
    response = client.get("/list_exchanges", auth=("admin", "securepassword123"))
    assert response.status_code == 200
    assert "binance" in response.json()["exchanges"]
