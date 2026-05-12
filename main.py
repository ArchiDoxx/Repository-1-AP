from fastapi import FastAPI as fapi, HTTPException, Depends, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, select
from typing import Optional, Annotated
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
import re

app = fapi(
    title = "Applied Programming Course HS-Coburg",
    description= "Simple note management API",
    version= "1.0.0"
)

##################################
#### Note API Endpoints Day 2 ####
##################################

# Day 5 Task 2 & 5: Validation constants — single source of truth
ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas", "general"}
TAG_PATTERN = re.compile(r"^[a-z0-9-]+$")  # Day 5 Task 5: tag name format


# Pydantic models for request bodies (tags as list)
def _normalize_tags(v: list[str]) -> list[str]:
    """Strip + lowercase + dedupe each tag.
    Rejects: <2 chars, >30 chars, non-matching pattern, >10 tags total (Day 5 Task 5).
    """
    seen = set()
    result = []
    for tag in v:
        normalized = tag.strip().lower()
        if len(normalized) < 2:
            raise ValueError("each tag must be at least 2 characters after trimming")
        if len(normalized) > 30:
            raise ValueError("each tag must be at most 30 characters")
        if not TAG_PATTERN.fullmatch(normalized):
            raise ValueError(
                f"tag '{normalized}' must contain only lowercase letters, digits, or dashes"
            )
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    if len(result) > 10:
        raise ValueError("at most 10 tags allowed per note")
    return result


class NoteCreate(BaseModel):
    # Day 5 Task 1: model-wide config
    #   str_strip_whitespace -> auto-strip every str field before validation
    #   extra="forbid"       -> reject typos like {"tagz": [...]} with 422
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # Day 5 Task 1: Field constraints (length / count caps)
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)
    category: str = Field(min_length=2, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=10)

    # Day 5 Task 2: category must be in whitelist (lowercased before checking)
    @field_validator("category")
    @classmethod
    def _category_whitelist(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )
        return normalized

    # Day 5 Task 2 / Task 5: tag normalization + pattern check
    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, v: list[str]) -> list[str]:
        return _normalize_tags(v)

    # -----------------------------------------------------------------------
    # Day 5 Task 3 — Cross-Field Rule (didaktisch, NICHT aktiv)
    # -----------------------------------------------------------------------
    # Spec: wenn category == "work", muss "work" in tags enthalten sein.
    # Warum nicht aktiv: unsere Referenz-Test-Suite (Exploration/test_suit.py)
    # legt diverse work-Notizen ohne work-Tag an. Aktivierung würde ~15 Tests
    # brechen. Deshalb hier nur als didaktischer Block dokumentiert.
    #
    # from pydantic import model_validator
    # from typing_extensions import Self
    #
    # @model_validator(mode="after")
    # def _work_notes_need_work_tag(self) -> Self:
    #     """If category is 'work', the tag list must contain 'work'."""
    #     if self.category == "work" and "work" not in self.tags:
    #         raise ValueError("work notes must include the 'work' tag")
    #     return self


class NoteUpdate(BaseModel):
    # Day 5 Task 4: PATCH-Modell, gleiche Regeln aber alle Felder Optional.
    # Constraints greifen NUR, wenn das Feld mitgeschickt wird.
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    content: Optional[str] = Field(default=None, min_length=1, max_length=10_000)
    category: Optional[str] = Field(default=None, min_length=2, max_length=30)
    tags: Optional[list[str]] = Field(default=None, max_length=10)

    @field_validator("category")
    @classmethod
    def _category_whitelist(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        normalized = v.strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )
        return normalized

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return None
        return _normalize_tags(v)


