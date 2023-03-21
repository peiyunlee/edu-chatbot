from db.database import db
from router import scheduler


collection_remind_A = db["remind_A"]
collection_remind_B = db["remind_B"]
collection_remind_C = db["remind_C"]
collection_remind_L = db["remind_L"]


# ------------------------------ A

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


def get_remind_A(line_group_id: str):
    remind = collection_remind_A.find_one({'line_group_id': line_group_id})

    return remind

# ------------------------------ B

def create_remind_B(line_group_id: str, hw_no: int):
    old_remind = collection_remind_B.find_one({"line_group_id": line_group_id, 'hw_no': hw_no})

    if old_remind:
        print("remind exist")
        return old_remind
    else:
        new_remind = {
            "line_group_id": line_group_id,
            "hw_no": hw_no
        }

        new_remind = collection_remind_B.insert_one(new_remind)
        created_remind = collection_remind_B.find_one({"_id": new_remind.inserted_id})
    
        return created_remind
    
def delete_remind_B(hw_no: int, line_group_id: str or None = None):
    if line_group_id:
        remind = collection_remind_B.delete_one({'line_group_id': line_group_id, 'hw_no':hw_no})
    else:
        remind = collection_remind_B.delete_one({'hw_no': hw_no})

    if collection_remind_B.count_documents({}) == 0:
        scheduler.remove_remind('B')
    
def get_all_remind_B():
    groups = collection_remind_B.find()
    return groups


def get_remind_B(line_group_id: str, hw_no: int):
    remind = collection_remind_B.find_one({'line_group_id': line_group_id, 'hw_no': hw_no})

    return remind

# ------------------------------ C

def create_remind_C(line_group_id: str, hw_no: int):
    old_remind = collection_remind_C.find_one({"line_group_id": line_group_id, 'hw_no': hw_no})

    if old_remind:
        print("remind exist")
        return old_remind
    else:
        new_remind = {
            "line_group_id": line_group_id,
            "hw_no": hw_no
        }

        new_remind = collection_remind_C.insert_one(new_remind)
        created_remind = collection_remind_C.find_one({"_id": new_remind.inserted_id})
    
        return created_remind
    
def delete_remind_C(hw_no: int, line_group_id: str or None = None ):
    if line_group_id:
        remind = collection_remind_C.delete_one({'line_group_id': line_group_id, 'hw_no': hw_no})
    else:
        remind = collection_remind_C.delete_one({'hw_no': hw_no})

    if collection_remind_C.count_documents({}) == 0:
        scheduler.remove_remind('C')
    
def get_all_remind_C():
    groups = collection_remind_C.find()
    return groups


def get_remind_C(line_group_id: str, hw_no: int):
    remind = collection_remind_C.find_one({'line_group_id': line_group_id, 'hw_no': hw_no})

    return remind


# ------------------------------ L

def create_remind_L(line_group_id: str, hw_no: int):
    old_remind = collection_remind_L.find_one({"line_group_id": line_group_id, 'hw_no': hw_no})

    if old_remind:
        print("remind exist")
        return old_remind
    else:
        new_remind = {
            "line_group_id": line_group_id,
            "hw_no": hw_no
        }

        new_remind = collection_remind_L.insert_one(new_remind)
        created_remind = collection_remind_L.find_one({"_id": new_remind.inserted_id})
    
        return created_remind
    
def delete_remind_L(hw_no: int, line_group_id: str or None = None ):
    if line_group_id:
        remind = collection_remind_L.delete_one({'line_group_id': line_group_id, 'hw_no': hw_no})
    else:
        remind = collection_remind_L.delete_one({'hw_no': hw_no})

    if collection_remind_L.count_documents({}) == 0:
        scheduler.remove_remind('L')
    
def get_all_remind_L():
    groups = collection_remind_L.find()
    return groups


def get_remind_L(line_group_id: str, hw_no: int):
    remind = collection_remind_L.find_one({'line_group_id': line_group_id, 'hw_no': hw_no})

    return remind

def delete_all_remind(hw_no: int):
    delete_remind_L(hw_no=hw_no)
    delete_remind_C(hw_no=hw_no)
    delete_remind_B(hw_no=hw_no)

