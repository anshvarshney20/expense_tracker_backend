from typing import Any, Generic, Sequence, Type, TypeVar
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncIOMotorDatabase):
        self.model = model
        self.db = db
        self.collection_name = getattr(model, "__tablename__", model.__name__.lower())
        self.collection = self.db[self.collection_name]

    async def get(self, id: uuid.UUID) -> ModelType | None:
        doc = await self.collection.find_one({"id": str(id)})
        if doc:
            return self.model(**doc)
        return None

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        cursor = self.collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in docs]

    def _prepare_data(self, data: Any) -> Any:
        from datetime import date, datetime
        from decimal import Decimal
        import uuid

        if isinstance(data, dict):
            return {k: self._prepare_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_data(v) for v in data]
        elif isinstance(data, (uuid.UUID, date)):
            if isinstance(data, datetime):
                return data  # Keep as datetime object for MongoDB
            if isinstance(data, date):
                return datetime.combine(data, datetime.min.time())
            return str(data)
        elif isinstance(data, Decimal):
            return float(data)
        return data

    async def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        # 1. Validate and create instance (adds id, created_at, etc)
        instance = self.model(**obj_in)
        
        # 2. Convert to MongoDB-friendly data
        data = self._prepare_data(instance.model_dump())
            
        await self.collection.insert_one(data)
        return instance

    async def update(
        self, *, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        obj_id = str(db_obj.id)
        
        # Prepare update data
        mongo_update_data = self._prepare_data(obj_in)
        
        await self.collection.update_one({"id": obj_id}, {"$set": mongo_update_data})
        doc = await self.collection.find_one({"id": obj_id})
        return self.model(**doc)

    async def remove(self, *, id: uuid.UUID) -> ModelType | None:
        obj_id = str(id)
        doc = await self.collection.find_one({"id": obj_id})
        if doc:
            await self.collection.delete_one({"id": obj_id})
            return self.model(**doc)
        return None
