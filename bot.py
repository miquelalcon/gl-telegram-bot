# bot.py
import requests
import os
import random
import re
import datetime
import json 
from flask import Flask, request # Add your telegram token as environment variable
from apscheduler.schedulers.background import BackgroundScheduler
from Crypto.Cipher import AES
import mysql.connector

def read_file(path):
    with open(path, 'r') as f:
        return list(f.readlines())

BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
URLS = {
    'message':      BOT_URL + 'sendMessage',
    'animation':    BOT_URL + 'sendAnimation',
    'poll':         BOT_URL + 'sendPoll',
    'stop_poll':    BOT_URL + 'stopPoll',
    'resources':    'https://raw.githubusercontent.com/miquelalcon/gl-telegram-bot/master/resources/'
}

LUNCH_TIME = '12:45'
POLL_TIME = 10
INSULTS = read_file('resources/insults_cat.txt') + read_file('resources/insults_es.txt')
TABLES = {}
TABLES['strikes'] = (
    "CREATE TABLE `strikes` ("
    "  `id` varbinary NOT NULL,"
    "  `name` varbinary NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

app = Flask(__name__)
mydb = mysql.connector.connect(
   host = os.environ["JAWSDB_HOST"],
   user = os.environ["JAWSDB_USR"],
   password = os.environ["JAWSDB_PASSWD"],
   database = os.environ["JAWSDB_DB"]
)
mycursor = mydb.cursor()
scheduler = BackgroundScheduler()

striked = os.environ["STRIKED"]
lunch_chat_id = os.environ["BSC_CHAT"]
cipher = AES.new(str(os.environ["AES_KEY"]).encode(), AES.MODE_CFB, str(os.environ["AES_IV"]).encode('latin-1'))

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
    'edited':       URLS['resources'] + 'edit.mp4',
    'dragonite':    URLS['resources'] + 'dragonite.mp4',
    'comunism':     URLS['resources'] + 'comunism.mp4',
    'espetec':      URLS['resources'] + 'espetec.mp4',
    'guizmo':       URLS['resources'] + 'guizmo.mp4',
    'itadakimasu':  URLS['resources'] + 'itadakimasu.mp4'
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

current_poll_info = {}

def is_command(message):
    if 'entities' in message:
        for entity in message['entities']:
            if entity['type'] == 'bot_command':
                return True
    return False

def get_command(message):
    for c in re_commands:
        result = c.search(message['text'])
        if result:
            return ('strike', result.group('usr'))
    return []

def start_strike(chat_id, usr):
    poll = {
        'chat_id': chat_id,
        'question': '¿Merece @%s un buen strike? Teneis %d minutos para decidir'%(usr, POLL_TIME),
        'options': ['Por supuesto', 'No'],
        'is_anonymous': False,
        'allows_multiple_answers': False,
    }
    content = json.loads(requests.post(URLS['poll'], json=poll).content)   
    message_id = content['result']['message_id']
    scheduler.add_job(finish_strike, 'date', run_date=datetime.datetime.now()+datetime.timedelta(minutes=POLL_TIME), args=[chat_id, usr, message_id])
    return {'chat_id':chat_id, 'usr': usr}

def finish_strike(chat_id, usr, message_id):
    requests.post(URLS['stop_poll'], json={
        'chat_id':      chat_id,
        'message_id':   message_id
    })

@scheduler.scheduled_job('cron', id='go_lunch_time', day_of_week='mon-fri', hour=11, minute=45)
def go_lunch_time():
    msg = 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME
    send_message(lunch_chat_id, msg)

@scheduler.scheduled_job('cron', id='start_lunch_time', day_of_week='mon-fri', hour=12, minute=5)
def start_lunch_time():
    send_message(lunch_chat_id, 'Itadakimasu!')
    send_animation(lunch_chat_id, gifs['itadakimasu'])


def send_message(chat_id, text, reply_id=''):
    response_msg = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_id:
        response_msg['reply_to_message_id'] = reply_id
    requests.post(URLS['message'], json=response_msg)

def send_animation(chat_id, animation, reply_id=''):
    response_msg = {
        "chat_id": chat_id,
        "animation": animation,
    }
    if reply_id:
        response_msg['reply_to_message_id'] = reply_id
    requests.post(URLS['animation'], json=response_msg)

def random_insult():
    return random.choice(INSULTS).lower()

@app.route('/', methods=['POST'])
def main():
    global current_poll_info
    global striked
    data = request.json

    #print(data)
    # Normal messages
    if 'message' in data and 'text' in data['message']:
        message = data['message']
        chat_id = message['chat']['id']
        message_txt = message['text'].lower()
        message_usr = ''
        if 'from' in message and 'username' in message['from']:
            message_usr = message['from']['username']

        if is_command(message):
            command = get_command(message)
            if len(command) >= 2:
                if command[0] == 'strike' and not current_poll_info and command[1] != striked:
                    current_poll_info = start_strike(chat_id, command[1])
                elif current_poll_info:
                    send_message(chat_id, 'No seas ansias @%s, ya hay una votación en curso'%message_usr)
                elif command[1] == striked:
                    send_message(chat_id, 'El pobre @%s ya esta siendo torturado'%striked)
                else:
                    send_message(chat_id, 'Tengo problemas')
                # elif current_poll_info:
                #     send_message(chat_id, '@%s ya hay una votación para strike abierta, ahora te jodes %s'%(message_usr, random_insult()))
                #     current_poll_info = start_strike(chat_id, message_usr)
                # elif command[1] == striked and striked != message_usr:
                #     send_message(chat_id, '@%s tu colega @%s ya esta pringando, ahora te jodes tu %s'%(message_usr, striked, random_insult()))
                #     current_poll_info = start_strike(chat_id, message_usr)
                # elif command[1] == striked and striked == message_usr:
                #     send_message(chat_id, '@%s ya estas pringando, no seas %s'%(message_usr, random_insult()))
        else:
            ## Strike
            if os.environ['STRIKED'] != '' and message_usr == striked:
                send_message(chat_id, '@'+ striked + ' ' + random_insult())

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

    if 'poll' in data and data['poll']['is_closed']:
        options = data['poll']['options']
        chat_id = current_poll_info['chat_id']
        usr = current_poll_info['usr']
        send_message(chat_id, 'Fin de la votacion para ' + '@' + usr)
        if options[0]['voter_count'] > options[1]['voter_count']:
            change_striked(usr)
            send_message(chat_id, 'Veredicto: estas jodido @' + usr)
        elif options[0]['voter_count'] < options[1]['voter_count']:
            send_message(chat_id, 'Veredicto: sigues en la mierda @' + striked)
        else:
            new_striked = random.choice([striked,usr])
            if striked == new_striked:
                send_message(chat_id, 'Veredicto: gracias a random.choice sigues en la mierda @' + striked)
            else:
                change_striked(new_striked)
                send_message(chat_id, 'Veredicto: gracias a random.choice estas jodido @' + striked)
        current_poll = {}

    # Edited messages
    if 'edited_message' in data and 'text' in data['edited_message']:
        message = data['edited_message']
        chat_id = message['chat']['id']
        send_animation(chat_id, gifs['edited'], message['message_id'])

    return ''

def change_striked(usr):
    global striked
    striked = usr
    #with open(os.environ["DATA_PATH"], 'wb') as f:
    #        f.write(cipher.encrypt(striked))

def init_db():
    global mycursor
    for table_name in TABLES:
       table_description = TABLES[table_name]
       try:
           print("Creating table {}: ".format(table_name), end='')
           mycursor.execute(table_description)
       except mysql.connector.Error as err:
           if err.errno == err.ER_TABLE_EXISTS_ERROR:
               print("already exists.")
           else:
               print(err.msg)
       else:
           print("OK")

def init_striked():
    #with open(os.environ["DATA_PATH"], 'rb') as f:
    #    striked = cipher.decrypt(f.readline())
    #if not striked:
    #    print('MODIFY FILE',os.environ["DATA_PATH"])
    #    change_striked(os.environ["STRIKED"])
    striked = os.environ["STRIKED"]

def create_app():
    scheduler.start()
    init_striked()
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    create_app()
