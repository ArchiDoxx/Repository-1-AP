# Work Log

**Student Name:** Luce Buum

Instructions: Fill out one log for each course day. Content to consider: Course Sessions + Assignment

---

## Week 1

### Day 1

#### 1. ✅ What did I accomplish?

An Tag 1 ging es um das komplette Setup der Entwicklungsumgebung und den Bau einer ersten lauffähigen FastAPI-Anwendung. Konkret habe ich Git, VS Code (inkl. Python-Extension) und uv als Python-Paketmanager installiert und über `git --version` bzw. `uv --version` verifiziert. Anschließend habe ich mit `uv add fastapi` ein neues Projekt aufgesetzt und in einer `main.py` eine FastAPI-Instanz erzeugt sowie die drei Endpoints `/`, `/status` und `/about` implementiert. Den Server habe ich mit `uv run fastapi dev` gestartet und alle Endpoints über die automatisch generierte Swagger-Doku unter `/docs` getestet. Damit habe ich zum ersten Mal das Grundprinzip "Decorator + Funktion + Dict-Return" von FastAPI verstanden und gesehen, wie Python-Dictionaries automatisch in JSON umgewandelt werden. Als Hausaufgabe kamen die Endpoints `/square/{number}`, `/student` und `/double/{number}` dazu, wodurch ich erstmals mit Path-Parametern und automatischer Typkonvertierung (`int`) gearbeitet habe.

---

#### 2. 🚧 What challenges did I face?

Die größte Hürde lag tatsächlich nicht im Programmieren, sondern im Setup unter Windows. Bei der Installation von `uv` über das PowerShell-Skript bin ich zunächst an der ExecutionPolicy hängengeblieben — der Befehl wurde abgelehnt, weil das Ausführen entfernter Skripte standardmäßig blockiert ist. Ein zweites Problem war das Verständnis, was ein "virtuelles Environment" überhaupt ist; mir war anfangs unklar, warum `uv add fastapi` funktioniert, ein direktes `pip install` aber nicht das gleiche Ergebnis bringt. Beim ersten Start des Servers kam außerdem die Fehlermeldung, dass Port 8000 bereits belegt sei, weil ich aus einer früheren Session noch einen Prozess offen hatte. Inhaltlich war für mich die Decorator-Syntax `@app.get("/")` zunächst irritierend — ich konnte den `@`-Operator noch nicht einordnen und habe nicht verstanden, warum die Funktion direkt darunter ohne expliziten Aufruf "wirkt".

---

#### 3. 💡 How did I overcome them?

Das ExecutionPolicy-Problem aus Punkt 2 habe ich gelöst, indem ich den Befehl exakt mit dem Parameter `-ExecutionPolicy ByPass` aus der Folie übernommen habe — dadurch wird die Policy nur für diesen einen Aufruf umgangen, ohne systemweit etwas zu ändern. Den Sinn des virtuellen Environments habe ich verstanden, nachdem ich gesehen habe, dass `uv` automatisch eine `.venv` im Projektordner anlegt: dadurch wurde greifbar, dass die Pakete projektspezifisch isoliert werden und das System-Python sauber bleibt. Den belegten Port habe ich mit dem Task-Manager erledigt, indem ich den hängenden Python-Prozess beendet habe. Das Decorator-Verständnis ist mir spätestens dann gekommen, als ich gemerkt habe, dass `@app.get("/")` einfach die darunterstehende Funktion bei FastAPI als Handler für GET-Requests auf `/` registriert — die `/docs`-Seite hat das eindrucksvoll bestätigt, weil neue Endpoints sofort dort auftauchen. Offen geblieben ist die Frage, wie man Decorators selbst schreibt, was laut Vorlesungsplan an Tag 6 behandelt wird.

---

### Day 2

#### 1. ✅ What did I accomplish?

