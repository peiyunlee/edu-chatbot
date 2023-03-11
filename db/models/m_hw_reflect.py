from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .model import PyObjectId


class HWReflectModel(BaseModel):
    hwr_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    student_id: str = Field(...)
    hw_no: int = Field(...)
    reflect1: str = Field(...)
    reflect2: str = Field(...)
    reflect3: str = Field(...)
    reflect4: str = Field(...)
    group_score: int = Field(...)
    score: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}