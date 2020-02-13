# bot.py
import requests
import os
from flask import Flask, request # Add your telegram token as environment variable
from apscheduler.schedulers.background import BackgroundScheduler

BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
MESSAGE_URL = BOT_URL + 'sendMessage'
LUNCH_TIME = '12:45'

app = Flask(__name__)
chats_id = []

msg_dict = {
    'arriba': 'pero no más arriba que ESPAÑA',
}

def lunch_time():
    print('lunchtime')
    for chat_id in chats_id:
        response_msg = {
            "chat_id": chat_id,
            "text": 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME
        }
        requests.post(MESSAGE_URL, json=response_msg)

@app.route('/', methods=['POST'])
def main():
    data = request.json

    print(data)  # Comment to hide what Telegram is sending you
    chat_id = data['message']['chat']['id']
    if not chat_id in chats_id:
        chats_id.append(chat_id)
    message = data['message']['text'].lower()

    response_msg = {}
    for possible_str, response_str in msg_dict.items():
        if possible_str in message:
            response_msg = {
                "chat_id": chat_id,
                "text": response_str,
            }
        if response_msg:
            requests.post(MESSAGE_URL, json=response_msg)
    if message == 'test':
        lunch_time()

    return ''


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(lunch_time, 'cron', day_of_week='mon-fri', hour=23, minute=41)
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)