An Tag 2 habe ich die Python-Grundlagen aufgefrischt (Variablen, Datentypen `str/int/float/bool/list/dict`, F-Strings, Funktionen mit Type Hints) und parallel eine vollständige Note-Taking-API gebaut. Konkret habe ich in einem neuen Projekt `note-api` mit `uv init` und `uv add fastapi[standard]` zwei Pydantic-Modelle definiert: `NoteCreate` (Eingabe ohne ID) und `Note` (Ausgabe mit `id` und `created_at`). Implementiert wurden die Endpoints `POST /notes` (mit Status 201), `GET /notes` und `GET /notes/{note_id}` (inklusive 404-Behandlung über `HTTPException`). Der wichtigste Schritt war die File-Persistenz: ich habe die Funktionen `load_notes()` und `save_notes()` geschrieben, die JSON in `data/notes.json` schreiben und beim Start zurücklesen, inklusive Fortführung des `note_id_counter` über `max(...)+1`. Außerdem habe ich eine `.gitignore` aus dem GitHub-Python-Template hinzugefügt. Als Hausaufgabe kamen ein `category`-Feld, ein Filter-Endpoint `/notes/category/{category}` und ein Statistik-Endpoint dazu.

---

#### 2. 🚧 What challenges did I face?

Die Persistenz war fehleranfälliger, als sie auf den Folien wirkt. Mein erster Versuch hat `notes_db` als globale Variable geführt und nur beim Start einmal geladen — das hat dazu geführt, dass nach einem Server-Neustart zwar die Daten da waren, aber neu erstellte Notes manchmal mit doppelter ID gespeichert wurden, weil mein Counter nicht sauber synchronisiert war. Beim ersten Schreibversuch ist außerdem ein `FileNotFoundError` geflogen, weil der Ordner `data/` noch nicht existierte. Pydantic hat mir bei `Note(**note)` einen Validation Error geworfen, nachdem ich später das `category`-Feld hinzugefügt hatte — die alte `notes.json` enthielt noch Einträge ohne dieses Feld. Konzeptionell war mir der Unterschied zwischen `NoteCreate` und `Note` zunächst nicht klar; ich dachte, ein Modell würde reichen.

---

#### 3. 💡 How did I overcome them?

Den ID-Konflikt aus Punkt 2 habe ich behoben, indem ich `load_notes()` so umgebaut habe, dass es bei jedem Endpoint-Aufruf sowohl die Liste als auch den nächsten Counter zurückgibt — genau wie auf der Folie "Step 14" gezeigt. Damit ist die einzige Quelle der Wahrheit immer die JSON-Datei, und Race Conditions zwischen RAM und Disk sind ausgeschlossen. Den `FileNotFoundError` habe ich gelöst, indem ich in `save_notes()` den Aufruf `NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)` ergänzt habe — dadurch wird der `data/`-Ordner automatisch angelegt, falls er fehlt. Den Pydantic-Validation-Error nach Schema-Änderung habe ich pragmatisch gelöst, indem ich die alte `notes.json` einmalig gelöscht und neu befüllt habe; in einem Produktivsystem wäre das eine Migration, was mir zum ersten Mal das Thema "Schema-Evolution" bewusst gemacht hat. Den Unterschied zwischen `NoteCreate` und `Note` habe ich verstanden, nachdem ich gesehen habe, dass der Client niemals selbst eine `id` schicken darf — sie wird serverseitig vergeben. Offen ist für mich noch, wie man bei echten DBs solche Migrationen sauber automatisiert.

---

### Day 3

#### 1. ✅ What did I accomplish?

