from datetime import datetime, timezone
from typing import Optional
from pydantic import Field, BaseModel
from src.utils.constants import BaseSchema, PyObjectId, TaskStatus


class TtsTaskModel(BaseSchema):
    id: PyObjectId = Field(..., alias="_id", description="Unique task ID")
    user_id: Optional[PyObjectId] = Field(
        ..., alias="userId", description="Owner of the task"
    )
    text: str = Field(
        ..., min_length=1, max_length=50001, description="Text to be processed"
    )
    voice_url: str = Field(..., alias="voiceUrl", description="Source voice URL")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress: int = Field(
        default=0, ge=0, le=100, description="Task progress percentage"
    )

    generated_file: Optional[str] = Field(
        default=None,
        alias="generatedFile",
        description="Path to the outputs audio file",
    )
    error: Optional[str] = Field(
        default=None, description="Error message if the task failed"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="updatedAt"
    )


class CreateTaskRequest(BaseModel):
    user_id: Optional[PyObjectId] = Field(
        ..., description="ID of the user creating the task"
    )
    text: str = Field(..., min_length=1, max_length=50001)
    voice_url: str = Field(..., description="URL or identifier of the voice to use")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="updatedAt"
    )


class UpdateTaskStatusRequest(BaseModel):
    task_id: PyObjectId = Field(..., description="ID of the task to update")
    status: Optional[TaskStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    generated_file: Optional[str] = Field(None, alias="generatedFile")
    error: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), alias="updatedAt"
    )
