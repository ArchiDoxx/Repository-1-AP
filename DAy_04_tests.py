import pytest
import requests
from faker import Faker

name_faker = Faker()

BASE_URL = "http://localhost:8000"

def test_read_root():
    """Test the root endpoint return hello world"""
    response = requests.get(f"{BASE_URL}/")
    # assert status code 200 is ok
    assert response.status_code == 200

    # assert response body contains expected message
    data = response.json()
    assert data["message"] == "Hello World!"

def test_check_404_error():
    response = requests.get(f"{BASE_URL}/nonexistent")
    assert response.status_code == 404

def test_check_greetings():
    name = "martin"
    response = requests.get(f"{BASE_URL}/greetings/{name}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Hello {name}!"
