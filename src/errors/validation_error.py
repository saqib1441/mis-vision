from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.utils.responses import ApiResponse


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        missing_fields: list[str] = []
        other_errors: list[str] = []

        for err in exc.errors():
            loc: tuple = err.get("loc", ())
            err_type: str = err.get("type", "")
            msg: str = err.get("msg", "")

            if err_type == "missing":
                if len(loc) > 1:
                    missing_fields.append(str(loc[1]))
            else:
                field_name = loc[-1] if len(loc) > 0 else "unknown_field"
                other_errors.append(f"{field_name} ({msg})")

        if missing_fields:
            return ApiResponse.error(
                message=f"Missing required fields: {missing_fields}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if other_errors:
            return ApiResponse.error(
                message=f"Invalid input data: {other_errors}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    return ApiResponse.error(
        message="Invalid input data",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
