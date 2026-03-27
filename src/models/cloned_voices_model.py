from typing import Self
from datetime import datetime, timezone
from pydantic import Field, BaseModel
from src.utils.constants import BaseSchema, Gender, PyObjectId, VoiceLanguages


class ClonedVoiceModel(BaseSchema):
    id: PyObjectId = Field(..., alias="_id")
    user_id: PyObjectId
    name: str = Field(..., min_length=2, max_length=100)
    gender: Gender
    language: VoiceLanguages
    url: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        alias="updatedAt"
    )


class UploadClonedVoiceRequest(BaseModel):
    user_id: PyObjectId
    name: str = Field(..., min_length=2, max_length=100)
    gender: Gender
    language: VoiceLanguages
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        alias="updatedAt"
    )

    @classmethod
    def as_form(
        cls,
        user_id: PyObjectId,
        name: str,
        gender: Gender,
        language: VoiceLanguages,
    ) -> Self:
        return cls(
            user_id=user_id,
            name=name,
            gender=gender,
            language=language,
        )


class UpdateClonedVoiceRequest(BaseModel):
    user_id: PyObjectId
    voice_id: PyObjectId
    name: str | None = Field(default=None, min_length=2, max_length=100)
    gender: Gender | None = Field(default=None)
    language: VoiceLanguages | None = Field(default=None)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        alias="updatedAt"
    )


class DeleteClonedVoiceRequest(BaseModel):
    user_id: PyObjectId
    voice_id: PyObjectId