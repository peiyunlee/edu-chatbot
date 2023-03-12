from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .model import PyObjectId


class TaskReflectModel(BaseModel):
    tr_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    task_id: str = Field(...)
    student_id: str = Field(...)
    reflect1: str = Field(...)
    reflect2: str = Field(...)
    score: int = Field(...)
    is_self: bool = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateTaskReflect(BaseModel):
    reflect1: str = Field(...)
    reflect2: str = Field(...)
    score: int = Field(...)
    is_self: bool = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}