from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from src.errors.validation_error import validation_exception_handler
from src.utils.responses import ApiResponse
from src.utils.lifespan import lifespan
from src.utils.env import env
from fastapi.middleware.cors import CORSMiddleware
from src.routes.voices_routes import router as voices_router
from src.routes.cloned_voices_routes import router as cloned_voices_router
from src.routes.tts_routes import router as tts_router
from src.routes.tasks_routes import router as tasks_router
from src.routes.history_routes import router as history_router

app = FastAPI(
    title="Melo-AI TTS Server",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if env.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if env.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if env.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[env.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def root():
    return ApiResponse.success(message="Melo-AI TTS Server is running")


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(
        status_code=exc.status_code,
        message="Oops! The resource you requested was not found.",
    )


app.include_router(router=voices_router, prefix="/api/voices", tags=["Voices"])
app.include_router(
    router=cloned_voices_router, prefix="/api/cloned-voices", tags=["Cloned Voices"]
)
app.include_router(router=tts_router, prefix="/api/tts", tags=["TTS"])
app.include_router(router=tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(router=history_router, prefix="/api/histories", tags=["History"])