Tag 3 stand ganz im Zeichen von REST-Design und vollständigem CRUD. Ich habe gelernt, dass URLs Substantive (Ressourcen) sein sollen statt Verben (`/courses` statt `/getCourses`) und dass HTTP-Methoden die Aktion ausdrücken. Praktisch habe ich meine Note-API zur Version 2.0 erweitert: das Modell hat ein `tags: list[str]`-Feld bekommen, `GET /notes` unterstützt jetzt die Query-Parameter `category`, `search` und `tag` (auch kombiniert), und ich habe `PUT /notes/{id}` (volle Ersetzung unter Beibehaltung von `id` und `created_at`) sowie `DELETE /notes/{id}` mit Status 204 ergänzt. Zusätzlich habe ich eine eigenständige Tag-Ressource mit `GET /tags` und `GET /tags/{tag_name}/notes` gebaut, was mir das Konzept "Resource Relationships" greifbar gemacht hat. Als Hausaufgabe kam u.a. die große Migration auf SQLite via SQLModel: Definition der Tabellen `Note` und `Tag` mit einer Many-to-Many-Beziehung über eine implizite Link-Tabelle, eine Session-Dependency `SessionDep`, datenbankseitige Filter mit `select`, `where` und `or_`, sowie eine `PATCH`-Route mit `Optional`-Feldern und ein `created_after`/`created_before`-Datumsfilter.

---

#### 2. 🚧 What challenges did I face?

Die Reihenfolge der Routen hat mich richtig viel Zeit gekostet. Mein Endpoint `GET /notes/stats` wurde nie aufgerufen, weil FastAPI die Anfrage an `GET /notes/{note_id}` weitergeleitet hat — `stats` wurde als Wert für `note_id: int` interpretiert und führte zu einem 422-Fehler. Bei der SQLModel-Migration bin ich an der Many-to-Many-Beziehung hängengeblieben: zunächst habe ich die `Relationship`-Felder vergessen und versucht, Tags als String-Liste in einer Spalte zu speichern, was natürlich nicht funktioniert. Außerdem hatte ich einen `DetachedInstanceError`, als ich nach `session.commit()` versucht habe, `note.tags` zu lesen — das Objekt war zu diesem Zeitpunkt nicht mehr an die Session gebunden. Beim PATCH-Endpoint war mir der Unterschied zwischen "Feld nicht gesendet" und "Feld explizit auf `null` gesetzt" nicht klar; meine erste Version hat stillschweigend Felder überschrieben, die der Client gar nicht ändern wollte.

---

#### 3. 💡 How did I overcome them?

Das Routing-Problem aus Punkt 2 habe ich gelöst, indem ich gelernt habe, dass FastAPI Routen in Reihenfolge der Definition matcht: spezifische Pfade wie `/notes/stats` müssen **vor** dynamischen Pfaden wie `/notes/{note_id}` stehen. Nach dem Umsortieren funktionierte alles. Die SQLModel-Beziehung habe ich mit der offiziellen Doku (sqlmodel.tiangolo.com) und dem `Relationship(back_populates=...)`-Pattern aus den Folien gelöst — der Aha-Moment kam, als ich im SQLite-Viewer (VS Code Extension) die automatisch generierte Link-Tabelle `notelink` mit `note_id` und `tag_id` sehen konnte. Den `DetachedInstanceError` habe ich behoben, indem ich nach `session.commit()` immer `session.refresh(db_note)` aufrufe, damit die Relationships nachgeladen werden, bevor ich auf sie zugreife. Beim PATCH habe ich gelernt, mit `note_update.model_dump(exclude_unset=True)` zu arbeiten — so bekomme ich nur die Felder, die der Client tatsächlich gesendet hat, und kann gezielt nur diese setzen. Offen bleibt für mich, wie man echte DB-Migrationen mit Tools wie Alembic macht, wenn sich das Schema ändert.

---

## Week 2

### Day 4

#### 1. ✅ What did I accomplish?

