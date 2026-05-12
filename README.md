# Applied Programming FastAPI Lernprojekt (HS Coburg)

Dieses Repository ist das Lernprojekt zum Kurs "Applied Programming" der Hochschule Coburg. Sämtliche Endpoints aus den Kurstagen sind in **einer einzigen FastAPI-App** (`main.py`) gebündelt. Zum Testen dienen umfangreiche Pytest-Tests—eine Datenbank wird **nicht** verwendet, sondern eine JSON-Datei unter `data/`.

---

## 🛠️ Setup & Entwicklung

**Abhängigkeiten installieren**
```bash
uv sync
```

**Server starten**
```bash
uv run fastapi dev main.py
```

**Alle Tests ausführen**
```bash
uv run pytest -v
```

**Einzelnen Test ausführen**
```bash
uv run pytest test_main.py::test_read_root -v
```

Nach dem Start ist die Swagger-Dokumentation unter [`http://localhost:8000/docs`](http://localhost:8000/docs) erreichbar.

---

## 📁 Projektstruktur

```
Repository-1-AP/
├── main.py                   # Komplette FastAPI-App (alle Kurstage integriert)
├── test_main.py              # Pytest-Suite (Day 2–4, Integration)
├── data/
│   └── notes.json            # Persistenz für Notes API
├── day-03-homework.md        # Hausaufgabenbeschreibung Tag 3
├── day-04-presentation.md    # Präsentationsfolien Tag 4
├── class_based_decorator.py  # Lernartefakt
├── pyproject.toml            # Abhängigkeits- und Builddatei (POETRY)
├── uv.lock                   # Lockfile zu pyproject.toml
└── .venv/                    # Virtuelle Umgebung (nicht einchecken)
```

---

## 🏛️ Architektur

1. **Day 2 – Notes API**
   - Endpunkte: `POST/GET /notes`, `GET /notes/stats`, `GET /notes/{id}`, `PUT/PATCH/DELETE /notes/{id}`, `GET /categories`, `GET /categories/{name}/notes`
   - Persistenz über `data/notes.json`
   - Wichtig: Endpoint `/notes/stats` **vor** `/notes/{id}` definieren, da FastAPI Top-Down matched!

2. **Day 3 – Query Parameter**
   - Endpunkt: `GET /queryparameters`

3. **Day 4 – Greetings & Validation**
   - Endpunkte: `GET /`, `GET /greetings/{name}`, `GET /is-adult/{age}`

**Pydantic-Modelle**
- `GreetingResponse` — Responsemodell für Begrüßungen
- `NoteCreate` — für POST, Pflichtfelder
- `NoteUpdate` — für PATCH, alle Felder optional
- `Note` — vollständiges Notizobjekt inkl. id und Timestamp

---

## 🧪 Testen

- Alle Tests liegen in **einer** Datei: `test_main.py`
- Day-2/3/4-Tests nutzen intern `TestClient` gegen die FastAPI-App (kein laufender Server nötig)
- Integrationstests am Dateiende prüfen gegen laufenden Server unter `http://127.0.0.1:8000`
- Tools/Fixtures: Faker, monkeypatch, `tmp_path` zur Isolation/Persistenz (siehe `clean_notes` Fixture)
- Pytest-Ausführung siehe oben.

---

## 📚 API Beispiele

- **Alle Notizen holen**
    ```http
    GET /notes
    ```
- **Neue Notiz erstellen**
    ```http
    POST /notes
    Content-Type: application/json
    {
      "title": "Neuer Eintrag",
      "content": "Dies ist eine Notiz.",
      "category": "Allgemein"
    }
    ```
- **Statistiken anzeigen**
    ```http
    GET /notes/stats
    ```

Weitere Beispiele und alle Endpunkte sind über die Swagger-Oberfläche (`/docs`) einsehbar.

---

## ℹ️ Hinweise

- Es wird **keine** relationale DB verwendet; alle Daten sind JSON-basiert.
- Die gesamte App ist in **einer Datei** implementiert für maximale Übersicht.
- Kursdokumente und Präsentationen sind im Repo enthalten.
Kursdokumente und Präsentationen sind im Repo enthalten.App ist in **einer Datei** implementiert für maximale Übersicht.
- Kursdokumente und Präsentationen sind im Repo enthalten.
