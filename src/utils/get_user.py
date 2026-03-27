from src.utils.constants import PyObjectId
from src.utils.responses import ApiResponse
from src.models.user_model import User
from src.db.config import mongodb
from fastapi import status


async def get_user(id: PyObjectId) -> User | None:
    if not id:
        ApiResponse.error(message="User ID is required")
        return None

    user = await mongodb.users.find_one({"_id": id})

    if not user:
        ApiResponse.error(message="User not found")
        return None

    return User(**user)


async def require_admin(user_id: PyObjectId):
    user = await get_user(id=user_id)
    if not user:
        return ApiResponse.error(
            status_code=status.HTTP_404_NOT_FOUND,
            message="User not found",
        )
    if user.role != "admin":
        return ApiResponse.error(
            status_code=status.HTTP_403_FORBIDDEN,
            message="You are not authorized to perform this action",
        )
    return user
