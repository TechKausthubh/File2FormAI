import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _strip_nonempty(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("must not be blank")
    return stripped


class EquipmentModelCreate(BaseModel):
    manufacturer: str = Field(min_length=1, max_length=200)
    model_name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("manufacturer", "model_name")
    @classmethod
    def normalize_required_names(cls, value: str) -> str:
        return _strip_nonempty(value)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()


class EquipmentModelUpdate(BaseModel):
    manufacturer: str | None = Field(default=None, min_length=1, max_length=200)
    model_name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    metadata: dict[str, Any] | None = None

    @field_validator("manufacturer", "model_name")
    @classmethod
    def normalize_required_names(cls, value: str | None) -> str | None:
        return _strip_nonempty(value) if value is not None else None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def reject_null_fields(self) -> "EquipmentModelUpdate":
        for field_name in ("manufacturer", "model_name", "description", "metadata"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} may not be null")
        return self


class EquipmentModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    manufacturer: str
    model_name: str
    description: str
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime


class EquipmentInstanceCreate(BaseModel):
    equipment_model_id: uuid.UUID
    serial_number: str | None = Field(default=None, max_length=200)
    display_name: str = Field(min_length=1, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        return _strip_nonempty(value)

    @field_validator("serial_number")
    @classmethod
    def normalize_serial_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class EquipmentInstanceUpdate(BaseModel):
    equipment_model_id: uuid.UUID | None = None
    serial_number: str | None = Field(default=None, max_length=200)
    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    metadata: dict[str, Any] | None = None

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        return _strip_nonempty(value) if value is not None else None

    @field_validator("serial_number")
    @classmethod
    def normalize_serial_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "EquipmentInstanceUpdate":
        for field_name in ("equipment_model_id", "display_name", "metadata"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} may not be null")
        return self


class EquipmentInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    equipment_model_id: uuid.UUID
    serial_number: str | None
    display_name: str
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime
