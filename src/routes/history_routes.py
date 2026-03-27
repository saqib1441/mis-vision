from fastapi import APIRouter, Query, Path, status
from bson import ObjectId

from src.utils.constants import PyObjectId
from src.utils.responses import ApiResponse
from src.models.history_model import HistoryModel
from src.db.config import mongodb

router = APIRouter()


@router.get("/")
async def get_all_histories(
    page: int = Query(default=1, ge=1), limit: int = Query(default=10, le=10000, ge=1)
):
    try:
        skip = (page - 1) * limit
        cursor = mongodb.histories.find().sort("createdAt", -1).skip(skip).limit(limit)
        histories = await cursor.to_list(length=limit)

        histories_documents = [
            HistoryModel.model_validate(history).model_dump(mode="json", by_alias=True)
            for history in histories
        ]

        return ApiResponse.success(data=histories_documents)
    except Exception as e:
        return ApiResponse.error(
            error=e, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{history_id}")
async def delete_history(
    history_id: PyObjectId = Path(
        ..., description="The ID of the history record to delete"
    ),
    user_id: PyObjectId = Query(
        ..., description="The ID of the user requesting deletion"
    ),
):
    try:
        delete_result = await mongodb.histories.delete_one(
            {"_id": ObjectId(history_id), "userId": ObjectId(user_id)}
        )

        if delete_result.deleted_count == 0:
            return ApiResponse.error(
                message="History record not found or you do not have permission to delete it.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return ApiResponse.success(
            message="History record deleted successfully.", data=None
        )

    except Exception as e:
        return ApiResponse.error(
            error=e, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
