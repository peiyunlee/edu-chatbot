from db.models.m_student import StudentModel, GroupModel
from db.database import db
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from db.models.model import PyObjectId

collection_group = db["groups"]
collection_student = db["students"]


# ----------------------------- group
def create_group(line_group_id: str):
    old_group = collection_group.find_one({"line_group_id": line_group_id})

    if old_group is not None:
        print("group exist")
        return old_group
    else:

        new_group = jsonable_encoder(GroupModel(
            line_group_id=line_group_id,
            group_number=collection_group.count_documents({})+1,
            isExperimental=False,
            hw1_checked=False,
            hw2_checked=False,
            hw3_checked=False
        ))

        new_group = collection_group.insert_one(new_group)
        created_group = collection_group.find_one({"_id": new_group.inserted_id})
    
        return created_group

# ----------------------------- student
def create_student(line_user_id:str ,student_number:str, student_name:str, line_group_id:str):
    old_student = collection_student.find_one({"line_user_id": line_user_id})

    group = get_group_by_line_GID(line_group_id=line_group_id)
    group_id = group['group_id']
    
    if old_student is not None:
        print("student exist")
        # 修改 student資訊
        update_student(line_user_id= line_user_id ,student_number= student_number, student_name= student_name, group_id=group_id)
        return old_student
    else:

        new_student = jsonable_encoder(StudentModel(
            group_id=group_id,
            line_user_id=line_user_id,
            student_number=student_number,
            name=student_name,
        ))

        new_student = collection_student.insert_one(new_student)
        created_student = collection_student.find_one({"_id": new_student.inserted_id})

        print("create new student")
        return created_student

def update_student(line_user_id:str ,student_number:str, student_name:str, group_id:PyObjectId):
    student = collection_student.update_one({
        "line_user_id": line_user_id
    },{
        "$set":{
            "group_id":group_id,
            "line_user_id":line_user_id,
            "student_number":student_number,
            "name":student_name,
        }
    })

    print("update student group")
    return student


# ----------------------------- group
def get_group_by_line_GID(line_group_id: str):
    group = collection_group.find_one({"line_group_id": line_group_id})

    if group is not None:
        return group
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到group")