
import json
from linebot.models import *
from enum import IntEnum

counts = [
    3,2,1,1,1,
    1,1,1,2,2,
    2,1,3,1,1,
    1,1,1,1,1,
    1,1
]

alt_text = [
    #A
    '公布期中作業規範囉',
    #B
    '請依據期中作業規劃工作',
    #C
    '有新的工作新增囉',
    #D
    '有新的工作新增囉',
    #E
    '公告目前所有的工作',
    #F
    '有人認領工作囉',
    #G
    '全部的工作都認領完成了',
    #H
    '記得執行工作喔！',
    #I
    '有人執行工作囉！',
    #J
    '有人完成工作囉！記得填寫工作成果回饋',
    #K
    '公告團隊對工作的反思與建議',
    #L
    '記得填寫作業查核和成果回饋喔',
    #M
    '回報查核與回饋結果',
    #N
    '可以繳交作業了',
    #O
    '成功完成此階段的作業了，繼續下一階段的作業吧！',
    #P
    '還有工作尚未完成喔！',
    #Q
    '操作選單',
    #R
    '編輯/刪除任務',
    #S
    '推播任務',
    #T
    '推播提醒執行任務',
    #U
    '大家知道期中專題要做什麼了嗎？',
    #V
    '操作說明',
]

class MessageId(IntEnum):
    #公布作業
    A = 0
    #規劃作業
    B = 1
    #第一次回報新增工作
    C = 2
    #只要新增工作就回報
    D = 3
    #回報工作列表
    E = 4
    #認領回報
    F = 5
    #認領完成回報
    G = 6
    #執行工作引導
    H = 7
    #執行工作
    I = 8
    #完成工作
    J = 9
    #回報團體工作反思
    K = 10
    #引導作業查核與反思
    L = 11
    #回報團體作業反思
    M = 12
    #引導作業繳交
    N = 13
    #完成作業繳交
    O = 14
    #提醒還有未完成的工作
    P = 15
    #操作選單
    Q = 16
    #編輯刪除任務 
    R = 17
    #推播
    S = 18
    #推播提醒執行任務
    T = 19
    #知道期中專題按鈕
    U = 20
    #操作說明
    V = 21

# --------------------------- convert_to_flex_message

def get_messages(id:int):
    _messages = []
    count = counts[id]
    name = MessageId(id).name

    for idx in range(0,count):
        f = open (f'./message/content/{name}{idx}.json', "r")
        if name == 'A' or name == 'B' or name == 'F' or name == 'E' or name == 'J' or name == 'K' or name == 'M' or name == 'Q' or name == 'L' or name == 'R' or name == 'T':
            _messages.append(json.loads(f.read()))
        else:
            _messages.append(
                FlexSendMessage(
                    alt_text=alt_text[id],
                    contents=json.loads(f.read())
                )
            )

    return _messages