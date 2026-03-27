import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Request, status, BackgroundTasks

from src.utils.tts_worker import process_tts_task
from src.utils.responses import ApiResponse
from src.utils.get_user import get_user
from src.models.tts_model import GenerateTtsRequest
from src.db.config import mongodb

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@router.post("/synthesize")
async def synthesize(
    request: Request, body: GenerateTtsRequest, background_tasks: BackgroundTasks
):
    try:
        user = await get_user(id=body.user_id)
        if not user:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND, message="User not found"
            )

        voice = await mongodb.cloned_voices.find_one({"_id": body.voice_id})
        if not voice:
            voice = await mongodb.voices.find_one({"_id": body.voice_id})

        if not voice:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Voice ID not found in system or clones",
            )

        stored_path = voice["url"].lstrip("/")
        filename = os.path.basename(stored_path)

        potential_paths = [
            BASE_DIR / stored_path,
            BASE_DIR / "voices" / filename,
            BASE_DIR / "cloned_voices" / filename,
        ]

        resolved_path = None
        for p in potential_paths:
            if p.exists():
                resolved_path = p
                break

        if not resolved_path:
            return ApiResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Reference audio file not found on disk: {filename}",
            )

        tts_engines = {
            "default_model": getattr(request.app.state, "tts_model", None),
            "multilingual_model": getattr(request.app.state, "mtl_model", None),
            "turbo_model": getattr(request.app.state, "turbo_model", None),
        }

        if tts_engines.get(body.model_type) is None:
            return ApiResponse.error(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message=f"TTS Engine '{body.model_type}' is not initialized on this server.",
            )

        task_data = {
            "userId": str(body.user_id),
            "text": body.text.strip(),
            "voiceUrl": str(resolved_path),
            "modelType": body.model_type,
            "status": "pending",
            "progress": 0,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        task_result = await mongodb.tasks.insert_one(task_data)
        task_id = task_result.inserted_id

        background_tasks.add_task(
            process_tts_task,
            task_id=task_id,
            user_id=body.user_id,
            voice_id=body.voice_id,
            text=body.text.strip(),
            voice_url=str(resolved_path),
            voice_lang=voice.get("language", "en"),
            model_type=body.model_type,
            tts_engines=tts_engines,
        )

        return ApiResponse.success(
            message="Generation started in background", data={"taskId": str(task_id)}
        )

    except Exception as e:
        print(f"Synthesize Route Error: {str(e)}")
        return ApiResponse.error(error=e)
