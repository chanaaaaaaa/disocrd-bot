from flask import Flask, request
from flask_ngrok import run_with_ngrok
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 載入 json 標準函式庫，處理回傳的資料格式
import requests, json, time, statistics 

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

# 地震資訊函式
def earth_quake():
    msg = ['找不到地震資訊','https://example.com/demo.jpg']            # 預設回傳的訊息
    try:
        code = 'CWA-53CDB49E-D455-4018-BE72-36E6B6700123'
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
        e_data = requests.get(url)                                   # 爬取地震資訊網址
        e_data_json = e_data.json()                                  # json 格式化訊息內容
        eq = e_data_json['records']['Earthquake']                    # 取出地震資訊
        for i in eq:
            loc = i['EarthquakeInfo']['Epicenter']['Location']       # 地震地點
            val = i['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'] # 地震規模
            dep = i['EarthquakeInfo']['FocalDepth']              # 地震深度
            eq_time = i['EarthquakeInfo']['OriginTime']              # 地震時間
            img = i['ReportImageURI']                                # 地震圖
            msg = [f'{loc}，芮氏規模 {val} 級，深度 {dep} 公里，發生時間 {eq_time}。', img]
            break     # 取出第一筆資料後就 break
        return msg    # 回傳 msg
    except:
        return msg    # 如果取資料有發生錯誤，直接回傳 msg

# LINE push 訊息函式
def push_message(msg, uid, token):
    headers = {'Authorization':f'Bearer {token}','Content-Type':'application/json'}   
    body = {
    'to':uid,
    'messages':[{
            "type": "text",
            "text": msg
        }]
    }
    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push', headers=headers,data=json.dumps(body).encode('utf-8'))
    print(req.text)

# LINE 回傳訊息函式
def reply_message(msg, rk, token):
    headers = {'Authorization':f'Bearer {token}','Content-Type':'application/json'}
    body = {
    'replyToken':rk,
    'messages':[{
            "type": "text",
            "text": msg
        }]
    }
    req = requests.request('POST', 'https://api.line.me/v2/bot/message/reply', headers=headers,data=json.dumps(body).encode('utf-8'))
    print(req.text)

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

