# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Lernprojekt des Kurses "Applied Programming" (HS Coburg). Alle Endpoints aus den Kurstagen sind in einer einzigen FastAPI-App (`main.py`) zusammengeführt; alle Tests liegen unter `tests/`.

## Befehle

**Abhängigkeiten installieren:**
```bash
uv sync
```

**Server starten:**
```bash
uv run fastapi dev main.py
```

**Tests ausführen:**
```bash
uv run pytest -v
```

**Einzelnen Test ausführen:**
```bash
uv run pytest test_main.py::test_read_root -v
```

Die API-Dokumentation ist nach dem Start unter `http://localhost:8000/docs` erreichbar.

## Dateistruktur

```
Repository-1-AP/
├── main.py                   # Komplette FastAPI-App (alle Tage, aufsteigend sortiert)
├── test_main.py              # Pytest-Suite für alle Endpoints (Day 2 → 3 → 4 + Integration-Tests)
├── data/                     # JSON-Datenspeicher (z. B. notes.json)
├── day-03-homework.md        # Begleitdokumentation Hausaufgabe
├── day-04-presentation.md    # Präsentation Tag 4
├── work-log-template.md      # Vorlage Arbeitsprotokoll
├── class_based_decorator.py  # Lernartefakt
├── pyproject.toml
├── uv.lock
├── .venv/                    # Virtuelle Umgebung (nicht einchecken)
└── __pycache__/              # Python Bytecode-Cache (nicht einchecken)
```

## Architektur

`main.py` enthält drei Endpoint-Gruppen auf einer einzigen `app`-Instanz, sortiert nach Kurstag:

1. **Day 2 — Notes API:** `POST/GET /notes`, `GET /notes/stats`, `GET /notes/{id}`, `PUT/PATCH/DELETE /notes/{id}`, `GET /categories`, `GET /categories/{name}/notes`
2. **Day 3 — Query Parameters:** `GET /queryparameters`
3. **Day 4 — Greetings:** `GET /`, `GET /greetings/{name}`, `GET /is-adult/{age}`

### Notes API

Speichert Daten als JSON-Datei (`data/notes.json`) ohne Datenbank. Muster:

1. `load_notes()` — liest die JSON-Datei und gibt `(notes_db, next_id)` zurück
2. Verarbeitung im Endpoint
3. `save_notes(notes_db)` — schreibt die aktualisierte Liste zurück

**Wichtig bei der Route-Reihenfolge:** `/notes/stats` muss **vor** `/notes/{note_id}` definiert sein, da FastAPI Routen von oben nach unten prüft und `stats` sonst als `note_id` interpretiert wird.

### Pydantic-Modelle

- `GreetingResponse` — Hello-World-Response
- `NoteCreate` — alle Felder Pflicht (für POST)
- `NoteUpdate` — alle Felder `Optional` (für PATCH)
- `Note` — vollständiges Objekt inkl. `id` und `created_at`

### Tests (`test_main.py`)

Eine einzige Test-Datei mit aufsteigender Tag-Sortierung:

1. **Day 2** – Notes API (CRUD, Filtering, Errors, stats/categories/PATCH)
2. **Day 3** – Query Parameters
3. **Day 4** – Greeting Endpoints
4. **Integration tests via requests** (am Ende) – brauchen einen laufenden Server unter `http://127.0.0.1:8000`, sonst `ConnectionError`

Die Day-2/3/4-Tests verwenden `fastapi.testclient.TestClient` gegen die `app`-Instanz und brauchen keinen Server.

- `Faker` für zufällige Testdaten
- `monkeypatch` + `tmp_path` Fixture (`clean_notes`), um `NOTES_FILE` auf eine temporäre Datei umzuleiten
