# bot.py
import requests
import os
import random
from flask import Flask, request # Add your telegram token as environment variable
from apscheduler.schedulers.background import BackgroundScheduler

def read_file(path):
    with open(path, 'r') as f:
        return list(f.readlines())

BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
GIT_MEDIA_URL = 'https://raw.githubusercontent.com/miquelalcon/gl-telegram-bot/master/media/'
MESSAGE_URL = BOT_URL + 'sendMessage'
ANIMATION_URL = BOT_URL + 'sendAnimation'
LUNCH_TIME = '12:45'
INSULTS = read_file('media/insults_cat.txt')

app = Flask(__name__)
lunch_chat_id = os.environ["BSC_CHAT"]

msg_dict = {
    'arriba':   'Pero no más arriba que ESPAÑA',
    'dale':     'Mostrame un cuarto de teta aunque sea',
    'franco':   'FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO, POR QUÉ GRITO FRANCO'
}

gifs = {
    'edited': GIT_MEDIA_URL + 'edit.mp4'
}

gif_dict = {
    'españ':   GIT_MEDIA_URL + 'dragonite.mp4',
    'espany':  GIT_MEDIA_URL + 'dragonite.mp4',
    'spain':   GIT_MEDIA_URL + 'dragonite.mp4',
    'comunis':  GIT_MEDIA_URL + 'comunism.mp4',
    'roj':      GIT_MEDIA_URL + 'comunism.mp4',
    'guizmo':   GIT_MEDIA_URL + 'guizmo.mp4'
}

def lunch_time():
    response_msg = {
        "chat_id": lunch_chat_id,
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
        usr = data['message']['from']
        if usr['username'] != '' and usr['username'] == os.environ["STRICKED"]:
            response_msg = {
                "chat_id": chat_id,
                "text": random.choice(INSULTS).capitalize(),
            }
            requests.post(MESSAGE_URL, json=response_msg)
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

    if 'edited_message' in data and 'text' in data['edited_message']:
        message = data['edited_message']
        response_msg = {
            "chat_id": message['chat']['id'],
            "animation": gifs['edited'],
            "reply_to_message_id": message['message_id']
        }
        requests.post(ANIMATION_URL, json=response_msg)
    return ''

def create_app():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lunch_time, 'cron', day_of_week='mon-fri', hour=11, minute=45)
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    create_app()
