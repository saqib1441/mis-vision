from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from src.utils.env import env


class MongoDB:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None

    users: AsyncIOMotorCollection
    voices: AsyncIOMotorCollection
    histories: AsyncIOMotorCollection
    cloned_voices: AsyncIOMotorCollection
    tasks: AsyncIOMotorCollection

    async def connect(self) -> None:
        if self.client is None:
            self.client = AsyncIOMotorClient(env.MONGODB_URL)
            self.database = self.client[env.DB_NAME]

            self.users = self.database["user"]
            self.voices = self.database["voices"]
            self.histories = self.database["histories"]
            self.cloned_voices = self.database["cloned_voices"]
            self.tasks = self.database["tasks"]

            assert self.users is not None
            assert self.voices is not None
            assert self.histories is not None
            assert self.cloned_voices is not None
            assert self.tasks is not None

    async def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None

            self.users = None  # type: ignore
            self.voices = None  # type: ignore
            self.histories = None  # type: ignore
            self.cloned_voices = None  # type: ignore
            self.tasks = None  # type: ignore

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        if self.database is None:
            raise RuntimeError("Database not connected.")
        return self.database[name]


mongodb = MongoDB()
