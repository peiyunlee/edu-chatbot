from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .model import PyObjectId

# ------------------------- Group
class GroupModel(BaseModel):
    group_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    line_group_id: str = Field(...)
    group_number: int = Field(...)
    isExperimental: bool = Field(...)
    hw1_checked: bool = Field(...)
    hw2_checked: bool = Field(...)
    hw3_checked: bool = Field(...)
    hw_no_now: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ------------------------- Student
class StudentModel(BaseModel):
    student_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    group_id: str = Field(...)
    line_user_id: str = Field(...)
    student_number: str = Field(...)
    name: str = Field(...)
    # email: EmailStr = Field(...)
    # email-validator==1.1.2

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}