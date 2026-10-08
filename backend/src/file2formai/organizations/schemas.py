import re
import uuid
from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _strip_nonempty(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("must not be blank")
    return stripped


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return _strip_nonempty(value) if value is not None else None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not SLUG_PATTERN.fullmatch(normalized):
            raise ValueError("must contain lowercase letters, numbers, and single hyphens")
        return normalized

    @model_validator(mode="after")
    def reject_null_fields(self) -> "OrganizationUpdate":
        for field_name in ("name", "slug"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} may not be null")
        return self


class OrganizationSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: uuid.UUID
    display_name: str
    logo_url: str | None
    primary_color: str
    secondary_color: str | None
    technician_label: str
    custom_settings: dict[str, Any]


class OrganizationSettingsUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    logo_url: AnyHttpUrl | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    technician_label: str | None = Field(default=None, min_length=1, max_length=100)
    custom_settings: dict[str, Any] | None = None

    @field_validator("display_name", "technician_label")
    @classmethod
    def normalize_labels(cls, value: str | None) -> str | None:
        return _strip_nonempty(value) if value is not None else None

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is not None and not COLOR_PATTERN.fullmatch(value):
            raise ValueError("must be a six-digit hexadecimal color such as #164E63")
        return value.upper() if value is not None else None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "OrganizationSettingsUpdate":
        for field_name in (
            "display_name",
            "primary_color",
            "technician_label",
            "custom_settings",
        ):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} may not be null")
        return self
