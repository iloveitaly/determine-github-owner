"""Data models for determine-github-owner."""

from pydantic import BaseModel


class ContactInfo(BaseModel):
    """Contact information for a GitHub user or package maintainer."""

    name: str | None = None
    email: str