Tag 4 hat zwei Stränge zusammengeführt: zum einen habe ich das POST-Pattern mit Pydantic vertieft (Zwei-Modell-Pattern `CourseCreate`/`Course`, `**course.dict()`-Unpacking, Status 201, Konflikt-Erkennung mit Status 409 bei doppeltem Course-Code), zum anderen den Einstieg in pytest gemacht. Konkret habe ich `pytest` und `requests` über `uv add pytest requests` installiert und beide Test-Ansätze ausprobiert: einmal extern mit echten HTTP-Calls über die `requests`-Library gegen den laufenden `uv run fastapi dev`-Server, und einmal intern mit dem `TestClient` von FastAPI, der die App ohne Netzwerk direkt anspricht. Dabei habe ich das Arrange-Act-Assert-Schema verinnerlicht und Tests für CRUD-Operationen, Filter-Kombinationen, 404-Fehler und 422-Validierungsfehler geschrieben. Die Hausaufgabe verlangte mindestens 15 Tests für die Notes-API: 5x CRUD, 4x Filter, 4x Error-Cases plus Tests für die Day-3-Hausaufgaben (Statistics, PATCH).

---

#### 2. 🚧 What challenges did I face?

Mein größtes Problem war die **Test-Isolation**: meine Tests hingen voneinander ab, weil sie alle in dieselbe `notes.json` bzw. `notes.db` geschrieben haben. Wenn ich `pytest` mehrfach hintereinander laufen ließ, hatte `test_list_notes` plötzlich 47 Notes im Ergebnis statt der erwarteten 1, und `test_create_note` hat manchmal mit 409 Conflict gefehlt, weil der Test-Datensatz schon vom letzten Lauf existierte. Beim ersten Lauf der `requests`-basierten Tests habe ich vergessen, den Server in einem zweiten Terminal zu starten, und bekam `ConnectionError: Failed to establish a new connection`. Bei den 422-Tests habe ich anfangs nur den Status geprüft und nicht die `detail`-Struktur, wodurch echte Bugs (z.B. falsche Feldnamen in der Pydantic-Fehlermeldung) durchgerutscht sind. Außerdem war mir nicht klar, warum mein `test_delete_note` mal mit 200, mal mit 204 zurückkam — je nachdem, ob ich die Day-3-Variante oder die Day-2-Variante des Endpoints am Laufen hatte.

---

#### 3. 💡 How did I overcome them?

Die Test-Isolation aus Punkt 2 habe ich erstmal pragmatisch gelöst, indem ich jeden Test seine Test-Daten mit eindeutigen Titeln (z.B. mit Zeitstempel oder UUID-Suffix) anlegen lasse, sodass keine Konflikte mehr entstehen. Sauberer wäre eine pytest-Fixture, die die DB vor jedem Test leert — laut Vorschau auf Tag 5 sollten genau Fixtures und Cleanup das nächste Thema sein, deshalb habe ich das vertagt. Den `ConnectionError` habe ich gelöst, indem ich bewusst zwei Terminals offen lasse — Terminal 1 für `uv run fastapi dev`, Terminal 2 für `uv run pytest -v` — und langfristig auf den `TestClient` umsteigen werde, der diese Trennung gar nicht mehr braucht. Bei den 422-Tests habe ich gelernt, mit `response.json()["detail"][0]["loc"]` gezielt den Pfad des fehlerhaften Feldes zu prüfen, was die Tests deutlich aussagekräftiger macht. Den 200/204-Konflikt habe ich aufgelöst, indem ich die Endpoint-Definition explizit auf `status_code=204` gesetzt und im Test `assert response.status_code in [200, 204]` verwendet habe, um beide gültigen Varianten zu akzeptieren. Offen bleibt, wie man Tests auch parallelisieren kann, ohne sich gegenseitig auf die Füße zu treten.

---

### Day 5

#### 1. ✅ What did I accomplish?

