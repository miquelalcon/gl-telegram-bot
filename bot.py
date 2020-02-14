# bot.py
import requests
import os
from flask import Flask, request # Add your telegram token as environment variable
from apscheduler.schedulers.background import BackgroundScheduler

BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
GIT_MEDIA_URL = 'https://raw.githubusercontent.com/miquelalcon/gl-telegram-bot/master/media/'
MESSAGE_URL = BOT_URL + 'sendMessage'
ANIMATION_URL = BOT_URL + 'sendAnimation'
LUNCH_TIME = '12:45'

app = Flask(__name__)
chats_id = [os.environ["BSC_CHAT"]]

msg_dict = {
    'arriba':   'Pero no más arriba que ESPAÑA',
    'dale':     'Mostrame un cuarto de teta aunque sea',
    'franco':   'FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO, POR QUÉ GRITO FRANCO'
}

gif_dict = {
    'españa':   GIT_MEDIA_URL + 'dragonite.mp4',
    'espanya':  GIT_MEDIA_URL + 'dragonite.mp4',
    'spanin':   GIT_MEDIA_URL + 'dragonite.mp4',
    'comunis':  GIT_MEDIA_URL + 'comunism.mp4',
    'roj':      GIT_MEDIA_URL + 'comunism.mp4',
    'guizmo':   GIT_MEDIA_URL + 'guizmo.mp4'
}

def lunch_time():
    for chat_id in chats_id:
        response_msg = {
            "chat_id": chat_id,
            "text": 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME
        }
        requests.post(MESSAGE_URL, json=response_msg)

@app.route('/', methods=['POST'])
def main():
    data = request.json

    # print(data)  # Comment to hide what Telegram is sending you
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        message = data['message']['text'].lower()
        for possible_str, response_str in msg_dict.items():
            response_msg = {}
            if possible_str in message:
                response_msg = {
                    "chat_id": chat_id,
                    "text": response_str,
                }
            if response_msg:
                requests.post(MESSAGE_URL, json=response_msg)
        for possible_str, response_url in gif_dict.items():
            response_msg = {}
            if possible_str in message:
                response_msg = {
                    "chat_id": chat_id,
                    "animation": response_url,
                }
            if response_msg:
                requests.post(ANIMATION_URL, json=response_msg)

    return ''


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(lunch_time, 'cron', day_of_week='mon-fri', hour=11, minute=45)
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
