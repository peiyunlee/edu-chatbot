from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from db.database import client
from db import db_student, db_remind, db_hw
from router import linebot
from config import DB_NAME, SCHEDULER_TEST, HOUR, HOUR_REMIND, MINUTES, MINUTES_REMIND
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status
from config import header


router = APIRouter(
    prefix='/scheduler',
    tags=['Scheduler']
)

job_stores = {
    f'{DB_NAME}-broadcast': MongoDBJobStore(database=f"{DB_NAME}-broadcast", client=client),
    f'{DB_NAME}-remind': MongoDBJobStore(database=f"{DB_NAME}-remind", client=client),
}

@router.post("/restart/all", summary="更新程式的話重啟每日提醒")
def restart_all():
    add_broadcast_task()
    add_remind_A()
    add_remind_B()
    add_remind_C()
    add_remind_L()
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.post("/broadcast/task/pause", summary="暫停每日提醒")
def pause_broadcast_task():
    scheduler_broadcast_task.pause()
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)

@router.post("/broadcast/hw/pause", summary="暫停功課繳交提醒")
def pause_broadcast_hw():
    scheduler_broadcast_hw.pause()
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.post("/remind/pause", summary="暫停remind")
def pause_remind():
    scheduler_remind.pause()
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


def add_broadcast_task():
    if not scheduler_broadcast_task.get_job('broadcast_task'):
        scheduler_broadcast_task.add_job(broadcast_task, 'cron', day_of_week='0-6', hour=int(HOUR), minute=int(MINUTES), id='broadcast_task')

def broadcast_task():
    groups = db_student.get_all_group()

    for group in groups:
        linebot.push_S(group_id=group['_id'], hw_no=group['hw_no_now'], line_group_id=group['line_group_id'])

def remove_broadcast_task():
    if scheduler_broadcast_task.get_job("broadcast_task"):
        scheduler_broadcast_task.remove_job("broadcast_task")

from datetime import timedelta

def add_remind_A():
    if not scheduler_remind.get_job('remind_A'):
        scheduler_remind.add_job(remind_A, 'cron', day_of_week='0-6', hour=int(HOUR_REMIND), minute=int(MINUTES_REMIND), id='remind_A')

def remind_A():
    groups = db_remind.get_all_remind_A()

    for group in groups:
        linebot.push_U(line_group_id=group['line_group_id'])

def add_remind_B():
    if not scheduler_remind.get_job('remind_B'):
       scheduler_remind.add_job(remind_B, 'cron', day_of_week='0-6', hour=int(HOUR_REMIND), minute=int(MINUTES_REMIND), id='remind_B')


def remind_B():
    groups_b = db_remind.get_all_remind_B()

    for group_b in groups_b:
        group = db_student.get_group_by_line_GID(line_group_id=group_b['line_group_id'])
        linebot.push_B_with_remind(line_group_id=group['line_group_id'], hw_no_now=group['hw_no_now'])

def add_remind_C():
    if not scheduler_remind.get_job('remind_C'):
        scheduler_remind.add_job(remind_C, 'cron', day_of_week='0-6', hour=int(HOUR_REMIND), minute=int(MINUTES_REMIND), id='remind_C')

def remind_C():
    groups_c = db_remind.get_all_remind_C()
    print("remind C")

    for group_c in groups_c:
        group = db_student.get_group_by_line_GID(line_group_id=group_c['line_group_id'])
        linebot.push_C(line_group_id= group['line_group_id'], group_id= group['_id'], hw_no= group['hw_no_now'])

def add_remind_L():
    if not scheduler_remind.get_job('remind_L'):
        scheduler_remind.add_job(remind_L, 'cron', day_of_week='0-6', hour=int(HOUR_REMIND), minute=int(MINUTES_REMIND), id='remind_L')

def remind_L():
    groups_l = db_remind.get_all_remind_L()

    for group_l in groups_l:
        linebot.push_L(line_group_id=group_l['line_group_id'], isRemind=True)

def remove_remind(type: str):
    if scheduler_remind.get_job(f"remind_{type}"):
        scheduler_remind.remove_job(f"remind_{type}")

import datetime

def add_broadcast_hw():
    homeworks = db_hw.get_all_hw()
    
    for hw in homeworks:
        date = hw['hand_over_date'].split('/')
        if not scheduler_broadcast_hw.get_job(f"broadcast_hw_{hw['hw_no']}"):
            scheduler_broadcast_hw.add_job(broadcast_hw, 'date', run_date=datetime.date(2023,int(date[0]), int(date[1]),), id=f"broadcast_hw_{hw['hw_no']}", args=[hw['hw_no']])


def broadcast_hw(hw_no):
    groups = db_student.get_all_group()

    for group in groups:
        if group['hw_no_now'] == hw_no:
            linebot.push_remind_hw(line_group_id=group['line_group_id'], hw_no=hw_no)


scheduler_broadcast_task = BackgroundScheduler(timezone="Asia/Taipei")
scheduler_broadcast_task.start()

scheduler_remind = BackgroundScheduler(timezone="Asia/Taipei")
add_remind_B()
add_remind_C()
add_remind_L()
scheduler_remind.start()

scheduler_broadcast_hw = BackgroundScheduler(timezone="Asia/Taipei")
add_broadcast_hw()
scheduler_broadcast_hw.start()

# scheduler.add_jobstore(job_stores[f'{DB_NAME}-broadcast'])
# scheduler.add_job(job1, 'interval', seconds=5, args=['cc'])
# scheduler.add_job(broadcast_task, 'interval', seconds=5, id='broadcast_task')