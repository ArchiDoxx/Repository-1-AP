# Day 3 Homework – Note API v2.0

## Status

| Task | Beschreibung | Status |
|------|-------------|--------|
| Task 1 | Combined Filters (category + search + tag) | ✅ |
| Task 2 | Statistics Endpoint `/notes/stats` | ✅ |
| Task 3 | Categories Resource `/categories` | ✅ |
| Task 4 | PATCH Endpoint (Partial Update) | ✅ |
| Task 5 | Date-Based Filtering | ✅ |
| Task 6 | Database Migration (SQLModel + SQLite) | ⬜ |

---

## Task 1: Combined Filters

**Ziel:** `GET /notes` unterstützt `category`, `search` und `tag` gleichzeitig.

**Testfälle:**
- `/notes?category=work&tag=urgent`
- `/notes?search=meeting&category=work`
- `/notes?category=personal&tag=family&search=vacation`

---

## ✅ Task 2: Statistics Endpoint

**Ziel:** `GET /notes/stats` gibt eine Zusammenfassung aller Noten zurück.

### Was wurde implementiert

```python
@app.get("/notes/stats")
def get_note_stats():
    from collections import Counter

    notes_db, _ = load_notes()

    by_category = {}
    tag_counter = Counter()

    for note in notes_db:
        by_category[note.category] = by_category.get(note.category, 0) + 1
        for tag in note.tags:
            tag_counter[tag] += 1

    top_tags = [{"tag": tag, "count": count} for tag, count in tag_counter.most_common(5)]

    return {
        "total_notes": len(notes_db),
        "by_category": by_category,
        "top_tags": top_tags,
        "unique_tags_count": len(tag_counter),
    }
```

### Warum so und nicht anders — Step by Step

**Step 1 — Route-Reihenfolge beachten:**
`/notes/stats` muss **vor** `/notes/{note_id}` definiert sein. FastAPI prüft Routen von oben nach unten. Käme `/notes/{note_id}` zuerst, würde FastAPI `stats` als `note_id` interpretieren und einen 422-Validierungsfehler zurückgeben (weil `stats` keine Ganzzahl ist).

**Step 2 — Alle Noten laden:**
`load_notes()` gibt die aktuelle Liste aus der JSON-Datei zurück. Von dort werden alle Statistiken berechnet.

**Step 3 — Kategorien zählen mit einem dict:**
`by_category.get(note.category, 0) + 1` liest den aktuellen Zähler für die Kategorie (oder 0, wenn sie noch nicht existiert) und erhöht ihn um 1. Ergebnis: `{"work": 3, "personal": 2}`.

**Step 4 — Tags zählen mit `collections.Counter`:**
`Counter` ist ein spezialisiertes dict, das automatisch Häufigkeiten zählt. `tag_counter[tag] += 1` reicht aus — kein Initialisieren nötig. `most_common(5)` liefert direkt die 5 häufigsten Tags sortiert nach Anzahl.

**Step 5 — Antwort zusammenstellen:**
- `total_notes`: einfach die Länge der Liste
- `by_category`: das aufgebaute dict
- `top_tags`: Liste aus `most_common(5)`, umgewandelt in `{"tag": ..., "count": ...}`-Objekte
- `unique_tags_count`: `len(tag_counter)` — Counter hat so viele Einträge wie es einzigartige Tags gibt

### Erwartetes Output
```json
{
  "total_notes": 3,
  "by_category": { "work": 2, "personal": 1 },
  "top_tags": [
    {"tag": "urgent", "count": 2},
    {"tag": "meeting", "count": 1}
  ],
  "unique_tags_count": 2
}
```

---

## ✅ Task 3: Categories Resource

**Ziel:** Eigene Ressource `/categories` — analog zu `/tags`.

### Was wurde implementiert

```python
@app.get("/categories")
def list_categories() -> list[str]:
    notes_db, _ = load_notes()
    return sorted({note.category for note in notes_db})


@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str) -> list[Note]:
    notes_db, _ = load_notes()
    return [note for note in notes_db if note.category == category_name]
```

### Warum so und nicht anders — Step by Step

**Step 1 — Set für Einzigartigkeit:**
`{note.category for note in notes_db}` ist eine Set-Comprehension. Ein `set` speichert automatisch nur einzigartige Werte — Duplikate werden ignoriert. Dann `sorted(...)` für alphabetische Reihenfolge.

**Step 2 — `/categories` gibt alle Kategorien zurück:**
Gleiche Idee wie `/tags`: eine Ressource, die einem Client zeigt, welche Kategorien existieren, ohne alle Noten laden zu müssen.

**Step 3 — `/categories/{category_name}/notes` filtert nach Kategorie:**
List-Comprehension: `[note for note in notes_db if note.category == category_name]`. Einfach, direkt, kein `continue`-Muster nötig da keine weiteren Filter kombiniert werden.

**Step 4 — REST-Muster eingehalten:**
```
/categories                    → Collection aller Kategorien
/categories/{name}/notes       → Sub-Collection: Noten einer Kategorie
```
Das spiegelt exakt das Muster von `/tags` und `/tags/{name}/notes` — konsistentes API-Design.

