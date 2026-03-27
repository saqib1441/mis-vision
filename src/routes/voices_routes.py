from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from src.models.voice_model import (
    VoiceModel,
    UploadVoiceRequest,
    UpdateVoiceRequest,
    DeleteVoiceRequest,
    LoadVoicesRequest,
)
from src.utils.voice_names import normalize_name, slugify_name
from src.utils.constants import voices_data
from src.utils.get_user import require_admin
from src.utils.responses import ApiResponse
from src.db.config import mongodb

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICES_FOLDER = PROJECT_ROOT / "voices"
VOICES_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_DIRS = [
    (PROJECT_ROOT / "voices").resolve(),
    (PROJECT_ROOT / "cloned_voices").resolve(),
    (PROJECT_ROOT / "outputs").resolve(),
]

ALLOWED_EXTENSIONS = {".mp3", ".wav"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.get("/play")
async def play_audio(
    url: str = Query(..., description="The relative path of the audio file"),
):
    try:
        requested_path = (PROJECT_ROOT / url.lstrip("/")).resolve()

        is_allowed = any(
            requested_path.is_relative_to(allowed) for allowed in ALLOWED_DIRS
        )

        if not is_allowed or not requested_path.is_file():
            return ApiResponse.error(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Access denied or file does not exist",
            )

        def iterfile():
            with open(requested_path, mode="rb") as file_like:
                while chunk := file_like.read(64 * 1024):
                    yield chunk

        return StreamingResponse(
            iterfile(),
            media_type="audio/mpeg",
            headers={"Accept-Ranges": "bytes", "Cache-Control": "no-cache"},
        )

    except Exception as e:
        return ApiResponse.error(error=e)


@router.get("/all")
async def get_all_voices():
    try:
        voices = await mongodb.voices.find().to_list(length=1000)

        if not voices:
            return ApiResponse.success(message="No voices found", data=[])

        serialized = [VoiceModel(**voice).model_dump(mode="json") for voice in voices]

        return ApiResponse.success(data=serialized)

    except Exception as e:
        return ApiResponse.error(error=e)


@router.post("/upload")
async def upload_voice(
    body: UploadVoiceRequest = Depends(UploadVoiceRequest.as_form),
    file: UploadFile = File(...),
):
    try:
        await require_admin(body.user_id)

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
        file_path = VOICES_FOLDER / unique_filename

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
            "name": normalize_name(body.name),
            "url": f"voices/{unique_filename}",
            "gender": body.gender,
            "language": body.language,
        }

        await mongodb.voices.insert_one(voice_data)

        return ApiResponse.success(message="Voice uploaded successfully")

    except Exception as e:
        return ApiResponse.error(error=e)


@router.post("/load")
async def load_voices(body: LoadVoicesRequest):
    try:
        await require_admin(body.user_id)

        existing = await mongodb.voices.find({}, {"url": 1}).to_list(length=None)
        existing_urls = {v["url"] for v in existing}

        new_voices = [v for v in voices_data if v["url"] not in existing_urls]

        if not new_voices:
            return ApiResponse.success(message="All default voices are already loaded")

        await mongodb.voices.insert_many(new_voices)

        return ApiResponse.success(
            message=f"{len(new_voices)} new voice(s) loaded successfully"
        )
    except Exception as e:
        return ApiResponse.error(error=e)


@router.put("/update")
async def update_voice(body: UpdateVoiceRequest):
    try:
        await require_admin(body.user_id)

        update_data = {}
        if body.name is not None:
            update_data["name"] = normalize_name(body.name)
        if body.gender is not None:
            update_data["gender"] = body.gender
        if body.language is not None:
            update_data["language"] = body.language

        if not update_data:
            return ApiResponse.success(message="Nothing to update")

        voice = await mongodb.voices.find_one({"_id": body.voice_id})
        if not voice:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Voice not found",
            )

        await mongodb.voices.update_one({"_id": body.voice_id}, {"$set": update_data})

        return ApiResponse.success(message="Voice updated successfully")

    except Exception as e:
        return ApiResponse.error(error=e)


@router.delete("/delete")
async def delete_voice(body: DeleteVoiceRequest):
    try:
        await require_admin(body.user_id)

        voice = await mongodb.voices.find_one({"_id": body.voice_id})

        if not voice:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Voice not found",
            )

        delete_result = await mongodb.voices.delete_one({"_id": body.voice_id})

        if delete_result.deleted_count > 0:
            relative_path = voice["url"].lstrip("/")
            file_path = PROJECT_ROOT / relative_path

            if file_path.exists():
                file_path.unlink()

            return ApiResponse.success(message="Voice deleted successfully")

        return ApiResponse.error(message="Failed to delete voice record")

    except Exception as e:
        return ApiResponse.error(error=e)
