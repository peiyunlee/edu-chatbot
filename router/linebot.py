from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from fastapi import APIRouter, HTTPException, Request
import json

import copy

from config import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN_TEST, CHANNEL_SECRET_TEST, header, LIFF_TASK_TOOL, LIFF_REFLECT_TASK, LIFF_REFLECT_HW 
from db import db_student, db_task, db_hw, db_task_reflect
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
    elif trigger == '繳交此階段作業' or trigger == 'O':
        _messages = get_messages(id=MessageId.O.value)

    # ------------------------------------- 引導作業繳交 trigger?
    elif trigger == '繳交作業' or trigger == 'N':
        _messages = get_messages(id=MessageId.N.value)

    # ------------------------------------- 提醒還有未完成的工作 trigger?
    elif trigger == '提醒還有未完成的工作' or trigger == 'P':
        _messages = get_messages(id=MessageId.P.value)
        # 回報工作列表
        _messages.extend(get_messages(id=MessageId.E.value))

    # ------------------------------------- 引導作業查核與反思 trigger?
    elif trigger == '我要繳交作業':
        _messages = get_messages(id=MessageId.L.value)

    # # ------------------------------------- 執行工作回報 trigger?
    # elif trigger == '執行工作' or trigger == 'I':
    #     _messages = get_messages(id=MessageId.I.value)

    # ------------------------------------- 規劃工作
    elif trigger == '我知道期中專題要做什麼了！':
        line_user_id = event.source.user_id
        _messages =  manage_B_message(line_user_id=line_user_id)
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


def manage_B_message(line_user_id):
    contents = get_messages(id=MessageId.B.value)
    
    # GET小組目前是第幾個作業
    group = db_student.get_group_by_student_line_UID(line_user_id=line_user_id)
    hw_no_now = group['hw_no_now']

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

    content_unclaimed = contents[0]["contents"][0]
    content_undo = contents[0]["contents"][1]
    content_finish = contents[0]["contents"][2]
    content_button = contents[0]["contents"][3]

    tasks = db_task.get_group_all_task(group_id=group_id)

    contents[0]["contents"] = []

    for idx, task in enumerate(tasks):
        if idx >= 11:
            break
        if task['student_id'] == '':
            new_content = copy.deepcopy(content_unclaimed)
            new_content['body']['contents'][0]['text'] = task['task_name']
            new_content['body']['contents'][3]['text'] = task['plan']
            new_content['body']['contents'][6]['text'] = task['hand_over']
            new_content['body']['contents'][8]['text'] = f"繳交日期 {task['hand_over_date']}"
            
            new_content['body']['contents'][9]['action']['uri'] = f"{LIFF_TASK_TOOL}/hw/{task['hw_no']}"
        elif task['is_finish']:
            new_content = copy.deepcopy(content_finish)
            new_content['body']['contents'][0]['text'] = task['task_name']
            new_content['body']['contents'][4]['text'] = task['plan']
            new_content['body']['contents'][7]['text'] = task['hand_over']
            new_content['body']['contents'][9]['text'] = f"繳交日期 {task['hand_over_date']}"
            new_content['body']['contents'][10]['text'] = f"完成日期 {task['hand_over']}"
        else:
            new_content = copy.deepcopy(content_undo)
            new_content['body']['contents'][0]['text'] = task['task_name']
            new_content['body']['contents'][3]['text'] = task['plan']
            new_content['body']['contents'][6]['text'] = task['hand_over']
            new_content['body']['contents'][8]['text'] = f"繳交日期 {task['hand_over_date']}"
            
            new_content['body']['contents'][9]['action']['uri'] = f"{LIFF_REFLECT_TASK}/{task['_id']}"

        contents[0]["contents"].append(new_content)

    if len(tasks) >= 12:
        contents[0]["contents"].append(content_button)

    _messages = []
    for content in contents:
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
    contents[0]['contents'][0]['body']['contents'][1]['text'] = task_name

    task_reflects = db_task_reflect.get_task_all_reflect(task_id=task_id)

    for reflect in task_reflects:
        student = db_student.get_student_by_student_id(student_id=reflect['student_id'])
        student_name = student['name']
        if reflect['is_self']:
            contents[0]['contents'][1]['body']['contents'][0]['text'] = "負責人"
            contents[0]['contents'][0]['body']['contents'][2]['text'] = f"負責人：{student_name}"
        else:
            contents[0]['contents'][1]['body']['contents'][0]['text'] = "成員回饋"

        # 成員回饋
        contents[0]['contents'][1]['body']['contents'][1]['text'] = student_name
        contents[0]['contents'][1]['body']['contents'][3]['contents'][1]['text'] = reflect['reflect1']
        contents[0]['contents'][1]['body']['contents'][5]['contents'][1]['text'] = reflect['reflect2']
        contents[0]['contents'][1]['body']['contents'][7]['contents'][1]['text'] = f"{reflect['score']}分 / 100分"

        new_content = copy.deepcopy(contents[0]['contents'][1])
        contents[0]['contents'].append(new_content)

    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages


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


def push_M(student_name: str, task_name: str, task_id: str, line_group_id: str):
    _messages = manage_M_message(student_name=student_name, task_name=task_name, task_id=task_id)

    for item in _messages:
        line_bot_api.push_message(to=line_group_id, messages=item)


def manage_M_message(student_name, task_name, task_id):
    contents = get_messages(id=MessageId.M.value)
    contents[0]['contents'][0]['body']['contents'][1]['text'] = task_name

    task_reflects = db_task_reflect.get_task_all_reflect(task_id=task_id)

    for reflect in task_reflects:
        student = db_student.get_student_by_student_id(student_id=reflect['student_id'])
        student_name = student['name']
        if reflect['is_self']:
            contents[0]['contents'][1]['body']['contents'][0]['text'] = "負責人"
            contents[0]['contents'][0]['body']['contents'][2]['text'] = f"負責人：{student_name}"
        else:
            contents[0]['contents'][1]['body']['contents'][0]['text'] = "成員回饋"

        # 成員回饋
        contents[0]['contents'][1]['body']['contents'][1]['text'] = student_name
        contents[0]['contents'][1]['body']['contents'][3]['contents'][1]['text'] = reflect['reflect1']
        contents[0]['contents'][1]['body']['contents'][5]['contents'][1]['text'] = reflect['reflect2']
        contents[0]['contents'][1]['body']['contents'][7]['contents'][1]['text'] = f"{reflect['score']}分 / 100分"

        new_content = copy.deepcopy(contents[0]['contents'][1])
        contents[0]['contents'].append(new_content)

    _messages = []
    for content in contents:
        _messages.append(
            FlexSendMessage(
                alt_text="有人完成工作囉!",
                contents=content
            )
        )
    return _messages



# line_bot_api.reply_message(event.reply_token, TextSendMessage(text=t_group_join))

