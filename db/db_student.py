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

    if old_group:
        print("group exist")
        return old_group
    else:

        new_group = jsonable_encoder(GroupModel(
            line_group_id=line_group_id,
            group_number=collection_group.count_documents({})+1,
            isExperimental=False,
            hw1_checked=False,
            hw2_checked=False,
            hw3_checked=False,
            hw_no_now=1
        ))

        new_group = collection_group.insert_one(new_group)
        created_group = collection_group.find_one({"_id": new_group.inserted_id})
    
        return created_group

def get_all_group():
    groups = collection_group.find()
    return groups

def update_group_hw_no_now(group_id:str, hw_no_now: int):
    group = collection_group.update_one({
        "_id": group_id
    },{
        "$set":{
            "hw_no_now": hw_no_now + 1 ,
        }
    })

    print("update group hwno_now")
    return group

# ----------------------------- student
def create_student(line_user_id:str ,student_number:str, student_name:str, line_group_id:str):
    old_student = collection_student.find_one({"line_user_id": line_user_id})

    group = get_group_by_line_GID(line_group_id=line_group_id)
    group_id = group['_id']
    
    if old_student:
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

def update_student(line_user_id:str ,student_number:str, student_name:str, group_id:str):
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

def get_student_by_line_UID(line_user_id: str):
    student = collection_student.find_one({"line_user_id": line_user_id})

    if student:
        return student
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到student")
    
def get_student_by_student_id(student_id: str):
    student = collection_student.find_one({"_id": student_id})

    if student:
        return student
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到student")

def get_group_members_by_student_line_UID(line_user_id: str):
    student = collection_student.find_one({"line_user_id": line_user_id})

    if student:
        group_id = student['group_id']
        students = collection_student.find({"group_id": group_id})
    
        return list(students)
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到student")


# ----------------------------- group
def get_group_by_group_id(group_id: str):
    group = collection_group.find_one({"_id": group_id})

    if group:
        return group
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到group")

def get_group_by_line_GID(line_group_id: str):
    group = collection_group.find_one({"line_group_id": line_group_id})

    if group:
        return group
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到group")
    
def get_group_by_student_line_UID(line_user_id: str):
    student = collection_student.find_one({"line_user_id": line_user_id})

    if student:
        group = collection_group.find_one({"_id": student['group_id']})

        if group:
            return group
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"找不到group")
        
    else:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"找不到student")

def update_all_group_hw_no_now(hw_no_now:int):
    collection_group.update_many({},{
        "$set":{
            "hw_no_now":hw_no_now,
        }
    })

def update_group_hw_check(group_id:str, hw_no: int):
    collection_group.update_one({"_id": group_id},{
        "$set":{
            f"hw{hw_no}_checked":True,
        }
    })