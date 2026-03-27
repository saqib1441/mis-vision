from contextlib import asynccontextmanager
from fastapi import FastAPI
import torch

from chatterbox.tts import ChatterboxTTS
from chatterbox.tts_turbo import ChatterboxTurboTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

from src.utils.ensure_directory_exists import ensure_directory_exists
from src.utils.logger import logger
from src.db.config import mongodb
from huggingface_hub import login
from src.utils.env import env


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing MongoDB connection...")
    await mongodb.connect()
    logger.info("MongoDB connection initialized successfully")

    logger.info("Ensuring all the required directories exists...")
    ensure_directory_exists()

    logger.info("Logging into Huggingface Hub...")
    login(env.HF_TOKEN)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Initializing TTS models on device: {device}")

    app.state.tts_model = None
    app.state.turbo_model = None
    app.state.mtl_model = None

    try:
        with torch.no_grad():
            logger.info("Loading Chatterbox TTS model")
            tts_model = ChatterboxTTS.from_pretrained(device=f"{device}")
            app.state.tts_model = tts_model
            tts_model.generate("Warmup")

            logger.info("Loading Chatterbox Turbo TTS model")
            turbo_model = ChatterboxTurboTTS.from_pretrained(device=f"{device}")
            app.state.turbo_model = turbo_model
            turbo_model.generate("Warmup")

            logger.info("Loading Chatterbox Multilingual TTS model")
            mlt_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
            app.state.mtl_model = mlt_model
            mlt_model.generate("Warmup", language_id="en")

        logger.info("All TTS models loaded successfully")
        yield

    except Exception as exc:
        logger.error(f"TTS model initialization failed: {exc}")

        for attr in ("tts_model", "turbo_model", "mtl_model"):
            model = getattr(app.state, attr, None)
            if model is not None:
                del model
                setattr(app.state, attr, None)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        raise

    finally:
        logger.info("FastAPI lifespan shutdown started")

        logger.info("Closing TTS models...")
        for attr in ("tts_model", "turbo_model", "mtl_model"):
            model = getattr(app.state, attr, None)
            if model is not None:
                del model
                setattr(app.state, attr, None)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Closing MongoDB connection...")
        await mongodb.close()
        logger.info("MongoDB connection closed successfully")

        logger.info("FastAPI lifespan shutdown completed")
