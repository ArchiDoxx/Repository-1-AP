# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Lernprojekt des Kurses "Applied Programming" (HS Coburg). Eine einzige FastAPI-App (`main.py`) mit allen Kurstag-Endpoints, eine Streamlit-Oberfläche (`frontend.py`) und zwei Test-Dateien im Repo-Root.

## Befehle

```bash
uv sync                              # Abhängigkeiten installieren
uv run fastapi dev main.py           # Backend starten (http://127.0.0.1:8000, Docs unter /docs)
uv run streamlit run frontend.py     # Streamlit-Frontend starten (http://localhost:8501)
uv run pytest -v                     # Alle Tests
uv run pytest test_main.py -v        # Nur die TestClient-Suite (kein Server nötig)
uv run pytest test_main.py::test_read_root -v   # Einzelner Test
```

`test_suit.py` und die Integrations-Tests am Ende von `test_main.py` schicken echte `requests` an `http://127.0.0.1:8000` und **überspringen** sich automatisch, wenn der Server nicht läuft. Für vollständige Testabdeckung daher `uv run fastapi dev main.py` parallel starten.

## Architektur

### Backend (`main.py`)
Eine einzige `app`-Instanz, drei Endpoint-Gruppen aufsteigend nach Kurstag sortiert:

1. **Day 2 — Notes API** mit SQLite-Persistenz: `POST/GET /notes`, `GET /notes/stats`, `GET /notes/{id}`, `PUT/PATCH/DELETE /notes/{id}`, `GET /categories`, `GET /categories/{name}/notes`, `GET /tags`, `GET /tags/{name}/notes`
2. **Day 3 — Query Parameters:** `GET /queryparameters`
3. **Day 4 — Greetings:** `GET /`, `GET /greetings/{name}`, `GET /is-adult/{age}`

### Persistenz (SQLModel + SQLite)
- DB-Datei: `notes.db` im Repo-Root (committed).
- Engine + `SQLModel.metadata.create_all(engine)` werden beim Modul-Import angelegt.
- Pro Request: `SessionDep = Annotated[Session, Depends(get_session)]` (FastAPI Dependency Injection statt manueller load/save-Helfer).
- Tags werden in SQLite als CSV-String gespeichert (kein Array-Typ); Konvertierung über `_tags_to_csv` / `_tags_to_list`, API liefert immer `list[str]`.

### Pydantic-Modelle
- `NoteCreate` — alle Felder Pflicht (POST **und** PUT verwenden dasselbe Modell)
- `NoteUpdate` — alle Felder `Optional` (PATCH)
- `Note(SQLModel, table=True)` — DB-Tabelle mit `tags: str` (CSV)
- Tag-Validierung (`_normalize_tags`): trim + lowercase + dedupe, ≥2 Zeichen, max. 10 Tags

### Route-Reihenfolge (CRITICAL)
`/notes/stats` muss **vor** `/notes/{note_id}` definiert sein, sonst matcht `stats` als `note_id` und liefert 422.

### Frontend (`frontend.py`)
Streamlit-App mit zwei Bereichen:
1. Demo-Buttons gegen die öffentliche `https://naas.isalman.dev/no` API (Session-State-Pattern für mehrere unabhängige Texte).
2. Notizen-UI gegen das lokale Backend `http://127.0.0.1:8000`: Button "Alle Notizen anzeigen" lädt `GET /notes`, Button "Neue Notiz erstellen" blendet ein `st.form` ein, das per `POST /notes` speichert. Erfolg/Fehler über `st.success` / `st.error`; bei nicht erreichbarem Backend wird `ConnectionError` abgefangen und als Hinweis "Backend nicht erreichbar" angezeigt.

### Tests
- `test_main.py` — primäre Suite, nutzt `fastapi.testclient.TestClient` direkt gegen `app`, plus Faker für Testdaten. Eine `clean_notes`-Fixture leitet die DB auf eine temporäre Datei um (per `monkeypatch` + `tmp_path`), damit Tests die echte `notes.db` nicht verändern. Integrations-Tests am Ende verwenden `requests` gegen einen laufenden Server (auto-skip).
- `test_suit.py` — separate Tag-3-Referenz-Suite, **ausschließlich** mit `requests` gegen einen laufenden Server; bei `ConnectionError` skippt die ganze Datei via `_require_server`-Fixture.

### Lernartefakt
`class_based_decorator.py` — eigenständige Demo-Datei mit klassenbasiertem Caching/Call-Counting-Decorator (nicht von der App importiert).

## Dateistruktur (Ist-Zustand)

```
Repository-1-AP/
├── main.py                   # Komplette FastAPI-App (SQLModel + SQLite)
├── frontend.py               # Streamlit-Frontend
├── test_main.py              # TestClient-Suite + Integrations-Tests
├── test_suit.py              # requests-basierte Tag-3-Suite (braucht laufenden Server)
├── class_based_decorator.py  # Decorator-Lernartefakt
├── notes.db                  # SQLite-Datenbank (committed)
├── data/                     # Alt-Verzeichnis (Vorgänger-JSON-Storage)
├── README.md                 # Generisches Setup (veraltet — diese Datei ist Source of Truth)
├── work-log-template.md
├── pyproject.toml            # Deps: fastapi[standard], sqlmodel, streamlit, requests, faker, pytest
└── uv.lock
```

> Hinweis: `README.md` enthält ein generisches Layered-Architecture-Template, das **nicht** dem aktuellen Code entspricht. Diese `CLAUDE.md` ist die maßgebliche Architektur-Beschreibung.
