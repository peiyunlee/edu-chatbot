
import json
from linebot.models import *

# --------------------------- convert_to_flex_message

f = open (f'./message/content/welcome.json', "r")
message = json.loads(f.read())

def get_welcome_flex_messages(id:int):
    if message[id]['body']['contents'][0]['type'] == "button":
        alt_text = "點選按鈕"
    else:
        alt_text = message[id]['body']['contents'][0]['text']
    return FlexSendMessage(
                alt_text=alt_text,
                contents=message[id]
            )