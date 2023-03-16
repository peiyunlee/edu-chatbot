from db.database import db
from router import scheduler


collection_remind_A = db["remind_A"]
collection_remind_B = db["remind_B"]


def create_remind_A(line_group_id: str):
    old_remind = collection_remind_A.find_one({"line_group_id": line_group_id})

    if old_remind:
        print("remind exist")
        return old_remind
    else:
        new_remind = {
            "line_group_id": line_group_id
        }

        new_remind = collection_remind_A.insert_one(new_remind)
        created_remind = collection_remind_A.find_one({"_id": new_remind.inserted_id})
    
        return created_remind
    
def delete_remind_A(line_group_id: str):
    remind = collection_remind_A.delete_one({'line_group_id': line_group_id})

    if collection_remind_A.count_documents({}) == 0:
        scheduler.remove_remind('A')
    
def get_all_remind_A():
    groups = collection_remind_A.find()
    return groups

def create_remind_B(line_group_id: str):
    old_remind = collection_remind_B.find_one({"line_group_id": line_group_id})

    if old_remind:
        print("remind exist")
        return old_remind
    else:
        new_remind = {
            "line_group_id": line_group_id
        }

        new_remind = collection_remind_B.insert_one(new_remind)
        created_remind = collection_remind_B.find_one({"_id": new_remind.inserted_id})
    
        return created_remind
    
def delete_remind_B(line_group_id: str):
    remind = collection_remind_B.delete_one({'line_group_id': line_group_id})

    if collection_remind_B.count_documents({}) == 0:
        scheduler.remove_remind('B')
    
def get_all_remind_B():
    groups = collection_remind_B.find()
    return groups
