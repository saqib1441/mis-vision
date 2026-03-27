from datetime import datetime, timezone
from typing import Optional
from pydantic import Field, BaseModel
from src.utils.constants import BaseSchema, ModelType, PyObjectId


class TtsRecordModel(BaseSchema):
    id: PyObjectId = Field(..., alias="_id", description="Unique record ID")
    user_id: PyObjectId = Field(
        ..., alias="userId", description="The user who generated this audio"
    )

    text: str = Field(..., min_length=1, max_length=50001, description="The input text")
    character_count: int = Field(
        ..., alias="characterCount", ge=1, description="Length of the input text"
    )

    voice_id: PyObjectId = Field(
        ..., alias="voiceId", description="ID of the voice used"
    )
    generated_url: str = Field(
        ..., alias="generatedUrl", description="URL to the produced audio file"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="createdAt"
    )


class GenerateTtsRequest(BaseModel):
    user_id: Optional[PyObjectId] = Field(
        ..., description="User ID for quota verification"
    )
    voice_id: PyObjectId = Field(..., description="The voice ID to use for generation")
    text: str = Field(
        ..., min_length=1, max_length=50001, description="Text to synthesize"
    )
    model_type: ModelType = Field(default=ModelType.DEFAULT_MODEL)
