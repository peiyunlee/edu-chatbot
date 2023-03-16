from db.models.m_task import TaskModel, CreateTaskModel
from db.database import db
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status

collection_task = db["tasks"]


# ----------------------------- task
def create_task(task: CreateTaskModel, group_id: str):    
    task = jsonable_encoder(TaskModel(
            student_id='',
            group_id=group_id,
            hw_no=task.hw_no,
            task_name=task.task_name,
            plan=task.plan,
            hand_over_date=task.hand_over_date,
            hand_over=task.hand_over,
            finish_date='',
            is_finish=False,
        ))
    new_task = collection_task.insert_one(task)
    created_task = collection_task.find_one({"_id": new_task.inserted_id})
    return created_task


# ----------------------------- claim
def claim_task(task_id: str, student_id: str):
    task = collection_task.update_one({"_id":task_id, "student_id": ''},{"$set": {"student_id": student_id}})

    if task is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"此工作已經有人認領")


# ----------------------------- complete
def complete_task(task_id: str, finish_date: str):
    task = collection_task.update_one({"_id":task_id},{"$set": {"is_finish": True, "finish_date": finish_date}})
    task = collection_task.find_one({"_id": task_id})

    return task


def get_task_by_task_id(task_id: str):
    task = collection_task.find_one({"_id": task_id})
    return task


def get_group_all_task_by_hw_id(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id, "hw_no": hw_no})
    
    return list(tasks)


def is_group_all_task_is_all_claimed(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id, "hw_no": hw_no, "student_id": ''})
    tasks = list(tasks)

    if len(tasks) == 0:
        # 都認領完
        return True
    else:
        return False


def is_group_all_task_is_all_completed(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id, "hw_no": hw_no, "is_finish": False})
    tasks = list(tasks)

    if len(tasks) == 0:
        # 都完成了
        return True
    else:
        return False


import datetime

def get_group_all_coming_task(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id, "hw_no": hw_no, "is_finish": False, "hand_over_date": (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%m/%d')})
    tasks = list(tasks)
    return tasks


def update_task(task_id:str ,task_name: str, hand_over: str, plan: str, hand_over_date: str):
    task = collection_task.update_one({
        "_id": task_id
    },{
        "$set":{
            "task_name":task_name,
            "plan":plan,
            "hand_over":hand_over,
            "hand_over_date":hand_over_date,
        }
    })

    print("update task")
    return task 

def delete_task_by_task_id(task_id: str):
    task = collection_task.delete_one({'_id':task_id})