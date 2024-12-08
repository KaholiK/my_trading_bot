# tests/test_chat_interface.py

import pytest
from fastapi.testclient import TestClient
from src.chat_interface import app, CredentialStore, get_credential_store

client = TestClient(app)

@pytest.fixture
def mock_credentials():
    """
    Provide mock credentials for testing.
    """
    return {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "api_passphrase": "test_api_passphrase",
    }

@pytest.fixture
def mock_credential_store():
    """
    Set up a mock credential store for testing.
    """
    store = CredentialStore()
    store.credentials["binance"] = {
        "api_key": "existing_key",
        "api_secret": "existing_secret",
        "api_passphrase": "existing_passphrase",
    }
    return store

@pytest.fixture(autouse=True)
def override_dependency(mock_credential_store):
    """
    Override the get_credential_store dependency with the mock_credential_store.
    """
    app.dependency_overrides[get_credential_store] = lambda: mock_credential_store
    yield
    app.dependency_overrides[get_credential_store] = None

def test_store_credentials(mock_credentials):
    """
    Test storing API credentials through the chat interface.
    """
    response = client.post("/store-credentials", json={
        "broker": "coinbase",
        "api_key": mock_credentials["api_key"],
        "api_secret": mock_credentials["api_secret"],
        "api_passphrase": mock_credentials["api_passphrase"],
    })
    assert response.status_code == 200, "API should return 200 on success"
    assert response.json() == {"message": "Credentials stored successfully"}

def test_store_credentials_existing():
    """
    Test storing credentials for an already existing broker.
    """
    response = client.post("/store-credentials", json={
        "broker": "binance",
        "api_key": "new_key",
        "api_secret": "new_secret",
        "api_passphrase": "new_passphrase",
    })
    assert response.status_code == 400, "API should return 400 for existing credentials"
    assert response.json()["detail"] == "Credentials for binance already exist"

def test_get_credentials():
    """
    Test retrieving credentials through the chat interface.
    """
    response = client.get("/get-credentials/binance")
    assert response.status_code == 200, "API should return 200 on success"
    credentials = response.json()
    assert credentials["api_key"] == "existing_key", "API key should match the stored value"
    assert credentials["api_secret"] == "existing_secret", "API secret should match the stored value"

def test_get_credentials_nonexistent():
    """
    Test retrieving credentials for a broker with no stored credentials.
    """
    response = client.get("/get-credentials/unknown_broker")
    assert response.status_code == 404, "API should return 404 for missing credentials"
    assert response.json()["detail"] == "Credentials for unknown_broker not found"

def test_chat_endpoint():
    """
    Test the /chat endpoint for processing user queries.
    """
    response = client.post("/chat", json={"query": "What is my balance?"})
    assert response.status_code == 200, "API should return 200 on success"
    assert "response" in response.json(), "Response should include a reply"
