import pytest
from fastapi.testclient import TestClient
from faker import Faker
from day_04_main import app
import main
from main import app as notes_app
from main_tag_3 import app as query_app
import requests

client = TestClient(app)
notes_client = TestClient(notes_app)
query_client = TestClient(query_app)
name_faker = Faker()


@pytest.fixture
def clean_notes(tmp_path, monkeypatch):
    """Redirect NOTES_FILE to a temp file so notes-tests don't touch real data"""
    temp_file = tmp_path / "notes.json"
    monkeypatch.setattr(main, "NOTES_FILE", temp_file)
    yield temp_file

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

##### Homework Space begins #####

def test_is_adult_returns_all_fields():
    """Test that the is-adult endpoint returns all expected fields with correct values"""
    response = client.get("/is-adult/25")
    assert response.status_code == 200
    data = response.json()

    assert "age" in data
    assert "is_adult" in data
    assert "can_vote" in data
    assert "can_drive" in data

    assert data["age"] == 25
    assert data["is_adult"] is True
    assert data["can_vote"] is True
    assert data["can_drive"] is True


def test_is_adult_invalid_age_type():
    """Test that the is-adult endpoint rejects non-integer age values"""
    response = client.get("/is-adult/abc")
    assert response.status_code == 422


def test_greetings_with_special_characters():
    """Test the greetings endpoint with names containing special characters and umlauts"""
    special_names = ["Lüce", "François", "José", "Müller-Schmidt", "O'Brien"]

    for name in special_names:
        response = client.get(f"/greetings/{name}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Hello {name}!"


# ============================================================================
# TESTS FOR main.py (Notes API)
# ============================================================================

def test_create_and_get_note(clean_notes):
    """Test creating a note and retrieving it by ID"""
    new_note = {
        "title": "Test Note",
        "content": "This is a test note",
        "category": "testing",
        "tags": ["pytest", "fastapi"]
    }

    create_response = notes_client.post("/notes", json=new_note)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == new_note["title"]
    assert created["content"] == new_note["content"]
    assert "id" in created
    assert "created_at" in created

    note_id = created["id"]
    get_response = notes_client.get(f"/notes/{note_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == note_id


def test_get_note_not_found(clean_notes):
    """Test that requesting a non-existent note returns 404"""
    response = notes_client.get("/notes/999999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_notes_stats_structure(clean_notes):
    """Test that the stats endpoint returns the expected structure"""
    response = notes_client.get("/notes/stats")
    assert response.status_code == 200
    data = response.json()

    assert "total_notes" in data
    assert "by_category" in data
    assert "top_tags" in data
    assert "unique_tags_count" in data

    assert isinstance(data["total_notes"], int)
    assert isinstance(data["by_category"], dict)
    assert isinstance(data["top_tags"], list)

# ============================================================================
# TESTS FOR main_tag_3.py (Query Parameters from Day 3)
# ============================================================================

def test_query_parameters_filter_names():
    """Test that the query parameter endpoint filters names correctly"""
    response = query_client.get("/queryparameters", params={"param1": "ar", "param2": 1})
    assert response.status_code == 200
    data = response.json()

    assert data["param1"] == "ar"
    assert data["param2"] == 1
    assert "filtered_names" in data
    assert "martin" in data["filtered_names"]
    assert "sarah" in data["filtered_names"]


def test_query_parameters_no_match():
    """Test that no matches returns an empty filtered list"""
    response = query_client.get("/queryparameters", params={"param1": "xyz", "param2": 0})
    assert response.status_code == 200
    data = response.json()

    assert data["filtered_names"] == []


def test_query_parameters_missing_required():
    """Test that missing required query parameters returns 422"""
    response = query_client.get("/queryparameters")
    assert response.status_code == 422




#### Own Try ####