### Testfälle
- `GET /categories` → `["personal", "school", "work"]`
- `GET /categories/work/notes` → alle Noten mit `category: "work"`
- `GET /categories/personal/notes` → alle Noten mit `category: "personal"`

---

## ✅ Task 4: PATCH Endpoint (Partial Update)

**Ziel:** Nur die mitgegebenen Felder einer Note aktualisieren — im Gegensatz zu PUT, das alle Felder ersetzen muss.

### Was wurde implementiert

```python
class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None

@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate) -> Note:
    notes_db, _ = load_notes()

    for i, note in enumerate(notes_db):
        if note.id == note_id:
            updated = Note(
                id=note.id,
                title=note_update.title if note_update.title is not None else note.title,
                content=note_update.content if note_update.content is not None else note.content,
                category=note_update.category if note_update.category is not None else note.category,
                tags=note_update.tags if note_update.tags is not None else note.tags,
                created_at=note.created_at,
            )
            notes_db[i] = updated
            save_notes(notes_db)
            return updated

    raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
```

### Warum so — Step by Step

**Step 1 — Neues Model `NoteUpdate` mit `Optional`:**
Alle Felder sind `Optional[str] = None`. Das bedeutet: der Client muss nicht alle Felder schicken. Fehlt ein Feld im Request-Body, ist sein Wert `None`. Das ist der zentrale Unterschied zu `NoteCreate`, wo alle Felder Pflicht sind.

**Step 2 — `from typing import Optional`:**
`Optional[str]` ist die Python-Schreibweise für "entweder ein String oder `None`". Muss explizit importiert werden.

**Step 3 — Feld-für-Feld prüfen mit `is not None`:**
`note_update.title if note_update.title is not None else note.title` — hat der Client einen neuen Wert gesendet, wird er übernommen, sonst bleibt der alte. Wichtig: `is not None` statt `if note_update.title`, weil ein leerer String `""` auch ein gültiger neuer Wert wäre und bei `if ""` fälschlich ignoriert würde.

**Step 4 — `id` und `created_at` nie verändern:**
Genauso wie bei PUT — die ID identifiziert die Ressource, der Timestamp bleibt der ursprüngliche Erstellungszeitpunkt.

**Step 5 — PUT vs PATCH im Vergleich:**

| | PUT | PATCH |
|---|---|---|
| Alle Felder nötig | Ja | Nein |
| Nicht gesendete Felder | werden überschrieben | bleiben unverändert |
| Use Case | Komplett ersetzen | Einzelne Felder ändern |

### Testfälle
```
PATCH /notes/1  Body: {"title": "Neuer Titel"}
→ Nur der Titel ändert sich, content/category/tags bleiben unverändert

PATCH /notes/1  Body: {"tags": ["updated"]}
→ Nur die Tags ändern sich
```

---

## ✅ Task 5: Date-Based Filtering

**Ziel:** `GET /notes` kann zusätzlich nach Erstellungsdatum gefiltert werden.

### Was wurde implementiert

In `list_notes()` wurden zwei neue optionale Parameter und zwei `continue`-Blöcke ergänzt:

```python
@app.get("/notes")
def list_notes(
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: str = None,
    created_before: str = None,
) -> list[Note]:
    ...
    if created_after and note.created_at < created_after:
        continue

    if created_before and note.created_at > created_before:
        continue
```

### Warum so — Step by Step

**Step 1 — Parameter als `str`, nicht als `datetime`:**
Die Datumsfilter werden als einfache Strings entgegengenommen (z.B. `"2026-04-01"`). Kein Parsing zu einem `datetime`-Objekt nötig — das funktioniert wegen Step 2.

**Step 2 — ISO-Strings sind direkt vergleichbar:**
Das ISO-8601-Format (`"2026-04-28T10:30:00"`) ist so aufgebaut, dass alphabetische String-Sortierung identisch mit chronologischer Sortierung ist. `"2026-04-28" < "2026-04-29"` ergibt `True` — Python vergleicht Zeichen von links nach rechts, und das Jahr steht immer zuerst. Kein datetime-Parsing nötig.

**Step 3 — `continue`-Muster wie alle anderen Filter:**
`if created_after and note.created_at < created_after: continue` — Note wird übersprungen wenn sie vor dem Startdatum erstellt wurde. Alle fünf Filter arbeiten nach demselben Muster: nur Noten die alle Checks bestehen landen in `filtered`.

**Step 4 — Kombination mit anderen Filtern automatisch:**
Die Datumsfilter sind einfach weitere `continue`-Blöcke in der bestehenden Schleife — die Kombination mit `category`, `search` und `tag` funktioniert ohne zusätzlichen Code.

### Testfälle
```
GET /notes?created_after=2026-04-01
GET /notes?created_before=2026-04-30
GET /notes?created_after=2026-04-01&created_before=2026-04-30
GET /notes?category=work&created_after=2026-04-01
```
