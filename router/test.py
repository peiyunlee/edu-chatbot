from fastapi import APIRouter
from fastapi import Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db.database import db
from db.models.m_student import StudentModel
from config import header

router = APIRouter(
    prefix='/test',
    tags=['test']
)

@router.post("/", response_description="Add new student", response_model=StudentModel)
def create_student(student: StudentModel = Body(...)):
    student = jsonable_encoder(student)
    new_student = db["students"].insert_one(student)
    created_student = db["students"].find_one({"_id": new_student.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student, headers=header)