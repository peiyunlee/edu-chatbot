from db.models.m_hw import HWModel, UpdateHWModel
from db.database import db
from fastapi.encoders import jsonable_encoder

collection_hw = db["homeworks"]


# ----------------------------- group
def create_hw(hw: HWModel):
    hw = jsonable_encoder(hw)
    old_hw = collection_hw.find_one({"hw_no": hw['hw_no']})

    if old_hw:
        print("HW exist")
        new_hw = replace_hw(hw=hw)
        return new_hw
    else:
        new_hw = collection_hw.insert_one(hw)
        created_hw = collection_hw.find_one({"_id": new_hw.inserted_id})
        return created_hw
    
def replace_hw(hw: UpdateHWModel):
    hw = jsonable_encoder(hw)
    replaced_hw = collection_hw.replace_one({
        "hw_no": hw['hw_no']
    },hw)

    print(f"replace hw: {hw['hw_no']}")
    return replaced_hw
    
def get_hw_by_hw_no(hw_no: int):
    hw = collection_hw.find_one({"hw_no": hw_no})
    return hw
    
def get_all_hw():
    hws = list(collection_hw.find({}).sort('hw_no',1))
    return hws