# 目前天氣函式
def current_weather(address):
    city_list, area_list, area_list2 = {}, {}, {} # 定義好待會要用的變數
    msg = '找不到氣象資訊。'                         # 預設回傳訊息

    # 定義取得資料的函式
    def get_data(url):
        w_data = requests.get(url)   # 爬取目前天氣網址的資料
        w_data_json = w_data.json()  # json 格式化訊息內容
        location = w_data_json['cwaopendata']['dataset']['Station']  # 取出對應地點的內容
        for i in location:
            name = i['StationName']                       # 測站地點
            city = i['GeoInfo']['CountyName']     # 縣市名稱
            area = i['GeoInfo']['TownName']     # 鄉鎮行政區
            dailyhigh = check_data(i['WeatherElement']['DailyExtreme']['DailyHigh']['TemperatureInfo']['AirTemperature'])
            dailylow = check_data(i['WeatherElement']['DailyExtreme']['DailyLow']['TemperatureInfo']['AirTemperature'])
            temp = check_data(i['WeatherElement']['AirTemperature'])                         # 氣溫
            humd = check_data(round(float(i['WeatherElement']['RelativeHumidity'] )*1,1)) # 相對濕度
            r24 = check_data(i['WeatherElement']['Now']['Precipitation'])                    # 累積雨量
            if area not in area_list:
                area_list[area] = {'temp':temp, 'humd':humd, 'r24':r24, 'dailyhigh':dailyhigh, 'dailylow':dailylow}  # 以鄉鎮區域為 key，儲存需要的資訊
            if city not in city_list:
                city_list[city] = {'temp':[], 'humd':[], 'r24':[], 'dailyhigh':[], 'dailylow':[]}       # 以主要縣市名稱為 key，準備紀錄裡面所有鄉鎮的數值
            city_list[city]['temp'].append(temp)               # 記錄主要縣市裡鄉鎮區域的溫度 ( 串列格式 )
            city_list[city]['humd'].append(humd)               # 記錄主要縣市裡鄉鎮區域的濕度 ( 串列格式 )
            city_list[city]['r24'].append(r24)                 # 記錄主要縣市裡鄉鎮區域的雨量 ( 串列格式 )
            city_list[city]['dailyhigh'].append(dailyhigh)     # 記錄主要縣市裡鄉鎮區域最高溫 ( 串列格式 )
            city_list[city]['dailylow'].append(dailylow)       # 記錄主要縣市裡鄉鎮區域最低溫 ( 串列格式 )

    # 定義如果數值小於 0，回傳 False 的函式
    def check_data(e):
        return False if float(e)<0 else float(e)

    # 定義產生回傳訊息的函式
    def msg_content(loc, msg):
        a = msg
        for i in loc:
            if i in address: # 如果地址裡存在 key 的名稱
                temp = f"氣溫 {loc[i]['temp']} 度" if loc[i]['temp'] != False else ''
                dailyhigh = f"\n最高溫 {loc[i]['dailyhigh']}度" if loc[i]['dailyhigh'] != False else ''
                dailylow = f"\n最低溫 {loc[i]['dailylow']}度" if loc[i]['dailylow'] != False else ''
                humd = f"\n相對濕度 {loc[i]['humd']}%" if loc[i]['humd'] != False else ''
                r24 = f"\n累積雨量 {loc[i]['r24']}mm" if loc[i]['r24'] != False else ''
                description = f'{temp}{dailyhigh}{dailylow}{humd}{r24}'
                a = f'{description}' # 取出 key 的內容作為回傳訊息使用
                break
        return a

    try:
        # 因為目前天氣有兩組網址，兩組都爬取
        code = 'CWA-53CDB49E-D455-4018-BE72-36E6B6700123'
        get_data(f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization={code}&downloadType=WEB&format=JSON')
        get_data(f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0003-001?Authorization={code}&downloadType=WEB&format=JSON')

        for i in city_list:
            if i not in area_list2: # 將主要縣市裡的數值平均後，以主要縣市名稱為 key，再度儲存一次，如果找不到鄉鎮區域，就使用平均數值
                area_list2[i] = {'temp':round(statistics.mean(city_list[i]['temp']),1),
                                'humd':round(statistics.mean(city_list[i]['humd']),1),
                                'r24':round(statistics.mean(city_list[i]['r24']),1),
                                'dailyhigh':round(statistics.mean(city_list[i]['dailyhigh']),1),
                                'dailylow':round(statistics.mean(city_list[i]['dailylow']),1)
                                }
        msg = msg_content(area_list2, msg)  # 將訊息改為「大縣市」
        msg = msg_content(area_list, msg)   # 將訊息改為「鄉鎮區域」
        return msg    # 回傳 msg
    except:
        print(Exception)
        return msg    # 如果取資料有發生錯誤，直接回傳 msg

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
            if json_data['events'][0]['message']['type'] == 'location':
                address = json_data['events'][0]['message']['address'].replace('台','臺')
                # 回覆爬取到的相關氣象資訊
                reply_message(f'{address}\n\n{current_weather(address)}', reply_token, access_token)
                print(address)
            if json_data['events'][0]['message']['type'] == 'text':   # 如果 message 的類型是文字 text
                text = json_data['events'][0]['message']['text']      # 取出文字
                if text == '!help' or text == '！help':
                    line_bot_api.reply_message(reply_token,TextSendMessage(text='"雷達回波圖"\n傳送最新的台灣周圍雷達迴波圖\n"地震資訊"\n傳送最新有感地震資訊\n"指定地點當前氣象狀況"\n左下角+號 位置資訊\n以上')) 
                elif text == '雷達回波圖' or text == '雷達回波':           # 如果是雷達回波圖相關的文字
                    # 傳送雷達回波圖 ( 加上時間戳記 )
                    reply_image('https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png', reply_token, access_token)
                elif text == '地震資訊' or text == '地震':              # 如果是地震相關的文字
                    msg = earth_quake()                               # 爬取地震資訊
                    push_message(msg[0], user_id, access_token)       # 傳送地震資訊 ( 用 push 方法，因為 reply 只能用一次 )
                    reply_image(msg[1], reply_token, access_token)    # 傳送地震圖片 ( 用 reply 方法 )
                else:
                    line_bot_api.reply_message(reply_token,TextSendMessage(text='別吵 有問題就用"!help"'))
    except:
        print('error')                       # 如果發生錯誤，印出 error
    return 'OK'                              # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
  run_with_ngrok(app)                        # 串連 ngrok 服務
  app.run()