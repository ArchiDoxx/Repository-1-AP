# ============================================================================
# DAY 4 HOMEWORK – Comprehensive test suite for the Notes API
# ============================================================================
# Covers: Task 1 (CRUD), Task 2 (Filtering), Task 3 (Errors), Task 4 (Day 3)
# Uses FastAPI TestClient – no running server needed.
# Run: uv run pytest day-04-hometests.py -v
# ============================================================================

import pytest
from fastapi.testclient import TestClient
import main
from main import app

client = TestClient(app)

# ─── Fixture & helpers ────────────────────────────────────────────────────────

@pytest.fixture
def clean_notes(tmp_path, monkeypatch):
    """Redirect NOTES_FILE to a temp file so tests never touch real data."""
    temp_file = tmp_path / "notes.json"
    monkeypatch.setattr(main, "NOTES_FILE", temp_file)
    yield temp_file


NOTE = {
    "title": "Test Note",
    "content": "Test content",
    "category": "Testing",
    "tags": ["test", "pytest"],
}


def _create(data=None):
    """Helper: POST a note and return its JSON."""
    return client.post("/notes", json=data or NOTE).json()


# ============================================================================
# Task 1 – Basic CRUD
# ============================================================================

def test_create_note(clean_notes):
    """POST /notes returns 201 with id and created_at."""
    response = client.post("/notes", json=NOTE)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == NOTE["title"]
    assert "id" in data
    assert "created_at" in data


def test_list_notes(clean_notes):
    """GET /notes returns a list."""
    response = client.get("/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_note_by_id(clean_notes):
    """GET /notes/{id} returns the correct note."""
    note_id = _create()["id"]
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id


def test_update_note(clean_notes):
    """PUT /notes/{id} replaces all fields and returns 200."""
    note_id = _create()["id"]
    updated = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Updated",
        "tags": ["updated"],
    }
    response = client.put(f"/notes/{note_id}", json=updated)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"


def test_delete_note(clean_notes):
    """DELETE /notes/{id} removes the note; follow-up GET returns 404."""
    note_id = _create()["id"]
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
    assert client.get(f"/notes/{note_id}").status_code == 404


# ============================================================================
# Task 2 – Filtering
# ============================================================================

def test_filter_by_category(clean_notes):
    """GET /notes?category=Work only returns notes in that category."""
    for i in range(3):
        client.post("/notes", json={
            "title": f"Work Note {i}", "content": "Content",
            "category": "Work", "tags": [],
        })
    client.post("/notes", json={
        "title": "Personal Note", "content": "Content",
        "category": "Personal", "tags": [],
    })

    response = client.get("/notes?category=Work")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 3
    for note in notes:
        assert note["category"] == "Work"


def test_filter_by_search(clean_notes):
    """GET /notes?search=meeting only returns notes whose title/content matches."""
    client.post("/notes", json={
        "title": "Important meeting notes", "content": "Discussed project timeline",
        "category": "Work", "tags": [],
    })
    client.post("/notes", json={
        "title": "Shopping list", "content": "Milk, eggs, bread",
        "category": "Personal", "tags": [],
    })

    response = client.get("/notes?search=meeting")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert "meeting" in notes[0]["title"].lower()


def test_filter_by_tag(clean_notes):
    """GET /notes?tag=urgent only returns notes with that tag."""
    client.post("/notes", json={
        "title": "Urgent task", "content": "Must finish today",
        "category": "Work", "tags": ["urgent", "work"],
    })
    client.post("/notes", json={
        "title": "Normal task", "content": "Can wait",
        "category": "Work", "tags": ["work"],
    })

    response = client.get("/notes?tag=urgent")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert "urgent" in notes[0]["tags"]


