from fastapi import APIRouter
from fastapi import Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db_student, db_task_reflect, db_task, db_remind
from router import linebot
from config import header
from db.models.m_task_reflect import CreateTaskReflect

router = APIRouter(
    prefix='/reflect/task',
    tags=['Reflect-Task']
)

@router.post("/create/{task_id}/LUID/{line_user_id}", summary="新增自己的工作反思")
def create_new_reflect(task_id: str, line_user_id: str, reflect: CreateTaskReflect):
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    task =  db_task.get_task_by_task_id(task_id=task_id)
    created_reflect = db_task_reflect.create_task_reflects(reflect=reflect,student_id=student['_id'],task_id=task_id)
    line_group_id = group['line_group_id']
    task_name = task['task_name']
    hand_over = task['hand_over']
    hand_over_date = task['hand_over_date']
    student_name = student['name']
    finish_date = task['finish_date']
    reflect1=created_reflect['reflect1']
    reflect2=created_reflect['reflect2']
    score=created_reflect['score']
    line_group_id = group['line_group_id']
    if created_reflect['is_self']:
        linebot.push_J(line_group_id=line_group_id, task_name=task_name, student_name=student_name, reflect1=reflect1, reflect2=reflect2, score=score, hand_over=hand_over, hand_over_date=hand_over_date, finish_date=finish_date, task_id=task_id, isExperimental=group['isExperimental'])
    if not created_reflect['is_self'] and group['isExperimental']:
        linebot.push_K(line_group_id=line_group_id, task_name=task_name, student_name=student_name, task_id=task_id)
    is_all_completed = db_task.is_group_all_task_is_all_completed(group_id=group['_id'],hw_no=task['hw_no'])
    if is_all_completed:
        linebot.push_L(line_group_id=line_group_id, isRemind=False)
        db_remind.create_remind_L(line_group_id=line_group_id, hw_no=group['hw_no_now'])
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.get("/{task_id}/student/{student_id}", summary="取得工作反思")
def get_reflect(task_id: str, student_id: str):
    reflect = db_task_reflect.get_task_reflect(task_id=task_id, student_id=student_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=reflect, headers=header)