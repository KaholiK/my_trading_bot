# tests/test_chat_interface.py

import pytest
from fastapi.testclient import TestClient
from src.chat_interface import app

client = TestClient(app)

def test_set_credentials():
    """
    Test setting credentials for a broker.
    """
    response = client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    assert response.status_code == 200, "API should return 200 for successful credential setting"
    assert response.json()["message"] == "Credentials for binance set successfully"

def test_set_credentials_existing():
    """
    Test setting credentials for a broker that already has credentials.
    """
    # First, set credentials
    client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    # Update credentials
    response = client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "new_api_key",
            "api_secret": "new_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    assert response.status_code == 200, "API should return 200 for updating existing credentials"
    assert response.json()["message"] == "Credentials for binance set successfully"

def test_get_credentials():
    """
    Test retrieving credentials for a broker.
    """
    # Ensure credentials are set
    client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
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
    # Ensure credentials are set
    client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    # Delete credentials
    response = client.delete("/delete_credentials/binance", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for successful credential deletion"
    assert response.json()["message"] == "Credentials for binance deleted successfully"

def test_list_exchanges():
    """
    Test listing available exchanges.
    """
    # Ensure multiple credentials are set
    client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    client.post(
        "/set_credentials",
        json={
            "broker": "coinbase",
            "api_key": "coinbase_api_key",
            "api_secret": "coinbase_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    response = client.get("/list_exchanges", auth=("admin", "securepassword123"))
    assert response.status_code == 200, "API should return 200 for listing exchanges"
    assert isinstance(response.json(), list), "API response should be a list of exchanges"
    assert "binance" in response.json(), "Exchange 'binance' should be listed"
    assert "coinbase" in response.json(), "Exchange 'coinbase' should be listed"

def test_chat_endpoint():
    """
    Test the /chat endpoint with a valid prompt.
    """
    # Ensure credentials are set (required for auth)
    client.post(
        "/set_credentials",
        json={
            "broker": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        },
        auth=("admin", "securepassword123")
    )
    response = client.post(
        "/chat",
        json={
            "prompt": "Generate a trading strategy for BTCUSD based on current market trends."
        },
        auth=("admin", "securepassword123")
    )
    assert response.status_code == 200, "API should return 200 for successful chat response"
    assert "reply" in response.json(), "API response should include 'reply'"
    assert isinstance(response.json()["reply"], str), "Reply should be a string"
    assert len(response.json()["reply"]) > 0, "Reply should not be empty"
