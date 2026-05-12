"""
Day 5 Task 6 — Validation Tests

Prüft die Pydantic-Härtung aus Day 5 Tasks 1-5:
  - Field()-Constraints (Längen)
  - ConfigDict(str_strip_whitespace, extra="forbid")
  - Custom field_validators (title-Whitespace, category-Whitelist)
  - Tag-Normalization + Pattern-Check (Task 5)
  - NoteUpdate (PATCH) mit gleichen Regeln

Läuft direkt gegen die FastAPI-App via TestClient — kein laufender Server nötig.
Die clean_notes-Fixture leitet die SQLite-DB auf eine temporäre Datei um,
damit die echte notes.db nicht angefasst wird.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine

import main
from main import app

client = TestClient(app)


@pytest.fixture
def clean_notes(tmp_path, monkeypatch):
    """Temporäre SQLite-DB pro Test — gleicher Pattern wie test_main.py."""
    temp_db = tmp_path / "notes.db"
    test_engine = create_engine(f"sqlite:///{temp_db}")
    SQLModel.metadata.create_all(test_engine)
    monkeypatch.setattr(main, "engine", test_engine)
    yield temp_db


def _valid_payload(**overrides):
    """Baseline-Payload, der ALLE Day-5-Regeln erfüllt."""
    payload = {
        "title": "Valid Title",
        "content": "Valid content",
        "category": "work",
        "tags": ["alpha", "beta"],
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Task 1: Field-Constraints (Länge / Anzahl)
# ---------------------------------------------------------------------------

def test_create_note_rejects_short_title(clean_notes):
    """title < 3 Zeichen (auch nach Strip) muss 422 ergeben."""
    response = client.post("/notes", json=_valid_payload(title="ab"))
    assert response.status_code == 422


def test_create_note_rejects_whitespace_only_title(clean_notes):
    """Whitespace-only title wird auto-stripped und dann zu kurz -> 422.
    Test für str_strip_whitespace=True + min_length=3."""
    response = client.post("/notes", json=_valid_payload(title="   "))
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Task 2: Category-Whitelist
# ---------------------------------------------------------------------------

def test_create_note_rejects_unknown_category(clean_notes):
    """category außerhalb von {work,personal,school,ideas,general} -> 422."""
    response = client.post("/notes", json=_valid_payload(category="banana"))
    assert response.status_code == 422


def test_create_note_normalizes_category_to_lowercase(clean_notes):
    """category 'WORK' wird auf 'work' normalisiert (in der Whitelist)."""
    response = client.post("/notes", json=_valid_payload(category="WORK"))
    assert response.status_code == 201
    assert response.json()["category"] == "work"


# ---------------------------------------------------------------------------
# Task 2 / Task 5: Tag-Normalization & Pattern
# ---------------------------------------------------------------------------

def test_create_note_normalizes_tags(clean_notes):
    """Tags werden stripped + lowercased + dedupliziert."""
    response = client.post(
        "/notes",
        json=_valid_payload(tags=["URGENT", "urgent", "  Meeting  "]),
    )
    assert response.status_code == 201
    assert sorted(response.json()["tags"]) == ["meeting", "urgent"]


def test_tag_name_rejects_uppercase_only(clean_notes):
    """Tag-Pattern erfordert [a-z0-9-]+. 'no_underscore' (Underscore) ist nicht erlaubt."""
    response = client.post(
        "/notes",
        json=_valid_payload(tags=["valid", "no_underscore"]),
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Task 1: ConfigDict(extra="forbid")
# ---------------------------------------------------------------------------

def test_create_note_forbids_extra_fields(clean_notes):
    """Tippfehler wie 'tagz' (statt 'tags') werden mit 422 abgelehnt."""
    payload = _valid_payload()
    payload["tagz"] = ["typo"]  # extra field
    response = client.post("/notes", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Task 3 (didaktisch, NICHT aktiv) — siehe Kommentar in main.py NoteCreate
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason="Task 3 ist absichtlich auskommentiert (siehe main.py NoteCreate), "
           "weil das Referenz-test_suit.py work-Notizen ohne work-Tag erstellt."
)
def test_work_note_requires_work_tag(clean_notes):
    """Wenn Task 3 aktiv wäre: category='work' ohne 'work' im tag-Set -> 422."""
    response = client.post(
        "/notes",
        json=_valid_payload(category="work", tags=["urgent", "meeting"]),
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Task 4: NoteUpdate (PATCH) — gleiche Constraints, aber Optional
# ---------------------------------------------------------------------------

def test_patch_with_empty_body_succeeds(clean_notes):
    """PATCH mit {} ändert nichts -> 200."""
    created = client.post("/notes", json=_valid_payload()).json()
    response = client.patch(f"/notes/{created['id']}", json={})
    assert response.status_code == 200


def test_patch_with_invalid_title_fails(clean_notes):
    """PATCH mit title='' verstößt gegen min_length=3 -> 422."""
    created = client.post("/notes", json=_valid_payload()).json()
    response = client.patch(f"/notes/{created['id']}", json={"title": ""})
    assert response.status_code == 422


def test_patch_with_unknown_category_fails(clean_notes):
    """PATCH mit unbekannter Kategorie -> 422 (Whitelist greift auch bei Update)."""
    created = client.post("/notes", json=_valid_payload()).json()
    response = client.patch(
        f"/notes/{created['id']}", json={"category": "banana"}
    )
    assert response.status_code == 422
