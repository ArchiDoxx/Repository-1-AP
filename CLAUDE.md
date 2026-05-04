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

## Dateistruktur & Namenskonventionen

```
Repository-1-AP/
├── main.py               # Wachsende Haupt-API (aktuell: Notes-API aus Tag 2)
├── main_tag_3.py         # Älteres Format: Tag 3 (Query Parameters)
├── day_04_main.py        # Neues Format: Tag 4 Hauptmodul
├── day_04_tests.py       # Neues Format: Tag 4 Tests
├── API-tests.py          # Manuelle Integrationstests gegen laufenden Server
├── day-03-homework.py    # Hausaufgaben (Bindestrich-Format)
├── day-03-homework.md    # Begleitdokumentation zu den Hausaufgaben
├── day-04-presentation.md
├── data/                 # JSON-Datenspeicher (z. B. notes.json)
├── .venv/                # Virtuelle Umgebung (nicht einchecken)
└── __pycache__/          # Python Bytecode-Cache (nicht einchecken)
```

### Namensregeln

| Dateityp | Schema | Beispiel |
|----------|--------|---------|
| Kurstag-Hauptmodul (neu) | `day_XX_main.py` | `day_04_main.py` |
| Kurstag-Tests (neu) | `day_XX_tests.py` | `day_04_tests.py` |
| Kurstag-Hauptmodul (alt) | `main_tag_X.py` | `main_tag_3.py` |
| Hausaufgaben Python | `day-XX-homework.py` | `day-03-homework.py` |
| Markdown-Dokumente | `day-XX-<thema>.md` | `day-04-presentation.md` |

**Regel:** Python-Module mit Unterstrich (`_`), Markdown- und Homework-Dateien mit Bindestrich (`-`).
Neue Kurstage folgen dem Format `day_XX_main.py` / `day_XX_tests.py`.

## Architektur

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

### Tag 4 — Testing (`day_04_main.py` + `day_04_tests.py`)

**Thema:** Testen von FastAPI-Endpunkten mit pytest und TestClient.

`day_04_main.py` enthält drei Endpunkte:
- `GET /` — gibt `{"message": "Hello World!"}` zurück
- `GET /greetings/{name}` — personalisierter Gruß
- `GET /is-adult/{age}` — prüft Volljährigkeit, gibt `age`, `is_adult`, `can_vote`, `can_drive` zurück

`day_04_tests.py` testet **drei Apps gleichzeitig**:
- `day_04_main.app` — Tag-4-Endpunkte
- `main.app` (als `notes_app`) — Notes-API
- `main_tag_3.app` (als `query_app`) — Query-Parameter-Endpunkt aus Tag 3

Zwei Testvarianten nebeneinander:
- `day_04_tests.py` — pytest mit `fastapi.testclient.TestClient` (kein laufender Server nötig); verwendet `Faker` für zufällige Testdaten; nutzt `monkeypatch` + `tmp_path` Fixture, um `NOTES_FILE` auf eine temporäre Datei umzuleiten
- `API-tests.py` — manuelle Integrationstests mit `requests` gegen laufenden Server (`http://localhost:8000`)

`TestClient` importiert die `app`-Instanz direkt und simuliert HTTP-Requests im selben Prozess.