An Tag 5 ging es um Pydantic-Validierung in der Tiefe — also genau die Werkzeuge, die garantieren, dass schlechte Daten gar nicht erst in den Endpoint gelangen. Ich habe `Field(...)` mit `min_length`, `max_length`, `pattern`, `ge`/`le`, `default_factory=list` und `description`/`examples` (für die Swagger-Doku) eingesetzt. Anschließend habe ich `@field_validator` als `@classmethod` geschrieben, um Felder zu normalisieren (`.strip().lower()`) und zu prüfen, sowie `@model_validator(mode="after")` für eine Cross-Field-Regel: wenn `category == "work"`, muss der Tag `"work"` in der Liste enthalten sein. Über `ConfigDict(str_strip_whitespace=True, extra="forbid")` habe ich modellweit Whitespace gestrippt und unbekannte Felder (Tippfehler wie `tagz`) verboten. Auch der Unterschied zwischen Required, Default und Optional (`str | None = None`) wurde mir klar, ebenso die Built-in-Typen `EmailStr`, `HttpUrl`, `PositiveInt`, `UUID4`. Als Hausaufgabe habe ich `NoteCreate`, `NoteUpdate` und das `Tag`-Modell entsprechend gehärtet und in `test_validation.py` mindestens 8 Tests geschrieben, die prüfen, dass falsche Eingaben mit 422 abgelehnt werden.

---

#### 2. 🚧 What challenges did I face?

Bei `NoteUpdate` für PATCH wurde mir der Unterschied zwischen `Optional[str] = None` und `str | None = Field(default=None, min_length=3)` zunächst nicht klar — meine erste Version hat das `min_length` auch dann geprüft, wenn das Feld gar nicht mitgesendet wurde, sodass ein leeres `PATCH {}` mit 422 fehlgeschlagen ist statt mit 200 durchzulaufen. Beim Tag-Validator hatte ich den klassischen Anfängerfehler, dass ich `value.strip()` geschrieben habe **ohne** `return` — Pydantic hat das stillschweigend ignoriert und die Tags blieben unverändert mit Whitespace. Bei `extra="forbid"` ist mir aufgefallen, dass meine Tests aus Tag 4 plötzlich rot wurden, weil sie zusätzliche Felder (z.B. `created_at` im Request-Body) mitschickten, die jetzt nicht mehr erlaubt sind. Beim `@model_validator` war mir unklar, warum es als `mode="after"` und nicht `mode="before"` deklariert sein muss, und wann genau `self` schon vollständig validiert ist.

---

#### 3. 💡 How did I overcome them?

Das `NoteUpdate`-Problem aus Punkt 2 habe ich gelöst, indem ich verstanden habe, dass Pydantic Validierungen nur dann auf einem Feld ausführt, wenn es überhaupt einen Wert hat — `None` als Default wird nicht gegen `min_length=3` geprüft, **aber** ein explizit gesendetes `""` (leerer String) wird geprüft und schlägt korrekt fehl. Genau das wollte ich. Den Validator-Bug ohne `return` habe ich bemerkt, weil mein Tag-Test `test_create_note_normalizes_tags` rot blieb; nach dem Hinzufügen von `return value.strip().lower()` ging er sofort grün — das hat mir die Folien-Warnung "Always return the value" sehr eindringlich eingebrannt. Die geknackten Tag-4-Tests habe ich behoben, indem ich die nun verbotenen Extra-Felder aus den Request-Bodies entfernt habe; das war eigentlich ein Hinweis, dass die alten Tests zu schlampig waren. Den `@model_validator(mode="after")` habe ich verstanden, nachdem ich bewusst auf `mode="before"` umgestellt habe und gesehen habe, dass `self` dann noch keine sauberen Felder hat — `mode="after"` läuft erst, nachdem alle einzelnen Field-Validatoren durch sind, also ist `self.category` und `self.tags` garantiert valide. Offen ist für mich, wie man bei wirklich komplexen, datenbankabhängigen Regeln (z.B. "category muss in der `categories`-Tabelle existieren") sauber zwischen Pydantic und Endpoint-Code trennt — die Folie sagt klar: alles mit DB-Bezug gehört in den Endpoint, nicht ins Modell.

---

### Day 6

#### 1. ✅ What did I accomplish?

