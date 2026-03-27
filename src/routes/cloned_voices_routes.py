from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, status
from src.models.cloned_voices_model import (
    ClonedVoiceModel,
    UploadClonedVoiceRequest,
    UpdateClonedVoiceRequest,
    DeleteClonedVoiceRequest,
)
from src.utils.get_user import get_user
from src.utils.voice_names import normalize_name, slugify_name
from src.utils.constants import PyObjectId
from src.db.config import mongodb
from src.utils.responses import ApiResponse

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLONED_VOICES_FOLDER = PROJECT_ROOT / "cloned_voices"
CLONED_VOICES_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.get("/all")
async def get_all_cloned_voices(user_id: PyObjectId):
    try:
        user = await get_user(id=user_id)
        if not user:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found",
            )

        voices = await mongodb.cloned_voices.find({"user_id": user_id}).to_list(
            length=None
        )

        if not voices:
            return ApiResponse.success(
                message="You have not uploaded any voice yet!", data=None
            )

        serialized = [
            ClonedVoiceModel(**voice).model_dump(mode="json") for voice in voices
        ]

        return ApiResponse.success(data=serialized)

    except Exception as e:
        return ApiResponse.error(error=e)


@router.post("/upload")
async def upload_cloned_voice(
    body: UploadClonedVoiceRequest = Depends(UploadClonedVoiceRequest.as_form),
    file: UploadFile = File(...),
):
    try:
        user = await get_user(id=body.user_id)
        if not user:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found",
            )

        if not file.filename:
            return ApiResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="No file uploaded",
            )

        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            return ApiResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}",
            )

        unique_filename = f"{slugify_name(body.name)}-{uuid4().hex}{suffix}"
        file_path = CLONED_VOICES_FOLDER / unique_filename

        size = 0
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    file_path.unlink(missing_ok=True)
                    return ApiResponse.error(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="File size limit exceeded (5MB)",
                    )
                buffer.write(chunk)

        voice_data = {
            "user_id": body.user_id,
            "name": normalize_name(body.name),
            "url": f"/cloned_voices/{unique_filename}",
            "gender": body.gender,
            "language": body.language,
        }

        await mongodb.cloned_voices.insert_one(voice_data)

        return ApiResponse.success(message="Voice uploaded successfully")

    except Exception as e:
        return ApiResponse.error(error=e)


@router.put("/update")
async def update_cloned_voice(body: UpdateClonedVoiceRequest):
    try:
        update_data = {}
        if body.name is not None:
            update_data["name"] = normalize_name(body.name)
        if body.gender is not None:
            update_data["gender"] = body.gender
        if body.language is not None:
            update_data["language"] = body.language

        if not update_data:
            return ApiResponse.success(message="Nothing to update")

        voice = await mongodb.cloned_voices.find_one(
            {"_id": body.voice_id, "user_id": body.user_id}
        )

        if not voice:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Voice not found or you do not have permission to edit it",
            )

        await mongodb.cloned_voices.update_one(
            {"_id": body.voice_id}, {"$set": update_data}
        )

        return ApiResponse.success(message="Voice updated successfully")

    except Exception as e:
        return ApiResponse.error(error=e)


@router.delete("/delete")
async def delete_cloned_voice(body: DeleteClonedVoiceRequest):
    try:
        voice = await mongodb.cloned_voices.find_one(
            {"_id": body.voice_id, "user_id": body.user_id}
        )

        if not voice:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Voice not found or you do not have permission to delete it",
            )

        delete_result = await mongodb.cloned_voices.delete_one({"_id": body.voice_id})

        if delete_result.deleted_count > 0:
            relative_path = voice["url"].lstrip("/")
            file_path = PROJECT_ROOT / relative_path

            if file_path.exists():
                file_path.unlink()

            return ApiResponse.success(message="Voice deleted successfully")

        return ApiResponse.error(message="Failed to delete voice record")

    except Exception as e:
        return ApiResponse.error(error=e)
