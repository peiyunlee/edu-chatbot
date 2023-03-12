from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from fastapi import APIRouter, HTTPException, Request
import json

import copy

from config import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN_TEST, CHANNEL_SECRET_TEST, header, LIFF_TASK_TOOL, LIFF_REFLECT_TASK, LIFF_REFLECT_HW 
from db import db_student, db_task, db_hw, db_task_reflect, db_hw_reflect
from message.manage_other import get_welcome_flex_messages
from message.manage import get_messages, MessageId


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN_TEST)
handler = WebhookHandler(CHANNEL_SECRET_TEST)

router = APIRouter(
    prefix='/linebot',
    tags=['linebot']
)

# ----------------------------- Webhook 驗證功能
@router.post('/callback', summary="linebot callback")
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
    if event.source.type == "group":
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
    db_student.create_group(line_group_id=line_group_id)

    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=0))
    line_bot_api.push_message(to=line_group_id,messages=TextMessage(text="學號：111034010/姓名：李小明"))


# ----------------------------- 監聽成員加入群組事件
@handler.add(MemberJoinedEvent)
def handle_join_event_reply_message(event):
    print("成員加入群組事件")

    line_group_id = event.source.group_id

    line_bot_api.push_message(to=line_group_id,messages=get_welcome_flex_messages(id=0))
    line_bot_api.push_message(to=line_group_id,messages=TextMessage(text="學號：111034010/姓名：李小明"))


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
        db_student.create_student(line_user_id=line_user_id,student_number=student_number,student_name=student_name,line_group_id=line_group_id)

    # ------------------------------------- 完成作業繳交 trigger?
    elif trigger == '操作選單':
        line_user_id = event.source.user_id
        _messages =  manage_Q_message(line_user_id=line_user_id)

    # ------------------------------------- 完成作業繳交 trigger?
    elif trigger == '進行下一階段作業':
        line_user_id = event.source.user_id
        group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
        db_student.update_group_hw_no_now(group_id=group['_id'], hw_no_now=group['hw_no_now'])
        _messages =  manage_B_message(hw_no_now=group['hw_no_now'])

    # ------------------------------------- 完成作業繳交 trigger?
    elif trigger == '完成繳交作業':
        _messages = get_messages(id=MessageId.O.value)

    # # ------------------------------------- 引導作業繳交 trigger?
    # elif trigger == '繳交作業' or trigger == 'N':
    #     _messages = get_messages(id=MessageId.N.value)

    # ------------------------------------- 引導作業查核與反思 trigger?
    elif trigger == '我要繳交作業':
        line_user_id = event.source.user_id
        group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
        is_all_completed = db_task.is_group_all_task_is_all_completed(group_id=group['_id'],hw_no=group['hw_no_now'])
        if is_all_completed:
            _messages = get_messages(id=MessageId.L.value)
        else:
            # 提醒還有尚未完成的工作
            _messages = get_messages(id=MessageId.P.value)
            # 回報工作列表
            _messages.extend(manage_E_message(group_id=group['_id']))



    # # ------------------------------------- 執行工作回報 trigger?
    # elif trigger == '執行工作' or trigger == 'I':
    #     _messages = get_messages(id=MessageId.I.value)

    # ------------------------------------- 規劃工作
    elif trigger == '我知道期中專題要做什麼了！':
        line_user_id = event.source.user_id
        group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
        _messages =  manage_B_message(hw_no_now=group['hw_no_now'])
    else:
        _messages = None

    print(trigger) 

    return _messages


def push_A(homeworks, all_groups):
    _messages = manage_A_message(homeworks=homeworks)

    for group in all_groups:
        line_group_id = group['line_group_id']
        print(f"公布期中專題到群組:{line_group_id}")
        line_bot_api.push_message(to=line_group_id, messages=_messages)


