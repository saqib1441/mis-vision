from fastapi import APIRouter, Query, status
from src.models.task_model import TtsTaskModel
from src.utils.responses import ApiResponse
from src.db.config import mongodb
from bson import ObjectId

router = APIRouter()


@router.get("/")
async def get_all_tasks(
    page: int = Query(default=1, ge=1), limit: int = Query(default=10, le=100, ge=1)
):
    try:
        skip = (page - 1) * limit
        cursor = mongodb.tasks.find().sort("createdAt", -1).skip(skip).limit(limit)
        tasks = await cursor.to_list(length=limit)

        tasks_documents = [
            TtsTaskModel.model_validate(task).model_dump(mode="json", by_alias=True)
            for task in tasks
        ]

        return ApiResponse.success(data=tasks_documents)
    except Exception as e:
        return ApiResponse.error(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    try:
        delete_result = await mongodb.tasks.delete_one({"_id": ObjectId(task_id)})

        if delete_result.deleted_count == 0:
            return ApiResponse.error(
                message="Task not found", status_code=status.HTTP_404_NOT_FOUND
            )

        return ApiResponse.success(message="Task deleted successfully")
    except Exception as e:
        return ApiResponse.error(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
