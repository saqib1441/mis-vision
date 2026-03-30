import torch
import numpy as np
import scipy.io.wavfile as wavfile
from uuid import uuid4
from datetime import datetime, timezone
from pathlib import Path

from src.db.config import mongodb
from src.utils.chunks import text_to_chunks
from src.utils.constants import PyObjectId, TaskStatus, ModelType


def process_audio_tensor(audio_tensor):
    if torch.is_tensor(audio_tensor):
        return audio_tensor.detach().cpu().numpy().flatten()
    return np.array(audio_tensor).flatten()


def finalize_audio_and_save(audio_list, sample_rate, output_path):
    if not audio_list:
        return False

    full_audio = np.concatenate(audio_list)

    max_val = np.max(np.abs(full_audio))
    if max_val > 0:
        full_audio = full_audio / max_val

    audio_int16 = (full_audio * 32767).astype(np.int16)

    wavfile.write(output_path, sample_rate, audio_int16)
    return True


async def process_tts_task(
    task_id: PyObjectId,
    user_id: PyObjectId,
    voice_id: PyObjectId,
    text: str,
    voice_url: str,
    voice_lang: str,
    model_type: ModelType,
    tts_engines: dict,
):
    audio_chunks_in_memory = []
    output_dir = Path("outputs")

    final_filename = f"melo-ai_{uuid4().hex}.wav"
    final_path = output_dir / final_filename

    try:
        await mongodb.tasks.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": TaskStatus.PROCESSING,
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
        )

        chunks = text_to_chunks(text=text, model_type=model_type, max_chars=250)
        total_chunks = len(chunks)

        engine = tts_engines.get(model_type)
        if engine is None:
            raise ValueError(f"Engine {model_type} not found.")

        for i, chunk_text in enumerate(chunks):
            gen_kwargs = {
                "text": chunk_text.strip(),
                "audio_prompt_path": voice_url,
                "cfg_weight": 0.4,
                "exaggeration": 0.7,
                "temperature": 0.7,
                "repetition_penalty": 1.2,
            }
            if model_type == ModelType.MULTILINGUAL_MODEL:
                gen_kwargs["language_id"] = voice_lang

            with torch.inference_mode():
                raw_audio = engine.generate(**gen_kwargs)

            processed_chunk = process_audio_tensor(raw_audio)
            audio_chunks_in_memory.append(processed_chunk)

            progress = int(((i + 1) / total_chunks) * 100)
            await mongodb.tasks.update_one(
                {"_id": task_id},
                {
                    "$set": {
                        "progress": min(progress, 99),
                        "updatedAt": datetime.now(timezone.utc),
                    }
                },
            )

        finalize_audio_and_save(audio_chunks_in_memory, engine.sr, str(final_path))

        await mongodb.tasks.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": TaskStatus.COMPLETED,
                    "progress": 100,
                    "generatedFile": f"/outputs/{final_filename}",
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
        )

        await mongodb.histories.insert_one(
            {
                "userId": user_id,
                "text": text,
                "voice": voice_id,
                "generatedVoice": f"/outputs/{final_filename}",
                "createdAt": datetime.now(timezone.utc),
            }
        )

    except Exception as e:
        await mongodb.tasks.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": TaskStatus.FAILED,
                    "error": str(e),
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
        )
        print(f"Worker Failure: {e}")
