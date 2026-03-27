from datetime import datetime, timezone
from pydantic import Field, BaseModel, ConfigDict
from src.utils.constants import BaseSchema, PyObjectId


class HistoryModel(BaseSchema):
    id: PyObjectId = Field(..., alias="_id")
    user_id: PyObjectId = Field(..., alias="userId")
    text: str = Field(..., min_length=1, max_length=50000)
    voice_id: PyObjectId = Field(..., alias="voiceId")
    generated_voice_url: str = Field(..., alias="generatedVoiceUrl")
    created_at: datetime = Field(default_factory=datetime.now(tz=timezone.utc), alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class CreateHistoryRequest(BaseModel):
    user_id: PyObjectId
    text: str = Field(..., min_length=1, max_length=50000)
    voice_id: PyObjectId
    generated_voice_url: str


class DeleteHistoryRequest(BaseModel):
    user_id: PyObjectId
    history_id: PyObjectId


class HistoryResponse(BaseModel):
    id: str
    text: str
    voice_id: str
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)