def manage_A_message(homeworks):
    contents = get_messages(id=MessageId.A.value)

    _messages = []

    contents[1] = {
        "type": "carousel",
        "contents": []
    }

    for hw_idx, hw in enumerate(homeworks):
        rules_contents =  [{
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": hw['rule1_title'],
                                "size": "md",
                                "color": "#111111",
                                "align": "start",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": ('\n').join(hw['rule1_contents']),
                                "size": "md",
                                "color": "#111111",
                                "align": "start",
                                "wrap": True
                            }
                            ],
                            "spacing": "sm"
                        }]
            
        if hw['hw_no'] == 1:
            rules_contents.append(
                        {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": hw['rule2_title'],
                                    "size": "md",
                                    "color": "#111111",
                                    "align": "start",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": ('\n').join(hw['rule2_contents']),
                                    "size": "md",
                                    "color": "#111111",
                                    "align": "start",
                                    "wrap": True
                                }
                                ],
                                "spacing": "sm"
                            }
                            )
            rules_contents.append(
                    {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": hw['rule3_title'],
                                "size": "md",
                                "color": "#111111",
                                "align": "start",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": ('\n').join(hw['rule3_contents']),
                                "size": "md",
                                "color": "#111111",
                                "align": "start",
                                "wrap": True
                            }
                            ],
                            "spacing": "sm"
                        }
                        )

        bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": f"作業{hw_idx+1}:{hw['title']}",
                        "weight": "bold",
                        "size": "lg",
                        "margin": "sm",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": hw['description'],
                        "size": "md",
                        "color": "#111111",
                        "align": "start",
                        "wrap": True,
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "md",
                        "contents": rules_contents
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "lg",
                        "contents": [
                        {
                            "type": "text",
                            "text": "繳交方式",
                            "size": "md",
                            "flex": 0,
                            "weight": "bold",
                            "align": "start",
                            "color": "#aaaaaa"
                        },
                        {
                            "type": "text",
                            "text": hw['hand_over'],
                            "size": "md",
                            "wrap": True,
                            "color": "#aaaaaa",
                            "align": "end"
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "lg",
                        "contents": [
                        {
                            "type": "text",
                            "text": "繳交日期",
                            "size": "md",
                            "flex": 0,
                            "weight": "bold",
                            "align": "start",
                            "color": "#aaaaaa"
                        },
                        {
                            "type": "text",
                            "text": hw['hand_over_date'],
                            "size": "md",
                            "color": "#aaaaaa",
                            "align": "end"
                        }
                        ]
                    }
                    ]
                },
                "styles": {
                    "footer": {
                    "separator": True
                    }
                }
                 }

        contents[1]['contents'].append(bubble)
        
    for idx, content in enumerate(contents):
        _messages.append(
            FlexSendMessage(
                alt_text=f"公布期中專題規範",
                contents=content
            )
        )

    return _messages


def push_B(hw_no_now: int, line_group_id: str):
    _messages = manage_B_message(hw_no_now=hw_no_now)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_B_message(hw_no_now: int):
    contents = get_messages(id=MessageId.B.value)

    # 修改規範內容
    hw = db_hw.get_hw_by_hw_no(hw_no=hw_no_now)

    rules_contents =  [{
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": hw['rule1_title'],
                "size": "md",
                "color": "#111111",
                "align": "start",
                "weight": "bold"
            },
            {
                "type": "text",
                "text": ('\n').join(hw['rule1_contents']),
                "size": "md",
                "color": "#111111",
                "align": "start",
                "wrap": True
            }
        ],
        "spacing": "sm"
    }]

    contents[1] = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": f"作業{hw_no_now}:{hw['title']}",
                "weight": "bold",
                "size": "lg",
                "margin": "sm",
                "color": "#1DB446"
            },
            {
                "type": "text",
                "text": hw['description'],
                "size": "md",
                "color": "#111111",
                "align": "start",
                "wrap": True,
                "margin": "lg"
            },
            {
                "type": "separator",
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "xxl",
                "spacing": "md",
                "contents": rules_contents
            },
            {
                "type": "separator",
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "lg",
                "contents": [
                {
                    "type": "text",
                    "text": "繳交方式",
                    "size": "md",
                    "flex": 0,
                    "weight": "bold",
                    "align": "start",
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": hw['hand_over'],
                    "size": "md",
                    "wrap": True,
                    "color": "#aaaaaa",
                    "align": "end"
                }
            ]
        },
        {
            "type": "box",
            "layout": "horizontal",
                "margin": "lg",
                "contents": [
                        {
                            "type": "text",
                            "text": "繳交日期",
                            "size": "md",
                            "flex": 0,
                            "weight": "bold",
                            "align": "start",
                            "color": "#aaaaaa"
                        },
                        {
                            "type": "text",
                            "text": hw['hand_over_date'],
                            "size": "md",
                            "color": "#aaaaaa",
                            "align": "end"
                        }
                        ]
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "md",
                        "action": {
                        "type": "uri",
                        "label": "規劃工作",
                        "uri": f"{LIFF_TASK_TOOL}/hw/{hw_no_now}"
                        },
                        "margin": "none"
                    }
                    ],
                    "margin": "none"
                },
                "styles": {
                    "footer": {
                    "separator": True
                    }
                }
            }
    
    _messages = []

    for idx, content in enumerate(contents):
        _messages.append(
            FlexSendMessage(
                alt_text=f"公布期中專題規範",
                contents=content
            )
        )

    return _messages


