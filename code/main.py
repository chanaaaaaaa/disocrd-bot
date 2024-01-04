from flask import Flask, request
from flask_ngrok import run_with_ngrok
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 載入 json 標準函式庫，處理回傳的資料格式
import requests, json, time

import  jpype     
import  asposecells     
jpype.startJVM() 
from asposecells.api import Workbook

app = Flask(__name__)

access_token = 'Gs2gpzDO1/T99ggBEf/NqZfVjjejQ2zDL6iIJciH7MqqMVKkZAhNQL02P/SXx0t/LTkb9o7G0/bjQejhdpPiGdd1HGnhnEEISokwIFikKTYowZFJe0frqjvfJPIeOf+vwvZ/StynJASjIZQCnyt/NwdB04t89/1O/w1cDnyilFU='
channel_secret = '8de70cc350dc45902920777a64d73df8'

# LINE 回傳圖片函式
def reply_image(msg, rk, token):
    headers = {'Authorization':f'Bearer {token}','Content-Type':'application/json'}    
    body = {
    'replyToken':rk,
    'messages':[{
          'type': 'image',
          'originalContentUrl': msg,
          'previewImageUrl': msg
        }]
    }
    req = requests.request('POST', 'https://api.line.me/v2/bot/message/reply', headers=headers,data=json.dumps(body).encode('utf-8'))
    print(req.text)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)    # 取得收到的訊息內容
    try:
        line_bot_api = LineBotApi(access_token)               # 確認 token 是否正確
        handler = WebhookHandler(channel_secret)              # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']       # 加入回傳的 headers
        handler.handle(body, signature)                       # 綁定訊息回傳的相關資訊
        json_data = json.loads(body)                          # 轉換內容為 json 格式
        reply_token = json_data['events'][0]['replyToken']    # 取得回傳訊息的 Token ( reply message 使用 )
        user_id = json_data['events'][0]['source']['userId']  # 取得使用者 ID ( push message 使用 )
        print(json_data)                                      # 印出內容
        if 'message' in json_data['events'][0]:               # 如果傳送的是 message
            if json_data['events'][0]['message']['type'] == 'text':   # 如果 message 的類型是文字 text
                text = json_data['events'][0]['message']['text']      # 取出文字
                if text == '雷達回波圖' or text == '雷達回波':           # 如果是雷達回波圖相關的文字
                    # 傳送雷達回波圖 ( 加上時間戳記 )
                    reply_image('https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png', reply_token, access_token)
                elif text == '!help' or text == '！help':
                    line_bot_api.reply_message(reply_token,TextSendMessage(text='"雷達回波圖"\n傳送最新的台灣周圍雷達迴波圖\n以上')) 
                else:
                    line_bot_api.reply_message(reply_token,TextSendMessage(text='別吵 有問題就用"!help"'))
    except:
        print('error')                       # 如果發生錯誤，印出 error
    return 'OK'                              # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
  run_with_ngrok(app)                        # 串連 ngrok 服務
  app.run()