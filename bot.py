# bot.py
import requests
import os
import random
import re
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
INSULTS = read_file('media/insults_cat.txt') + read_file('media/insults_es.txt')
striked = os.environ["STRIKED"]

app = Flask(__name__)
lunch_chat_id = os.environ["BSC_CHAT"]

re_commands = [r'^\/strike\s+\@(?P<usr>\w+)\s*',r'^\/strike\@grande_y_libre_bot\s+\@(?P<usr>\w+)\s*']
re_commands = [re.compile(x) for x in re_commands]

msg_responses = {
    'arriba':       'Pero no más arriba que ESPAÑA',
    'dale':         'Mostrame un cuarto de teta aunque sea',
    'franco':       'FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO FRANCO, POR QUÉ GRITO FRANCO',
    'aunque sea':   'Dale Carla',
    'tarta':        'Nooo, dónde te sentaaaaaste',
    'cake':         'Nooo, dónde te sentaaaaaste',
    'pastel':       'Nooo, dónde te sentaaaaaste'
}

gifs = {
    'edited':       GIT_MEDIA_URL + 'edit.mp4',
    'dragonite':    GIT_MEDIA_URL + 'dragonite.mp4',
    'comunism':     GIT_MEDIA_URL + 'comunism.mp4',
    'espetec':      GIT_MEDIA_URL + 'espetec.mp4',
    'guizmo':       GIT_MEDIA_URL + 'guizmo.mp4'
}

gif_responses = {
    'españ':   gifs['dragonite'],
    'espany':  gifs['dragonite'],
    'spain':   gifs['dragonite'],
    'catal':   gifs['espetec'],
    'comunis':  gifs['comunism'],
    'roj':      gifs['comunism'],
    'guizmo':   gifs['guizmo']
}

def is_command(message):
    return message['entities']['type'] == 'bot_command'

def get_command(message):
    for c in re_commands:
        result = c.search(message['text'])
        if result:
            start_strike(result.group('usr'))
            break

def start_strike(usr):
    print('LETSGO ' + usr)

def lunch_time():
    response_msg = {
        "chat_id": lunch_chat_id,
        "text": 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME
    }
    requests.post(MESSAGE_URL, json=response_msg)

def send_message(chat_id, text, reply_id=''):
    response_msg = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_id:
        response_msg['reply_to_message_id'] = reply_id
    requests.post(MESSAGE_URL, json=response_msg)

def send_animation(chat_id, animation, reply_id=''):
    response_msg = {
        "chat_id": chat_id,
        "animation": animation,
    }
    if reply_id:
        response_msg['reply_to_message_id'] = reply_id
    requests.post(ANIMATION_URL, json=response_msg)

@app.route('/', methods=['POST'])
def main():
    data = request.json

    print(data)
    # Normal messages
    if 'message' in data and 'text' in data['message']:
        message = data['message']
        chat_id = message['chat']['id']

        if is_command(message):
            command = get_command(message)
        else:
            message_txt = message['text'].lower()
            message_usr = ''
            if 'from' in message and 'username' in message['from']:
                message_usr = message['from']['username']

            ## Strike 
            if os.environ['STRIKED'] != '' and message_usr == striked:
                send_message(chat_id, '@'+ message_usr + ' ' + random.choice(INSULTS).lower())

            ## Messages 
            for possible_str, response_str in msg_responses.items():
                response_msg = {}
                if possible_str in message_txt:
                    send_message(chat_id, response_str)

            ## Animations 
            for possible_str, response_url in gif_responses.items():
                response_msg = {}
                if possible_str in message_txt:
                    send_animation(chat_id, response_url)

    # Edited messages
    if 'edited_message' in data and 'text' in data['edited_message']:
        message = data['edited_message']
        chat_id = message['chat']['id']
        send_animation(chat_id, gifs['edited'], message['message_id'])

    return ''

def create_app():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lunch_time, 'cron', day_of_week='mon-fri', hour=11, minute=45)
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    create_app()