# def push_C(line_group_id: str):
#     _messages = get_messages(id=MessageId.C.value)
#     # 回報工作列表
#     # _messages.extend(manage_E_message(group_id=group_id))

#     for item in _messages:
#         line_bot_api.push_message(to=line_group_id, messages=item)


def push_D(line_group_id: str, group_id: str):
    _messages = get_messages(id=MessageId.D.value)
    # 回報工作列表
    _messages.extend(manage_E_message(group_id=group_id))

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def push_G(line_group_id: str, group_id: str):
    _messages = get_messages(id=MessageId.G.value)
    # 執行工作引導
    _messages.extend(get_messages(id=MessageId.H.value))
    # 回報工作列表
    _messages.extend(manage_E_message(group_id=group_id))

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def push_F(line_group_id: str, task_name: str, student_name: str, group_id: str):
    _messages = manage_F_message(student_name, task_name)
    # 執行工作引導
    _messages.extend(get_messages(id=MessageId.H.value))
    # 回報工作列表
    _messages.extend(manage_E_message(group_id=group_id))

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_F_message(student_name, task_name):
    contents = get_messages(id=MessageId.F.value)
    contents[0]['body']['contents'][0]['text'] = f"{student_name} 認領了「{task_name}」工作！"
    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人認領工作囉!",
                contents=content
            )
        )
    return _messages


def manage_E_message(group_id: str):
    contents = get_messages(id=MessageId.E.value)
    
    new_contents = copy.deepcopy(contents)

    content_unclaimed = new_contents[0]["contents"][0]
    content_undo = new_contents[0]["contents"][1]
    content_finish = new_contents[0]["contents"][2]
    content_button = new_contents[0]["contents"][3]

    tasks = db_task.get_group_all_task(group_id=group_id)

    new_contents[0]["contents"] = []

    for idx, task in enumerate(tasks):
        new_content = None
        if idx >= 11:
            break
        if task['student_id'] == '':
            new_content = copy.deepcopy(content_unclaimed)
            new_content['body']['contents'][0]['text'] = task['task_name']
            new_content['body']['contents'][3]['text'] = task['plan']
            new_content['body']['contents'][6]['text'] = task['hand_over']
            new_content['body']['contents'][8]['text'] = f"繳交日期 {task['hand_over_date']}"
            
            new_content['body']['contents'][9]['action']['uri'] = f"{LIFF_TASK_TOOL}/hw/{task['hw_no']}"
        elif not task['is_finish']:
            new_content = copy.deepcopy(content_undo)
            new_content['body']['contents'][0]['text'] = task['task_name']
            new_content['body']['contents'][3]['text'] = task['plan']
            new_content['body']['contents'][6]['text'] = task['hand_over']
            new_content['body']['contents'][8]['text'] = f"繳交日期 {task['hand_over_date']}"
            
            new_content['body']['contents'][9]['action']['uri'] = f"{LIFF_REFLECT_TASK}/{task['_id']}"
        
        # elif task['is_finish']:
        #     new_content = copy.deepcopy(content_finish)
        #     new_content['body']['contents'][0]['text'] = task['task_name']
        #     new_content['body']['contents'][4]['text'] = task['plan']
        #     new_content['body']['contents'][7]['text'] = task['hand_over']
        #     new_content['body']['contents'][9]['text'] = f"繳交日期 {task['hand_over_date']}"
        #     new_content['body']['contents'][10]['text'] = f"完成日期 {task['finish_date']}"

        if new_content:
            new_contents[0]["contents"].append(new_content)

    if len(tasks) >= 12:
        new_contents[0]["contents"].append(content_button)

    _messages = []
    for content in new_contents:
        _messages.append(
            FlexSendMessage(
                alt_text="公告目前所有的工作",
                contents=content
            )
        )
    return _messages
    

