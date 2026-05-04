import pytest
from fastapi.testclient import TestClient
from faker import Faker
from day_04_main import app

client = TestClient(app)
name_faker = Faker()

def test_read_root():
    """Test the root endpoint return hello world"""
    response = client.get("/")
    # assert status code 200 is ok
    assert response.status_code == 200

    # assert response body contains expected message
    data = response.json()
    assert data["message"] == "Hello World!"

def test_check_404_error():
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_check_greetings():
    """Test the personalized greeting endpoint with multiple random names """
    for _ in range(10):
        name = name_faker.first_name()
        response = client.get(f"/greetings/{name}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Hello {name}!"


def test_check_is_adult():
    """Test if adult check works correctly"""

    for age in range(0, 41):
        adult = age >= 18
        response = client.get(f"/is-adult/{age}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_adult"] == adult