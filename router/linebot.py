from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from fastapi import APIRouter, HTTPException, Request
import json

from config import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, header
from db import db_student
from message.manage_other import get_welcome_flex_messages
from message.manage import get_flex_messages, MessageId


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

router = APIRouter(
    prefix='/linebot',
    tags=['linebot']
)

# ----------------------------- Webhook 驗證功能
@router.post('/callback')
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    # get request body as text
    body = await request.body()
    body = body.decode()

    # handle webhook body
    try:
        handler.handle(body, signature)
        data = json.loads(body)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter",headers=header)
    return "Success"


# ----------------------------- 監聽回覆事件
@handler.add(MessageEvent, message=TextMessage)
def handle_group_reply_message(event):
    # 在群組內發送
    if event.source.type is "group":
        handle_group_reply_message(event)
    # 在官方帳號內發送
    else:
        pass


# ----------------------------- 監聽機器人加入群組事件
@handler.add(JoinEvent)
def handle_join_event_reply_message(event):
    print("機器人加入群組")

    line_group_id = event.source.group_id

    #新增群組
    new_group = db_student.create_group(line_group_id=line_group_id)
    group_number = new_group['group_number']

    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=0))
    line_bot_api.push_message(to=line_group_id, messages=TextSendMessage(text=f"你們的小組編號是{group_number}號"))
    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=1))


# ----------------------------- 監聽成員加入群組事件
@handler.add(MemberJoinedEvent)
def handle_join_event_reply_message(event):
    print("成員加入群組事件")

    line_group_id = event.source.group_id
    group = db_student.get_group_by_line_GID(line_group_id=line_group_id)
    group_number = group['group_number']

    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=0))
    line_bot_api.push_message(to=line_group_id, messages=TextSendMessage(text=f"你們的小組編號是{group_number}號"))
    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=1))


# ---------------------------------------------------------- 群組

# ----------------------------- 群組回覆事件
def handle_group_reply_message(event):
    print("group reply")

    _messages = get_group_reply_messages(event)
    
    # 非指令不理
    if not _messages:
        return
    
    line_group_id = event.source.group_id

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


# ----------------------------- manage message
def get_group_reply_messages(event):
    trigger = event.message.text

    # 記錄每個小組到哪個id階段，確保某些流程不能重複
    pass

    # ------------------------------------- 輸入學號姓名新增學生資料
    if "學號" in trigger or "姓名" in trigger:
        text = trigger.split('/')
        student_number = text[0].replace('學號:','').replace('學號：','').strip()
        student_name = text[1].replace('姓名:','').replace('姓名：','').strip()
        _messages = [TextSendMessage(text=f"你的學號是：{student_number}/姓名是：{student_name}，恭喜你成功加入，接下來我們一起努力吧！")]

        line_user_id = event.source.user_id
        line_group_id = event.source.group_id
        new_student = db_student.create_student(line_user_id=line_user_id,student_number=student_number,student_name=student_name,line_group_id=line_group_id)
    
    # ------------------------------------- 完成作業繳交 trigger?
    elif trigger == '繳交此階段作業' or trigger == 'O':
        _messages = get_flex_messages(id=MessageId.O.value)

    # ------------------------------------- 引導作業繳交 trigger?
    elif trigger == '繳交作業' or trigger == 'N':
        _messages = get_flex_messages(id=MessageId.N.value)

    # ------------------------------------- 回報團體作業反思 trigger?
    elif trigger == '回報團體作業反思' or trigger == 'M':
        _messages = get_flex_messages(id=MessageId.M.value)

    # ------------------------------------- 提醒還有未完成的任務 trigger?
    elif trigger == '提醒還有未完成的任務' or trigger == 'P':
        _messages = get_flex_messages(id=MessageId.P.value)
        # 回報任務列表
        _messages.extend(get_flex_messages(id=MessageId.E.value))

    # ------------------------------------- 引導作業查核與反思 trigger?
    elif trigger == '引導作業查核與反思' or trigger == 'L':
        _messages = get_flex_messages(id=MessageId.L.value)

    # ------------------------------------- 完成團體任務反思回報 trigger?
    elif trigger == '完成團體任務反思' or trigger == 'K':
        _messages = get_flex_messages(id=MessageId.K.value)

    # ------------------------------------- 完成任務回報 trigger?
    elif trigger == '完成任務' or trigger == 'J':
        _messages = get_flex_messages(id=MessageId.J.value)

    # ------------------------------------- 執行任務回報 trigger?
    elif trigger == '執行任務' or trigger == 'I':
        _messages = get_flex_messages(id=MessageId.I.value)

    # ------------------------------------- 全部認領回報 trigger?
    elif trigger == '認領完成' or trigger == 'G':
        _messages = get_flex_messages(id=MessageId.G.value)
        # 執行任務引導
        _messages.extend(get_flex_messages(id=MessageId.H.value))
        # 回報任務列表
        _messages.extend(get_flex_messages(id=MessageId.E.value))

    # ------------------------------------- 認領任務 trigger?
    elif trigger == '認領' or trigger == 'F':
        _messages = get_flex_messages(id=MessageId.F.value)
        # 執行任務引導
        _messages.extend(get_flex_messages(id=MessageId.H.value))
        # 回報任務列表
        _messages.extend(get_flex_messages(id=MessageId.E.value))

    # ------------------------------------- 新增任務 trigger?
    elif trigger == '新增' or trigger == 'D':
        _messages = get_flex_messages(id=MessageId.D.value)
        # 回報任務列表
        _messages.extend(get_flex_messages(id=MessageId.E.value))

    # ------------------------------------- 第一次新增任務 trigger?
    elif trigger == '首次新增' or trigger == 'C':
        _messages = get_flex_messages(id=MessageId.C.value)
        # 回報任務列表
        _messages.extend(get_flex_messages(id=MessageId.E.value))

    # ------------------------------------- 規劃任務
    elif trigger == '我知道期中專題要做什麼了！':
        _messages = get_flex_messages(id=MessageId.B.value)
    # ------------------------------------- 公布期中專題
    elif trigger == 'A':
        _messages = get_flex_messages(id=MessageId.A.value)
    else:
        _messages = None

    return _messages




# line_bot_api.reply_message(event.reply_token, TextSendMessage(text=t_group_join))

