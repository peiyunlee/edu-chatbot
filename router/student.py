from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse
from db import db_student
from config import header

router = APIRouter(
    prefix='/student',
    tags=['Student']
)

@router.get("/group/all/LUID/{line_user_id}", summary="取得所有群組成員(by其中一人的LUID)")
def get_all_group_members_by_LUID(line_user_id: str):
    members = db_student.get_group_members_by_student_line_UID(line_user_id=line_user_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=members, headers=header)


@router.get("/LUID/{line_user_id}", summary="取得學生")
def get_student_by_LUID(line_user_id: str):
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=student, headers=header)



@router.get("/id/{student_id}", summary="取得學生")
def get_student_by_id(student_id: str):
    student = db_student.get_student_by_student_id(student_id= student_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=student, headers=header)