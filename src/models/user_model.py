from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

from src.utils.constants import Plans, PyObjectId, Role


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: Role = Role.USER
    current_plan: Plans = Plans.FREE
    total_characters: int = Field(default=20000, ge=0)
    used_characters: int = Field(default=0, ge=0)
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
