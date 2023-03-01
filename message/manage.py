
import json
from linebot.models import *
from enum import IntEnum

counts = [
    4,2,1,1,1,
    1,1,1,2,2,
    2,1,3,1,1,
    1
]

class MessageId(IntEnum):
    #公布作業
    A = 0
    #規劃作業
    B = 1
    #第一次回報新增任務
    C = 2
    #只要新增任務就回報
    D = 3
    #回報任務列表
    E = 4
    #認領回報
    F = 5
    #認領完成回報
    G = 6
    #執行任務引導
    H = 7
    #執行任務
    I = 8
    #完成任務
    J = 9
    #回報團體任務反思
    K = 10
    #引導作業查核與反思
    L = 11
    #回報團體作業反思
    M = 12
    #引導作業繳交
    N = 13
    #完成作業繳交
    O = 14
    #提醒還有未完成的任務
    P = 15

# --------------------------- convert_to_flex_message

def get_flex_messages(id:int):
    _messages = []
    count = counts[id]
    name = MessageId(id).name

    for idx in range(0,count):
        f = open (f'./message/content/{name}{idx}.json', "r")
        _messages.append(
            FlexSendMessage(
                alt_text=f"{name}{idx}",
                contents=json.loads(f.read())
            )
        )

    refresh_flex_message()

    return _messages


# --------------------------- 修改訊息內容(作業A0、A1、A2、B1)
def refresh_flex_message():
    pass
# all_messages['A'][0].contents.body.contents[0].text = "dasfas"