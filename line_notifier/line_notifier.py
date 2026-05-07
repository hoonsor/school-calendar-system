"""
LINE Bot 學校通知系統
使用 Flask + LINE Messaging API 發送學校行事曆通知
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, PostbackAction
)

app = Flask(__name__)

# 環境變數設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

class SchoolCalendarNotifier:
    """學校行事曆 LINE 通知器"""
    
    def __init__(self, line_bot_api: LineBotApi):
        self.line_api = line_bot_api
    
    def send_holiday_reminder(self, user_id: str, holiday: Dict):
        """發送放假提醒"""
        date = holiday.get('date', '')
        name = holiday.get('name', '')
        
        if len(date) == 8:
            formatted_date = f"{date[:4]}/{date[4:6]}/{date[6:8]}"
        else:
            formatted_date = date
        
        flex_message = FlexSendMessage(
            alt_text=f'📢 {name} 提醒',
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=f'📢 放假通知',
                            weight='bold',
                            size='xl',
                            color='#1DB446'
                        ),
                        TextComponent(
                            text=name,
                            weight='bold',
                            size='lg',
                            margin='md'
                        ),
                        TextComponent(
                            text=f'📅 日期：{formatted_date}',
                            size='md',
                            margin='md'
                        ),
                        TextComponent(
                            text=holiday.get('description', '記得休息喔！'),
                            size='sm',
                            color='#666666',
                            margin='md'
                        )
                    ]
                )
            )
        )
        
        try:
            self.line_api.push_message(user_id, flex_message)
            return True
        except Exception as e:
            print(f"發送失敗: {e}")
            return False
    
    def send_weekly_schedule(self, user_id: str, events: List[Dict]):
        """發送每週行事曆"""
        event_texts = []
        for i, event in enumerate(events[:5], 1):
            event_texts.append(f"{i}. {event.get('name', '事件')}")
        
        message = TextSendMessage(
            text=f"📅 本週行事曆\n\n" + "\n".join(event_texts) if event_texts else "本週沒有特殊事件"
        )
        
        try:
            self.line_api.push_message(user_id, message)
            return True
        except Exception as e:
            print(f"發送失敗: {e}")
            return False
    
    def send_calendar_subscription(self, user_id: str):
        """發送行事曆訂閱邀請"""
        flex_message = FlexSendMessage(
            alt_text='📅 行事曆訂閱邀請',
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text='📅 學校行事曆',
                            weight='bold',
                            size='xl'
                        ),
                        TextComponent(
                            text='點擊下方按鈕訂閱，及時接收放假通知！',
                            size='md',
                            margin='md'
                        ),
                        ButtonComponent(
                            action=PostbackAction(
                                label='📥 訂閱行事曆',
                                data='action=subscribe'
                            ),
                            style='primary',
                            margin='md'
                        ),
                        ButtonComponent(
                            action=PostbackAction(
                                label='📋 查看說明',
                                data='action=help'
                            ),
                            margin='sm'
                        )
                    ]
                )
            )
        )
        
        try:
            self.line_api.push_message(user_id, flex_message)
            return True
        except Exception as e:
            print(f"發送失敗: {e}")
            return False

notifier = SchoolCalendarNotifier(line_bot_api)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理LINE訊息"""
    user_message = event.message.text
    
    if user_message in ['訂閱', '訂閱行事曆', 'subscribe']:
        notifier.send_calendar_subscription(event.source.user_id)
    elif user_message in ['幫助', 'help', '說明']:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='📖 使用說明\n\n輸入「訂閱」訂閱行事曆通知\n輸入「本週」查看本週行事\n輸入「幫助」查看說明')
        )
    elif user_message in ['本週', '這週', 'schedule']:
        # 這裡可以從資料庫讀取本週事件
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='📅 本週沒有特殊事件')
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='📖 學校行事曆 LINE Bot\n\n輸入「訂閱」訂閱行事曆通知')
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理LINE Postback"""
    data = event.postback.data
    
    if data == 'action=subscribe':
        # 處理訂閱
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='✅ 訂閱成功！\n未來放假通知會第一時間發送給你！')
        )
    elif data == 'action=help':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='📖 使用說明\n\n• 輸入「訂閱」訂閱行事曆通知\n• 系統會在放假日前一天發送提醒')
        )

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE Webhook 端點"""
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@app.route('/api/notify', methods=['POST'])
def send_notification():
    """HTTP API: 發送通知"""
    data = request.get_json()
    user_id = data.get('user_id')
    holiday = data.get('holiday')
    
    if not user_id or not holiday:
        return jsonify({'error': '缺少參數'}), 400
    
    success = notifier.send_holiday_reminder(user_id, holiday)
    return jsonify({'success': success})

@app.route('/api/broadcast', methods=['POST'])
def broadcast_holiday():
    """HTTP API: 廣播放假通知給所有訂閱者"""
    data = request.get_json()
    holidays = data.get('holidays', [])
    
    # 這裡應該從資料庫讀取所有訂閱者
    # subscriber_ids = get_all_subscribers()
    subscriber_ids = []  # 替換為實際的訂閱者ID列表
    
    results = []
    for user_id in subscriber_ids:
        for holiday in holidays:
            result = notifier.send_holiday_reminder(user_id, holiday)
            results.append({'user_id': user_id, 'success': result})
    
    return jsonify({'results': results})

@app.route('/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

def main():
    """本地端測試用"""
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()