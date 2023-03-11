from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .model import PyObjectId

# ------------------------- Homework
class HWModel(BaseModel):
    hw_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hw_no: int = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    rule1_title: str = Field(...)
    rule1_contents: list = Field(...)
    rule2_title: str = Field(...)
    rule2_contents: list = Field(...)
    rule3_title: str = Field(...)
    rule3_contents: list = Field(...)
    hand_over_date: str = Field(...)
    hand_over: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UpdateHWModel(BaseModel):
    hw_no: Optional[int] = Field(...)
    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    rule1_title: Optional[str] = Field(...)
    rule1_contents: Optional[list] = Field(...)
    rule2_title: Optional[str] = Field(...)
    rule2_contents: Optional[list] = Field(...)
    rule3_title: Optional[str] = Field(...)
    rule3_contents: Optional[list]= Field(...)
    hand_over_date: Optional[str] = Field(...)
    hand_over: Optional[str] = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}