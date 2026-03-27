from typing import Annotated, Optional
from fastapi import Form
from pydantic import Field, BaseModel
from src.utils.constants import BaseSchema, Gender, PyObjectId, VoiceLanguages


class VoiceModel(BaseSchema):
    id: PyObjectId = Field(..., description="ID of the voice", alias="_id")
    name: str = Field(..., min_length=2, max_length=100, description="Display name")
    gender: Gender = Field(..., description="Gender of the voice")
    language: VoiceLanguages = Field(..., description="Language code")
    url: str = Field(..., description="Relative URL to the audio file")


class LoadVoicesRequest(BaseModel):
    user_id: PyObjectId = Field(
        ..., description="ID of the admin performing the action"
    )


class UploadVoiceRequest(BaseModel):
    user_id: PyObjectId = Field(..., description="ID of the admin uploading the voice")
    name: str = Field(
        ..., min_length=2, max_length=100, description="Name of the voice"
    )
    gender: Gender = Field(..., description="Gender of the voice")
    language: VoiceLanguages = Field(..., description="Language code")

    @classmethod
    def as_form(
        cls,
        user_id: Annotated[PyObjectId, Form(...)],
        name: Annotated[str, Form(...)],
        gender: Annotated[Gender, Form(...)],
        language: Annotated[VoiceLanguages, Form(...)],
    ):
        return cls(
            user_id=user_id,
            name=name,
            gender=gender,
            language=language,
        )


class UpdateVoiceRequest(BaseModel):
    user_id: PyObjectId = Field(..., description="ID of the admin")
    voice_id: PyObjectId = Field(..., description="ID of the voice to update")
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    gender: Optional[Gender] = Field(None)
    language: Optional[VoiceLanguages] = Field(None)


class DeleteVoiceRequest(BaseModel):
    user_id: PyObjectId = Field(..., description="ID of the admin")
    voice_id: PyObjectId = Field(..., description="ID of the voice to delete")
