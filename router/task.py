from fastapi import APIRouter
from fastapi import Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db_task, db_student, db_remind
from router import linebot
from config import header
from db.models.m_task import CreateTaskModel, UpdateTaskModel

router = APIRouter(
    prefix='/task',
    tags=['Task']
)

@router.post("/create/LUID/{line_user_id}", summary="新增和推播新增任務")
def create_new_task(line_user_id: str, task: CreateTaskModel):
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    created_task = db_task.create_task(task=task, group_id=student['group_id'])
    db_remind.delete_remind_B(line_group_id=group['line_group_id'], hw_no=group['hw_no_now'])
    db_remind.create_remind_C(line_group_id=group['line_group_id'], hw_no=group['hw_no_now'])
    db_remind.delete_remind_L(line_group_id=group['line_group_id'], hw_no=group['hw_no_now'])
    push_create_new_task(line_user_id= line_user_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


def push_create_new_task(line_user_id: str):
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    line_group_id = group['line_group_id']
    linebot.push_D(line_group_id=line_group_id, group_id=group['_id'], hw_no=group['hw_no_now'])

# ----------------------------------- claim

@router.post("/claim/LUID/{line_user_id}/id/{task_id}", summary="認領任務")
def claim_task(line_user_id: str, task_id: str):
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    db_task.claim_task(task_id=task_id, student_id=student['_id'])
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    task = db_task.get_task_by_task_id(task_id=task_id)
    task_name = task['task_name']
    hw_no = task['hw_no']
    student_name = student['name']
    group_id  = group['_id']
    line_group_id = group['line_group_id']
    db_remind.delete_remind_C(line_group_id=group['line_group_id'], hw_no=hw_no)
    push_claim_task(task_name=task_name, hw_no=hw_no, student_name=student_name, group_id=group_id, line_group_id=line_group_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.get("/LUID/{line_user_id}/hw_no/{hw_no}/all", summary="取得該階段所有任務")
def get_hw_all_task(line_user_id: str, hw_no: int):
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    tasks = db_task.get_group_all_task_by_hw_id(group_id=group['_id'], hw_no=hw_no)

    return JSONResponse(status_code=status.HTTP_200_OK, content=tasks, headers=header)


@router.get("/id/{task_id}", summary="取得任務資訊")
def get_task_by_task_id(task_id: str):
    task = db_task.get_task_by_task_id(task_id=task_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=task, headers=header)


@router.patch("/id/{task_id}/LUID/{line_user_id}", summary="編輯任務")
def update_task_by_task_id(task_id: str, task: UpdateTaskModel , line_user_id: str):
    task = jsonable_encoder(task)
    db_task.update_task(task_id=task_id, task_name=task['task_name'],plan=task['plan'], hand_over=task['hand_over'], hand_over_date=task['hand_over_date'])
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    is_all_completed = db_task.is_group_all_task_is_all_completed(group_id=group['_id'],hw_no=group['hw_no_now'])
    linebot.push_R(line_group_id=group['line_group_id'], line_user_id=line_user_id, task_name=task['task_name'], student_name=student['name'], group_id=group['_id'], action='編輯', is_all_completed=is_all_completed, hw_no=group['hw_no_now'])
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.delete("/id/{task_id}/LUID/{line_user_id}", summary="刪除任務")
def delete_task_by_task_id(task_id: str, line_user_id: str):
    task = db_task.get_task_by_task_id(task_id=task_id)
    db_task.delete_task_by_task_id(task_id=task_id)
    student = db_student.get_student_by_line_UID(line_user_id=line_user_id)
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    is_all_completed = db_task.is_group_all_task_is_all_completed(group_id=group['_id'],hw_no=group['hw_no_now'])
    if is_all_completed:
        db_remind.delete_remind_C(line_group_id=group['line_group_id'], hw_no=group['hw_no_now'])
    linebot.push_R(line_group_id=group['line_group_id'], line_user_id=line_user_id,task_name=task['task_name'], student_name=student['name'], group_id=group['_id'], action='刪除', is_all_completed=is_all_completed, hw_no=group['hw_no_now'])
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.post("/complete/id/{task_id}/date/{month}/{day}", summary="完成任務")
def complete_task_by_task_id(task_id: str, month: str, day: str):
    task = db_task.complete_task(task_id=task_id, finish_date=f"{month}/{day}")
    student = db_student.get_student_by_student_id(student_id=task['student_id'])
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


# @router.post("/broadcast1/pause", summary="定時推播")
# def pause_broadcast1():
#     scheduler1.pause()
#     return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)

# @router.post("/broadcast2/pause", summary="定時推播")
# def pause_broadcast2():
#     scheduler2.pause()
#     return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


# ----------------------------------- claim function

def push_claim_task(task_name: str, hw_no: int, student_name: str, group_id: str, line_group_id: str):
    is_all_claimed = db_task.is_group_all_task_is_all_claimed(group_id=group_id, hw_no=hw_no)
    if is_all_claimed:
        # 全部都認領完
        linebot.push_G(line_group_id=line_group_id, group_id=group_id, hw_no=hw_no)
    else:
        linebot.push_F(line_group_id=line_group_id,task_name=task_name, student_name=student_name, group_id=group_id, hw_no=hw_no)