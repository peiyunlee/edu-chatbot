from db.models.m_hw_reflect import HWReflectModel, CreateHWReflect, RuleCheckModel
from db.database import db
from db import db_student
from fastapi.encoders import jsonable_encoder

collection_hr = db["homework_reflects"]
collection_rc = db["rule_check"]

def create_hw_reflects(reflect: CreateHWReflect, hw_no: int, student_id: str):
    reflect = jsonable_encoder(HWReflectModel(
            hw_no = hw_no,
            student_id = student_id,
            reflect1 = reflect.reflect1,
            reflect2 = reflect.reflect2,
            reflect3 = reflect.reflect3,
            reflect4 = reflect.reflect4,
            group_score = reflect.group_score,
            score = reflect.score
        ))
    new_reflect = collection_hr.insert_one(reflect)
    created_reflect = collection_hr.find_one({"_id": new_reflect.inserted_id})
    return created_reflect


def get_hw_reflect(hw_no: int, student_id: str):
    reflect = collection_hr.find_one({"hw_no": hw_no, "student_id":student_id})
    
    return reflect


def create_hw_rule_check(check: CreateHWReflect, hw_no: int, student_id: str):
    check = jsonable_encoder(RuleCheckModel(
            hw_no = hw_no,
            student_id = student_id,
            rule1_checked = check.rule1_checked,
            rule2_checked = check.rule2_checked,
            rule3_checked = check.rule3_checked
        ))
    new_check = collection_rc.insert_one(check)
    created_check = collection_rc.find_one({"_id": new_check.inserted_id})
    return created_check


def is_all_hw_reflect_completed(hw_no: int, line_user_id: str):
    students = db_student.get_group_members_by_student_line_UID(line_user_id=line_user_id)

    for student in students:
        reflect = collection_hr.find_one({"hw_no": hw_no, "student_id":student['_id']})
        if not reflect:
            return False
        
    return True
        

def get_hw_check(hw_no: str, student_id: str):
    check = collection_rc.find_one({"hw_no": hw_no, "student_id":student_id})
    return check