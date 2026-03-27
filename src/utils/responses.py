from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi import status
import traceback
from src.utils.env import env


class ApiResponse:
    @staticmethod
    def success(
        *,
        message: Optional[str] = None,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> JSONResponse:
        response: Dict[str, Any] = {
            "success": True,
        }

        if message is not None:
            response["message"] = message

        if data is not None:
            response["data"] = data

        return JSONResponse(
            status_code=status_code,
            content=response,
        )

    @staticmethod
    def error(
        *,
        message: Optional[str] = None,
        error: Optional[Exception] = None,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> JSONResponse:
        error_message = "Something went wrong"

        if message:
            error_message = message
        elif isinstance(error, Exception) and str(error):
            error_message = str(error)

        response: Dict[str, Any] = {
            "success": False,
            "message": error_message,
        }

        if data is not None:
            response["data"] = data

        if env.ENVIRONMENT == "development" and isinstance(error, Exception):
            response["stack"] = traceback.format_exc()

        return JSONResponse(
            status_code=status_code,
            content=response,
        )