def push_J(line_group_id: str, task_name: str, student_name: str, reflect1: str, reflect2: str, score: int, hand_over: str, hand_over_date: str, finish_date: str, task_id: str):
    _messages = manage_J_message(student_name=student_name, task_name=task_name, reflect1=reflect1, reflect2=reflect2, score=score, hand_over=hand_over, hand_over_date=hand_over_date,finish_date=finish_date,task_id=task_id)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_J_message(student_name, task_name, reflect1, reflect2, score, hand_over, hand_over_date, finish_date, task_id):
    contents = get_messages(id=MessageId.J.value)
    contents[0]['body']['contents'][1]['text'] = task_name
    contents[0]['body']['contents'][2]['text'] = student_name
    contents[0]['body']['contents'][4]['contents'][1]['text'] = reflect1
    contents[0]['body']['contents'][6]['contents'][1]['text'] = reflect2
    contents[0]['body']['contents'][8]['contents'][1]['text'] = f"{score}分 / 100分"
    contents[0]['body']['contents'][10]['contents'][1]['text'] = hand_over
    contents[0]['body']['contents'][11]['contents'][1]['text'] = hand_over_date
    contents[0]['body']['contents'][12]['contents'][1]['text'] = finish_date

    contents[1]['body']['contents'][2]['action']['uri'] = f"{LIFF_REFLECT_TASK}/{task_id}"

    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages


def push_K(student_name: str, task_name: str, task_id: str, line_group_id: str):
    _messages = manage_K_message(student_name=student_name, task_name=task_name, task_id=task_id)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_K_message(student_name, task_name, task_id):
    contents = get_messages(id=MessageId.K.value)
    new_contents = copy.deepcopy(contents)

    new_contents[0]['contents'][0]['body']['contents'][1]['text'] = task_name

    task_reflects = db_task_reflect.get_task_all_reflect(task_id=task_id)

    bubble = new_contents[0]['contents'][1]

    temp_bubbles = []

    for reflect in task_reflects:
        student = db_student.get_student_by_student_id(student_id=reflect['student_id'])
        student_name = student['name']
        if reflect['is_self']:
            bubble['contents'][0]['text'] = "負責人"
            new_contents[0]['contents'][0]['body']['contents'][2]['text'] = f"負責人：{student_name}"
        else:
            bubble['contents'][0]['text'] = "成員回饋"

        # 成員回饋
        bubble['contents'][1]['text'] = student_name
        bubble['contents'][3]['contents'][1]['text'] = reflect['reflect1']
        bubble['contents'][5]['contents'][1]['text'] = reflect['reflect2']
        bubble['contents'][7]['contents'][1]['text'] = f"{reflect['score']}分 / 100分"

        temp_bubbles.append(bubble)

    new_contents[0]['contents'] = temp_bubbles

    _messages = []
    for content in new_contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages


def push_L(line_user_id:str, line_group_id: str):
    _messages = manage_L_message(line_uer_id=line_user_id)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_L_message(line_uer_id):
    contents = get_messages(id=MessageId.L.value)

    group = db_student.get_group_by_student_line_UID(line_user_id=line_uer_id)

    contents[0]['body']['contents'][2]['action']['uri'] = f"{LIFF_REFLECT_HW}/{group['hw_no_now']}"

    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages


