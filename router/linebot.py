from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from config import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, header
from fastapi import APIRouter, HTTPException, Request

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

router = APIRouter(
    prefix='/linebot',
    tags=['linebot']
)

# Webhook 驗證功能
@router.post('/callback')
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    # get request body as text
    body = await request.body()

    # handle webhook body
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter",headers=header)
    return "Success"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)