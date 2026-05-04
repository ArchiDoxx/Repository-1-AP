# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Lernprojekt des Kurses "Applied Programming" (HS Coburg). Jeder Kurstag ist eine eigenständige Übung rund um FastAPI.

## Befehle

**Abhängigkeiten installieren:**
```bash
uv sync
```

**Server starten (main.py):**
```bash
uv run fastapi dev main.py
```

**Server starten (anderes Modul):**
```bash
uv run fastapi dev day_04_main.py
```

**Tests ausführen:**
```bash
uv run pytest day_04_tests.py -v
```

**Einzelnen Test ausführen:**
```bash
uv run pytest day_04_tests.py::test_read_root -v
```

Die API-Dokumentation ist nach dem Start unter `http://localhost:8000/docs` erreichbar.

## Architektur

### Dateistruktur pro Kurstag

Jeder Tag bringt eine neue `day_0X_main.py` plus eine zugehörige `day_0X_tests.py` (alles Kleinbuchstaben). Die zentrale `main.py` enthält den aktuell fertigen Stand der Note-API.

### Note-API (`main.py`)

Die Note-API speichert Daten als JSON-Datei (`data/notes.json`) ohne Datenbank. Das Muster ist:

1. `load_notes()` — liest die JSON-Datei und gibt `(notes_db, next_id)` zurück
2. Verarbeitung im Endpoint
3. `save_notes(notes_db)` — schreibt die aktualisierte Liste zurück

**Wichtig bei der Route-Reihenfolge:** `/notes/stats` muss **vor** `/notes/{note_id}` definiert sein, da FastAPI Routen von oben nach unten prüft und `stats` sonst als `note_id` interpretiert wird.

### Pydantic-Modelle

- `NoteCreate` — alle Felder Pflicht (für POST)
- `NoteUpdate` — alle Felder `Optional` (für PATCH)
- `Note` — vollständiges Objekt inkl. `id` und `created_at`

### Testansatz (Tag 4)

Zwei Testvarianten nebeneinander:
- `day_04_tests.py` — pytest mit `fastapi.testclient.TestClient` (kein laufender Server nötig); verwendet `Faker` für zufällige Testdaten
- `API-tests.py` — manuelle Integrationstests mit `requests` gegen laufenden Server (`http://localhost:8000`)

`TestClient` importiert die `app`-Instanz direkt aus `day_04_main.py` und simuliert HTTP-Requests im selben Prozess.
