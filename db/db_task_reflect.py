from db.models.m_task import TaskModel
from db.database import db
from fastapi.encoders import jsonable_encoder

collection_tr = db["task_reflects"]


# ----------------------------- group
def create_task(task: TaskModel):
    task = jsonable_encoder(task)
    new_task = collection_task.insert_one(task)
    created_task = collection_task.find_one({"_id": new_task.inserted_id})
    return created_task
    
def get_group_all_task(group_id: str):
    tasks = collection_task.find({"group_id": group_id})
    return tasks

def get_group_all_task_by_hw_id(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id},{"hw_no": hw_no})
    return tasks

def is_group_all_task_is_all_claimed(group_id: str, hw_no: int):
    tasks = collection_task.find({"group_id": group_id},{"hw_no": hw_no},{"is_claimed": False})

    if len(tasks) == 0:
        # 都認領完
        return True
    else:
        return False
    
# def get_all_hw():
#     hws = list(collection_hw.find({}).sort('hw_no',1))
#     return hws
    
# def replace_hw(hw: UpdateHWModel):
#     hw = jsonable_encoder(hw)
#     replaced_hw = collection_hw.replace_one({
#         "hw_no": hw['hw_no']
#     },hw)

#     print(f"replace hw: {hw['hw_no']}")
#     return replaced_hw