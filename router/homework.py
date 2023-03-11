from fastapi import APIRouter
from fastapi import Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db_hw, db_student
from db.models.m_hw import HWModel
from router import linebot
from config import header

router = APIRouter(
    prefix='/homework',
    tags=['Homework']
)

@router.post("/push/all", summary="推播期中作業規範")
def push_all_hw_announcement():
    homeworks = db_hw.get_all_hw()
    all_groups = db_student.get_all_group()
    linebot.push_A(homeworks=homeworks, all_groups=all_groups )
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)

@router.post("/create/{hw_no}", summary="新增階段作業")
def create_hw(hw: HWModel = Body(...)):
    hw = jsonable_encoder(hw)
    created_hw = db_hw.create_hw(hw=hw)
    print(created_hw)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_hw, headers=header)

@router.get("/hw_no/{hw_no}", summary="根據階段編號取得作業規範")
def get_hw_by_hw_no(hw_no: int):
    hw = db_hw.get_hw_by_hw_no(hw_no=hw_no)
    return JSONResponse(status_code=status.HTTP_200_OK, content=hw, headers=header)

@router.get("/all", summary="取得所有作業規範")
def get_all_hw():
    hw = db_hw.get_all_hw()
    print(hw)
    return JSONResponse(status_code=status.HTTP_200_OK, content=hw, headers=header)