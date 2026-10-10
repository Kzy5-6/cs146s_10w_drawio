"""HTTP API for the meeting notes course project."""

from fastapi import FastAPI

from app.models import Note, NoteCreate
from app.store import note_store


app = FastAPI(title="Meeting Notes API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes() -> list[Note]:
    return note_store.list_notes()


@app.post("/notes", response_model=Note, status_code=201)
def create_note(request: NoteCreate) -> Note:
    return note_store.create_note(request)
