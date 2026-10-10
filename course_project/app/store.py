"""Small in-memory store used by the course starter project."""

from app.models import Note, NoteCreate, utc_now


class NoteStore:
    def __init__(self) -> None:
        self._notes: list[Note] = []
        self._next_id = 1

    def list_notes(self) -> list[Note]:
        return list(self._notes)

    def create_note(self, request: NoteCreate) -> Note:
        note = Note(
            id=self._next_id,
            title=request.title,
            body=request.body,
            created_at=utc_now(),
        )
        self._next_id += 1
        self._notes.append(note)
        return note

    def clear(self) -> None:
        """Reset in-memory state. Intended for isolated tests and demos."""
        self._notes.clear()
        self._next_id = 1


note_store = NoteStore()