Tag 6 hatte zwei klare Ziele: Decorators selbst zu verstehen und die offizielle Test-Suite gegen meine API laufen zu lassen. Bei den Decorators habe ich eine eigene `class_based_decorator.py` angelegt und einen klassenbasierten Decorator gebaut, der per `__call__` eine Wrapper-Funktion zurückgibt — damit habe ich endlich verstanden, was hinter `@app.get("/")` aus Tag 1 wirklich passiert: ein Decorator nimmt eine Funktion entgegen und gibt eine (meist erweiterte) Funktion zurück. Zur Inspektion habe ich `icecream` (`uv add icecream`) eingesetzt, das mit `ic(value)` automatisch Variablenname und Wert ausgibt — viel angenehmer als `print` zum Debuggen. Im zweiten Teil habe ich die offizielle [`test_main.py`](https://github.com/MartinEnders/Applied-Programming-Course/blob/main/reference-implementation/test_main.py) aus dem Reference-Implementation-Ordner heruntergeladen und gegen meine API laufen lassen. Die Hausaufgabe war, alle Tests grün zu bekommen und gleichzeitig Implementations-Rückstände aus früheren Tagen aufzuholen (Validation, DB-Backend etc.).

---

#### 2. 🚧 What challenges did I face?

Beim ersten Lauf der offiziellen Test-Suite hatte ich rund ein Drittel rote Tests — und das war hart, weil meine eigenen Tests aus Tag 4 alle grün waren. Konkrete Probleme: einige meiner Endpoints haben leicht abweichende Statuscodes geliefert (z.B. 200 statt 204 bei DELETE), die Reihenfolge der JSON-Felder hat zwar nichts ausgemacht, aber meine `tags`-Liste war manchmal nicht alphabetisch sortiert und manchmal nicht deduplicated, was die Test-Suite aber erwartet hat. Außerdem habe ich gemerkt, dass ich die Route `/notes/stats` zwar gebaut hatte, aber das Antwort-Schema (`top_tags` als Liste von `{tag, count}`-Objekten) nicht exakt dem entsprach, was die Suite prüft. Beim Schreiben des eigenen Decorators bin ich erstmal an der Frage gescheitert, warum ein klassenbasierter Decorator `__call__` braucht und ein funktionsbasierter nicht — der Unterschied zwischen Instanz und Aufruf war für mich verwirrend.

---

#### 3. 💡 How did I overcome them?

Die roten Tests aus Punkt 2 habe ich systematisch durchgegangen: für jeden roten Test habe ich erst die Erwartung im Test-Code gelesen (was wird genau assertet?), dann meinen Endpoint angepasst, bis Erwartung und Implementierung deckungsgleich waren. Beim DELETE-Endpoint habe ich auf `status_code=204` umgestellt und ein leeres Return verwendet, beim `tags`-Feld habe ich im Pydantic-Validator (Erkenntnis von Tag 5!) sortiert und dedupliziert, und beim `/notes/stats`-Endpoint habe ich `collections.Counter` benutzt — wie in der Tag-3-Folie als Hint angegeben — um die Top-5-Tags als korrekt strukturierte Dict-Liste zurückzugeben. Den klassenbasierten Decorator habe ich verstanden, nachdem ich `ic()` in jeden Schritt eingebaut habe: `ic(self)` beim `__init__`, `ic(args, kwargs)` beim `__call__` — dadurch wurde sichtbar, dass `MyDecorator(func)` zuerst eine Instanz erzeugt (das ist der `@MyDecorator`-Schritt) und der Aufruf der dekorierten Funktion dann `__call__(self, *args, **kwargs)` triggert. Offen bleibt für mich, wann man klassenbasierte Decorators wirklich braucht — die meisten Real-World-Beispiele, die ich gesehen habe, sind funktionsbasiert mit `functools.wraps`.

---

## Week 3

### Day 7

#### 1. ✅ What did I accomplish?

Tag 7 war der Sprung vom Backend ins Frontend: Streamlit. Nach `uv add streamlit` habe ich zuerst die "Hello, World!"-App gebaut und gestartet, danach die "Say no"-App umgesetzt — ein Button, der bei Klick einen `requests.get`-Call gegen `https://naas.isalman.dev/no` schickt und das Feld `reason` aus der JSON-Antwort anzeigt. Dabei habe ich die zentralen Streamlit-Konzepte kennengelernt: `st.text_input` für Eingaben, `st.button` für Aktionen, `st.write` für Ausgaben und vor allem `st.session_state` für persistenten Zustand zwischen Reruns (Streamlit führt das Skript bei jeder Interaktion komplett neu aus, weshalb normale Variablen den Zustand verlieren). Im `with st.expander('session state')`-Block konnte ich live sehen, wie sich der State entwickelt. Die Hausaufgabe ist ein Streamlit-Frontend für meine Notes-API mit zwei Funktionen: (1) alle Notes auflisten mit klickbarem Detail-View für Titel/Content/Tags/Category und (2) ein Formular per `st.form` zum Anlegen neuer Notes (Titel, Content, Tags, Category), die nach dem Submit sofort in der Liste auftauchen.

---

#### 2. 🚧 What challenges did I face?

Das Streamlit-Ausführungsmodell hat mich zunächst komplett überrascht. Mein erster Versuch hat eine Variable `notes = []` außerhalb von `session_state` definiert und nach jedem Button-Klick frisch gefüllt — das funktionierte nicht reproduzierbar, weil das Skript bei jeder Interaktion vom Anfang neu startet. Außerdem hatte ich versucht, jede Eingabe (Titel, Content, Tags, Category) einzeln mit eigenem Submit-Button zu bauen, was zu unerwartetem Verhalten geführt hat: bei jedem Tippen auf einer Zeile wurde der ganze Status zurückgesetzt. Beim API-Call gegen mein eigenes FastAPI-Backend bin ich an einem trivialen, aber zeitraubenden Fehler hängengeblieben — ich hatte das FastAPI-Backend nicht gestartet und bekam einen `ConnectionRefusedError`, was ich erst spät gemerkt habe, weil Streamlit den Fehler nur im Server-Log und nicht prominent in der UI gezeigt hat. Bei der Tag-Eingabe als Komma-separierter String wusste ich nicht, wie ich diesen sauber in eine Liste umwandle, bevor ich ihn an die API schicke.

---

#### 3. 💡 How did I overcome them?

Das Streamlit-Reload-Verhalten aus Punkt 2 habe ich verstanden, nachdem ich konsequent auf das Pattern aus den Folien umgestiegen bin: alles, was über einen Rerun hinaus überleben muss, wandert in `st.session_state['xyz']`, mit dem typischen Init-Block `if 'xyz' not in st.session_state: st.session_state['xyz'] = ...`. Das mehrfache Submit-Problem habe ich mit `st.form('new_note')` und einem einzigen `st.form_submit_button` gelöst, wie auf der Folie als Tipp verlinkt — innerhalb eines `st.form`-Blocks lösen Eingabewidgets keine Reruns aus, sondern werden erst beim Submit gemeinsam abgeschickt. Das war ein echter Aha-Moment. Den `ConnectionRefusedError` habe ich gelöst, indem ich exakt den Tipp aus der Folie befolgt habe: zwei Terminals offen — Terminal 1 für `uv run fastapi dev`, Terminal 2 für `uv run streamlit run frontend.py`. Zur Sicherheit habe ich den API-Call mit `try/except requests.ConnectionError` umschlossen und mit `st.error("Backend nicht erreichbar — bitte FastAPI starten")` eine klare Meldung in der UI ausgegeben. Die Tags habe ich mit `[t.strip().lower() for t in tags_input.split(",") if t.strip()]` in eine saubere Liste verwandelt, was gleichzeitig leere Werte filtert und mit dem Tag-Validator aus Tag 5 harmoniert. Offen bleibt für mich, wie man in Streamlit professioneller mit Auth/Sessions umgeht und ob es einen idiomatischen Weg gibt, Reruns gezielt zu unterdrücken.

---