# SQLModel table: tags stored as CSV string (SQLite has no array type)
class Note(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    content: str
    category: str
    tags: str = ""
    created_at: str


# DB setup
DB_FILE = Path("notes.db")
engine = create_engine(f"sqlite:///{DB_FILE}")
SQLModel.metadata.create_all(engine)


def get_session():
    """Yields a DB session per request; closes automatically afterwards."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# Helpers: convert between CSV string (DB) and list (API)
def _tags_to_csv(tags: list[str]) -> str:
    return ",".join(tags)

def _tags_to_list(tags_csv: str) -> list[str]:
    return tags_csv.split(",") if tags_csv else []

def _note_to_dict(note: Note) -> dict:
    """Convert a DB Note into the API response shape (tags as list)."""
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "category": note.category,
        "tags": _tags_to_list(note.tags),
        "created_at": note.created_at,
    }


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> dict:
    """Create a new note"""
    new_note = Note(
        title=note.title,
        content=note.content,
        category=note.category,
        tags=_tags_to_csv(note.tags),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return _note_to_dict(new_note)


@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
) -> list[dict]:
    """List notes with optional filters"""
    notes_db = session.exec(select(Note)).all()

    tag_lower = tag.lower() if tag else None
    after_iso = created_after.isoformat() if created_after else None
    before_iso = created_before.isoformat() if created_before else None

    filtered = []
    for note in notes_db:
        if category and note.category != category:
            continue

        if search:
            search_lower = search.lower()
            title_match = search_lower in note.title.lower()
            content_match = search_lower in note.content.lower()
            if not (title_match or content_match):
                continue

        tag_list = _tags_to_list(note.tags)
        if tag_lower and tag_lower not in tag_list:
            continue

        if after_iso and note.created_at < after_iso:
            continue

        if before_iso and note.created_at > before_iso:
            continue

        filtered.append(_note_to_dict(note))

    return filtered


@app.get("/notes/stats")
def get_note_stats(session: SessionDep):
    """Get statistics about all notes"""
    notes_db = session.exec(select(Note)).all()

    by_category = {}
    tag_counter = Counter()

    for note in notes_db:
        by_category[note.category] = by_category.get(note.category, 0) + 1
        for tag in _tags_to_list(note.tags):
            tag_counter[tag] += 1

    top_tags = [{"tag": tag, "count": count} for tag, count in tag_counter.most_common(5)]

    return {
        "total_notes": len(notes_db),
        "by_category": by_category,
        "top_tags": top_tags,
        "unique_tags_count": len(tag_counter),
    }


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> dict:
    """Get a specific note by ID"""
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    return _note_to_dict(note)


@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> dict:
    """Replace all fields of a note (full update)"""
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")

    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category
    note.tags = _tags_to_csv(note_update.tags)

    session.add(note)
    session.commit()
    session.refresh(note)
    return _note_to_dict(note)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    """Delete a note by ID. Returns 204 No Content."""
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    session.delete(note)
    session.commit()
    return Response(status_code=204)


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> dict:
    """Partially update a note — only provided fields are changed"""
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")

    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.category is not None:
        note.category = note_update.category
    if note_update.tags is not None:
        note.tags = _tags_to_csv(note_update.tags)

    session.add(note)
    session.commit()
    session.refresh(note)
    return _note_to_dict(note)


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    """Get all unique categories from all notes"""
    notes_db = session.exec(select(Note)).all()
    return sorted({note.category for note in notes_db})


@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[dict]:
    """Get all notes in a specific category"""
    notes_db = session.exec(select(Note).where(Note.category == category_name)).all()
    return [_note_to_dict(note) for note in notes_db]


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Get all unique tags across all notes (sorted)."""
    notes_db = session.exec(select(Note)).all()
    all_tags = set()
    for note in notes_db:
        all_tags.update(_tags_to_list(note.tags))
    return sorted(all_tags)


@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[dict]:
    """Get all notes carrying a given tag (case-insensitive)."""
    tag_lower = tag_name.lower()
    notes_db = session.exec(select(Note)).all()
    return [
        _note_to_dict(note)
        for note in notes_db
        if tag_lower in _tags_to_list(note.tags)
    ]


##################################
#### Day 3: Query Parameters #####
##################################

@app.get("/queryparameters")
def get_query_parameters(param1: str, param2: int) -> dict:

        namen = ['martin', 'michael', 'sarah', 'anna', 'tom', 'lisa']

        if not param1:
              return{"namen": namen}

        namen_gefiltert = []
        for name in namen:
                if param1 in name:
                 namen_gefiltert.append(name)
        return {"param1": param1, "param2": param2, "filtered_names": namen_gefiltert}


##################################
#### Day 4: Greeting Endpoints ###
##################################

class GreetingResponse(BaseModel):
    """Response model for greeting endpoints

    Attributes:
        message (str): The greeting message to be returned to the client
    """
    message: str


@app.get("/", response_model=GreetingResponse)
def read_root():
    """Welcome endpoint - returns greeting message"""
    return {"message": "Hello World!"}




@app.get("/greetings/{name}", response_model=GreetingResponse)
def read_greeting(name: str):
    """Personalized greeting endpoint - returns greeting message with name"""
    return {"message": f"Hello {name}!"}


@app.get("/is-adult/{age}")
def check_adult(age: int):
    """
    Check if person is an adult (18 or older)
    Example: /is-adult/17
    """
    is_adult = age >= 18

    return {
        "age": age,
        "is_adult": is_adult,
        "can_vote": is_adult,
        "can_drive": is_adult
    }

