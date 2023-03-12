from fastapi import APIRouter
from fastapi import Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db_hw_reflect, db_student
from router import linebot
from config import header
from db.models.m_hw_reflect import CreateHWReflect

router = APIRouter(
    prefix='/reflect/homework',
    tags=['Reflect-Homework']
)

@router.post("/create/hw_no/{hw_no}/LUID/{line_user_id}", summary="新增作業查核與反思")
def create_new_reflect(hw_no: int, line_user_id: str, reflect: CreateHWReflect):
    print(hw_no)
    print(line_user_id)
    print(reflect)
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    # group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    created_reflect = db_hw_reflect.create_hw_reflects(reflect=reflect, hw_no=hw_no, student_id=student['_id'])
    created_check = db_hw_reflect.create_hw_rule_check(check=reflect, hw_no=hw_no, student_id=student['_id'])
    # if created_reflect['is_self']:
    #     linebot.push_J(line_group_id=line_group_id, task_name=task_name, student_name=student_name, reflect1=reflect1, reflect2=reflect2, score=score, hand_over=hand_over, hand_over_date=hand_over_date, finish_date=finish_date, task_id=task_id)
    # else:
    #     linebot.push_K(line_group_id=line_group_id, task_name=task_name, student_name=student_name, task_id=task_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.get("/hw_no/{hw_no}/id/{student_id}", summary="取得作業反思")
def get_hw_reflect(hw_no: int, student_id: str):
    reflect = db_hw_reflect.get_hw_reflect(hw_no=hw_no, student_id=student_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=reflect, headers=header)

@router.get("/check/hw_no/{hw_no}/id/{student_id}", summary="取得作業檢查")
def get_hw_check(hw_no: int, student_id: str):
    check = db_hw_reflect.get_hw_check(hw_no=hw_no, student_id=student_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=check, headers=header)