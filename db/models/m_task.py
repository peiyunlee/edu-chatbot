from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .model import PyObjectId

# ------------------------- Homework
class TaskModel(BaseModel):
    task_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    student_id: str = Field(...)
    group_id: str = Field(...)
    hw_no: int = Field(...)
    task_name: str = Field(...)
    plan: str = Field(...)
    hand_over_date: str = Field(...)
    hand_over: str = Field(...)
    is_finish: bool = Field(...)
    finish_date: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CreateTaskModel(BaseModel):
    hw_no: int = Field(...)
    task_name: str = Field(...)
    plan: str = Field(...)
    hand_over_date: str = Field(...)
    hand_over: str = Field(...)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UpdateTaskModel(BaseModel):
    task_name: str = Field(...)
    plan: str = Field(...)
    hand_over_date: str = Field(...)
    hand_over: str = Field(...)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}