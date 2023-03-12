from db.models.m_task_reflect import CreateTaskReflect, TaskReflectModel
from db.database import db
from fastapi.encoders import jsonable_encoder

collection_tr = db["task_reflects"]

def create_task_reflects(reflect: CreateTaskReflect, task_id: str, student_id: str):
    reflect = jsonable_encoder(TaskReflectModel(
            task_id = task_id,
            student_id = student_id,
            reflect1 = reflect.reflect1,
            reflect2 = reflect.reflect2,
            score = reflect.score,
            is_self = reflect.is_self
        ))
    new_reflect = collection_tr.insert_one(reflect)
    created_reflect = collection_tr.find_one({"_id": new_reflect.inserted_id})
    return created_reflect


def get_task_reflect(task_id: str, student_id: str):
    reflect = collection_tr.find_one({"task_id": task_id, "student_id":student_id})
    return reflect

def get_task_all_reflect(task_id: str):
    reflects = collection_tr.find({"task_id": task_id})
    return reflects