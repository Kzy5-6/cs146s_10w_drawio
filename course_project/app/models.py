"""Request and response models for the meeting notes API."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="", max_length=4000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for new notes."""
    return datetime.now(timezone.utc)