def test_combined_filters(clean_notes):
    """GET /notes?category=Work&tag=urgent&search=meeting applies all three filters."""
    client.post("/notes", json={
        "title": "Work meeting", "content": "Agenda for tomorrow",
        "category": "Work", "tags": ["urgent"],
    })
    client.post("/notes", json={
        "title": "Personal meeting", "content": "Doctor appointment",
        "category": "Personal", "tags": ["urgent"],
    })
    client.post("/notes", json={
        "title": "Work task", "content": "No meeting here",
        "category": "Work", "tags": [],
    })

    response = client.get("/notes?category=Work&tag=urgent&search=meeting")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["category"] == "Work"
    assert "urgent" in notes[0]["tags"]


def test_date_filtering(clean_notes):
    """GET /notes?created_after filters out notes before the given date."""
    _create()

    response = client.get("/notes?created_after=2020-01-01")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response_empty = client.get("/notes?created_after=2099-01-01")
    assert response_empty.status_code == 200
    assert response_empty.json() == []


# ============================================================================
# Task 3 – Error cases
# ============================================================================

def test_create_note_missing_field(clean_notes):
    """POST /notes with missing required fields returns 422."""
    response = client.post("/notes", json={"title": "Only title"})
    assert response.status_code == 422


def test_get_nonexistent_note(clean_notes):
    """GET /notes/99999 returns 404 with a detail message."""
    response = client.get("/notes/99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_nonexistent_note(clean_notes):
    """PUT /notes/99999 returns 404."""
    response = client.put("/notes/99999", json={
        "title": "X", "content": "X", "category": "X", "tags": [],
    })
    assert response.status_code == 404


def test_delete_nonexistent_note(clean_notes):
    """DELETE /notes/99999 returns 404."""
    response = client.delete("/notes/99999")
    assert response.status_code == 404


# ============================================================================
# Task 4 – Day 3 Homework Features (stats, categories, PATCH)
# ============================================================================

def test_notes_statistics(clean_notes):
    """GET /notes/stats returns the expected structure and correct counts."""
    for category in ["Work", "Work", "Personal"]:
        client.post("/notes", json={
            "title": "Note", "content": "Content",
            "category": category, "tags": ["common"],
        })

    response = client.get("/notes/stats")
    assert response.status_code == 200
    data = response.json()

    assert "total_notes" in data
    assert "by_category" in data
    assert "top_tags" in data
    assert "unique_tags_count" in data

    assert data["total_notes"] == 3
    assert data["by_category"]["Work"] == 2
    assert data["by_category"]["Personal"] == 1


def test_list_categories(clean_notes):
    """GET /categories returns all unique categories."""
    for cat in ["Work", "Personal", "Study"]:
        client.post("/notes", json={
            "title": "Note", "content": "Content", "category": cat, "tags": [],
        })

    response = client.get("/categories")
    assert response.status_code == 200
    categories = response.json()
    assert "Work" in categories
    assert "Personal" in categories
    assert "Study" in categories


def test_notes_by_category(clean_notes):
    """GET /categories/{name}/notes returns only notes in that category."""
    client.post("/notes", json={
        "title": "Work Note", "content": "Content", "category": "Work", "tags": [],
    })
    client.post("/notes", json={
        "title": "Personal Note", "content": "Content", "category": "Personal", "tags": [],
    })

    response = client.get("/categories/Work/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["category"] == "Work"


def test_patch_note_title_only(clean_notes):
    """PATCH /notes/{id} with only title leaves other fields unchanged."""
    created = _create()
    note_id = created["id"]
    original_content = created["content"]

    response = client.patch(f"/notes/{note_id}", json={"title": "Patched Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Patched Title"
    assert data["content"] == original_content


def test_patch_multiple_fields(clean_notes):
    """PATCH /notes/{id} with title+content leaves category unchanged."""
    created = _create()
    note_id = created["id"]
    original_category = created["category"]

    response = client.patch(f"/notes/{note_id}", json={
        "title": "Multi Patch",
        "content": "New content",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Multi Patch"
    assert data["content"] == "New content"
    assert data["category"] == original_category
