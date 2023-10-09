from pydantic import BaseModel
from typing import Generic, TypeVar
from uuid import UUID


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    message: str
    data: T | None


class BaseResponseWithUUID(BaseResponse):
    session_id: UUID
