from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from db.database import client
from db import db_student, db_remind
from router import linebot
from config import DB_NAME
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
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


@router.post("/broadcast/pause", summary="暫停每日提醒")
def pause_broadcast():
    remove_broadcast_task()
    return JSONResponse(status_code=status.HTTP_200_OK, content="success", headers=header)


def add_broadcast_task():
    if not scheduler_broadcast.get_job('broadcast_task'):
        scheduler_broadcast.add_job(broadcast_task, 'cron', day_of_week='0-6', hour=10, minute=0, id='broadcast_task')

def broadcast_task():
    groups = db_student.get_all_group()

    for group in groups:
        linebot.push_S(group_id=group['_id'], hw_no=group['hw_no_now'], line_group_id=group['line_group_id'])

def remove_broadcast_task():
    if scheduler_broadcast.get_job("broadcast_task"):
        scheduler_broadcast.remove_job("broadcast_task")


def add_remind_A():
    if not scheduler_remind.get_job('remind_A'):
        scheduler_remind.add_job(remind_A, 'interval', hours=6, id='remind_A')

def remind_A():
    groups = db_remind.get_all_remind_A()

    for group in groups:
        linebot.push_U(line_group_id=group['line_group_id'])

def add_remind_B():
    if not scheduler_remind.get_job('remind_B'):
        #test
        scheduler_remind.add_job(remind_B, 'interval', seconds=20, id='remind_B')
        # scheduler_remind.add_job(remind_B, 'interval', hours=6, id='remind_B')

def remind_B():
    groups_b = db_remind.get_all_remind_B()

    for group_b in groups_b:
        group = db_student.get_group_by_line_GID(line_group_id=group_b['line_group_id'])
        linebot.push_B_with_remind(line_group_id=group['line_group_id'], hw_no_now=group['hw_no_now'])

def remove_remind(type: str):
    if scheduler_remind.get_job(f"remind_{type}"):
        scheduler_remind.remove_job(f"remind_{type}")


scheduler_broadcast = BackgroundScheduler(timezone="Asia/Taipei")
# scheduler.add_jobstore(job_stores[f'{DB_NAME}-broadcast'])
scheduler_broadcast.start()

scheduler_remind = BackgroundScheduler(timezone="Asia/Taipei")
scheduler_remind.start()

# scheduler.add_job(job1, 'interval', seconds=5, args=['cc'])
# scheduler.add_job(broadcast_task, 'interval', seconds=5, id='broadcast_task')