def push_M(hw_no: int, line_user_id: str, line_group_id:str):
    _messages = manage_M_message(hw_no, line_user_id)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_M_message(hw_no, line_user_id):
    contents = get_messages(id=MessageId.M.value)

    students = db_student.get_group_members_by_student_line_UID(line_user_id=line_user_id)
    hw = db_hw.get_hw_by_hw_no(hw_no=hw_no)

    # M0
    bubble_m0 = {
      "type": "bubble",
      "size": "kilo",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "李大明的檢查結果",
            "weight": "bold",
            "size": "lg",
            "margin": "md"
          },
          {
            "type": "separator",
            "margin": "lg"
          }
        ]
      },
      "styles": {
        "footer": {
          "separator": True
        }
      }
    }

    bubble_m1 = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "成員回饋",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": "李二明",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "作業還有沒有可以改進的地方？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "我覺得....",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "團隊進行遇到的挑戰？應該如何克服？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "我覺得....",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "下次規劃要注意的事情？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "我覺得...",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "你有什麼其他的建議呢？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "我覺得....",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "spacing": "none",
                    "contents": [
                    {
                        "type": "text",
                        "text": "你對團隊的滿意程度？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "80分 / 100分",
                        "size": "sm",
                        "color": "#555555",
                        "align": "end"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "spacing": "none",
                    "contents": [
                    {
                        "type": "text",
                        "text": "你覺得作業的完成度？",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "80分 / 100分",
                        "size": "sm",
                        "color": "#555555",
                        "align": "end"
                    }
                    ]
                }
                ]
            },
            "styles": {
                "footer": {
                "separator": True
                }
            }
            }

    for student in students:

        hw_check = db_hw_reflect.get_hw_check(hw_no=hw_no, student_id=student['_id'])

        new_bubble = copy.deepcopy(bubble_m0)

        new_bubble['body']['contents'][0]['text'] = f"{student['name']}的檢查結果"

        for idx, check in enumerate(hw_check['rule1_checked']):
            if not check:
                new_bubble['body']['contents'].append({
                    "type": "text",
                    "text": f"{hw['rule1_title']}",
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                    "weight": "bold",
                    "margin": "lg"
                })
                new_bubble['body']['contents'].append({
                    "type": "text",
                    "text": f"{hw['rule1_contents'][idx]}",
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                    "margin": "md"
                })

            if hw_no == 1:
                for idx, check in enumerate(hw_check['rule2_checked']):
                    if not check:
                        new_bubble['body']['contents'].append({
                            "type": "text",
                            "text": f"{hw['rule2_title']}",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0,
                            "weight": "bold",
                            "margin": "lg"
                        })
                        new_bubble['body']['contents'].append({
                            "type": "text",
                            "text": f"{hw['rule2_contents'][idx]}",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0,
                            "margin": "md"
                        })

                for idx, check in enumerate(hw_check['rule3_checked']):
                    if not check:
                        new_bubble['body']['contents'].append({
                            "type": "text",
                            "text": f"{hw['rule3_title']}",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0,
                            "weight": "bold",
                            "margin": "lg"
                        })
                        new_bubble['body']['contents'].append({
                            "type": "text",
                            "text": f"{hw['rule3_contents'][idx]}",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0,
                            "margin": "md"
                        })

        contents[0]['contents'].append(new_bubble)

        # M1
        hw_reflect = db_hw_reflect.get_hw_reflect(hw_no=hw_no, student_id=student['_id'])

        new_bubble = copy.deepcopy(bubble_m1)

        for reflect in hw_reflect:
            new_bubble['body']['contents'][0]['text'] = student['name']
            new_bubble['body']['contents'][3]['contents'][1]['text'] = reflect['reflect1']
            new_bubble['body']['contents'][4]['contents'][1]['text'] = reflect['reflect2']
            new_bubble['body']['contents'][5]['contents'][1]['text'] = reflect['reflect3']
            new_bubble['body']['contents'][6]['contents'][1]['text'] = reflect['reflect4']
            new_bubble['body']['contents'][7]['contents'][1]['text'] = f"{reflect['group_score']}分 / 100分"
            new_bubble['body']['contents'][8]['contents'][1]['text'] = f"{reflect['score']}分 / 100分"

        contents[1]['contents'].append(new_bubble)


    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages


def manage_Q_message(line_user_id):
    contents = get_messages(id=MessageId.Q.value)

    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)

    contents[0]['body']['contents'][1]['action']['uri'] = f"{LIFF_TASK_TOOL}/hw/{group['hw_no_now']}"

    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="操作選單",
                contents=content
            )
        )
    return _messages



# line_bot_api.reply_message(event.reply_token, TextSendMessage(text=t_group_join))

