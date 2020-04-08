# bot.py
import requests
import os
import random
import re
import datetime
import json 
from flask import Flask, request # Add your telegram token as environment variable
from apscheduler.schedulers.background import BackgroundScheduler
import mysql.connector
from mysql.connector import errorcode

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
DB_TABLES = {}
DB_TABLES['strikes'] = (
    "CREATE TABLE strikes ("
    "  chat_id bigint(255) NOT NULL,"
    "  user char(255) NOT NULL,"
    "  PRIMARY KEY (chat_id)"
    ") ENGINE=InnoDB")
DB_TABLES['efes'] = (
    "CREATE TABLE efes ("
    "  user char(255) NOT NULL,"
    "  count int(255) NOT NULL,"
    "  PRIMARY KEY (user)"
    ") ENGINE=InnoDB")
DB_INSERTS = {}
DB_INSERTS['strikes'] = (
    "INSERT INTO strikes (chat_id, user) "
    "VALUES (%(chat_id)s, %(user)s)")
DB_INSERTS['efes'] = (
    "INSERT INTO efes (user, count) "
    "VALUES (%(user)s, %(count)s)")
DB_QUERIES = {}
DB_QUERIES['strikes'] = (
    "SELECT user FROM strikes "
    "WHERE chat_id = %(chat_id)s")
DB_QUERIES['efes'] = (
    "SELECT count FROM efes "
    "WHERE user = %(user)s")
DB_QUERIES['efes_all'] = (
    "SELECT * FROM efes")
DB_UPDATES = {}
DB_UPDATES['strikes'] = (
    "UPDATE strikes SET user = %(user)s "
    "WHERE chat_id = %(chat_id)s")
DB_UPDATES['efes'] = (
    "UPDATE efes SET count = %(count)s "
    "WHERE user = %(user)s")

app = Flask(__name__)
mydb = mysql.connector.connect(
   host = os.environ["JAWSDB_HOST"],
   user = os.environ["JAWSDB_USR"],
   password = os.environ["JAWSDB_PASSWD"],
   database = os.environ["JAWSDB_DB"]
)
cursor = mydb.cursor()
scheduler = BackgroundScheduler()

bsc_chat_id = os.environ["BSC_CHAT"]

commands = {
    'strike': ([
        r'^\/strike\s+\@(?P<user>\w+)\s*\n*$',
        r'^\/strike\@grande_y_libre_bot\s+\@(?P<user>\w+)\s*\n*$',
    ], ['user']
    ),
    'ftable': ([
        r'^\/ftable\s*\n*$',
        r'^\/ftable\@grande_y_libre_bot\s*\n*$'
    ], [])
}
for k in commands.keys():
    commands[k] = [re.compile(x) for x in commands[k]]

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
    'itadakimasu':  URLS['resources'] + 'itadakimasu.mp4',
    'corona-naruto':URLS['resources'] + 'corona-naruto.gif',
    'iceage':       URLS['resources'] + 'iceage.mp4',
    'puig':         URLS['resources'] + 'puig.mp4'
}

gif_responses = {
    'españ':        gifs['dragonite'],
    'espany':       gifs['dragonite'],
    'spain':        gifs['dragonite'],
    'catal':        gifs['espetec'],
    'comunis':      gifs['comunism'],
    'roj':          gifs['comunism'],
    'guizmo':       gifs['guizmo'],
    'corona-naruto':gifs['corona-naruto'],
    'franco':       gifs['iceage']
}

current_poll_info = {}

def is_command(message):
    if 'entities' in message:
        for entity in message['entities']:
            if entity['type'] == 'bot_command':
                return True
    return False

def get_command(message):
    for k, v in commands.items():
        for c in v[0]:
            result = c.search(message['text'])
            if result:
                if v[1]:
                    return (k, result.groups(v[1]))
                return (k)
    return []

def start_strike(chat_id, user):
    poll = {
        'chat_id': chat_id,
        'question': '¿Merece @%s un buen strike? Teneis %d minutos para decidir'%(user, POLL_TIME),
        'options': ['Por supuesto', 'No'],
        'is_anonymous': False,
        'allows_multiple_answers': False,
    }
    content = json.loads(requests.post(URLS['poll'], json=poll).content)   
    message_id = content['result']['message_id']
    scheduler.add_job(finish_strike, 'date', run_date=datetime.datetime.now()+datetime.timedelta(minutes=POLL_TIME), args=[chat_id, user, message_id])
    return {'chat_id':chat_id, 'user': user}

def finish_strike(chat_id, user, message_id):
    requests.post(URLS['stop_poll'], json={
        'chat_id':      chat_id,
        'message_id':   message_id
    })

@scheduler.scheduled_job('cron', id='go_lunch_time', day_of_week='mon-fri', hour=10, minute=45)
def go_lunch_time():
    #msg = 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME
    msg = 'F'
    send_message(bsc_chat_id, msg)

@scheduler.scheduled_job('cron', id='start_lunch_time', day_of_week='mon-fri', hour=11, minute=5)
def start_lunch_time():
    #send_message(bsc_chat_id, 'Itadakimasu!')
    send_animation(bsc_chat_id, gifs['corona-naruto'])


def send_message(chat_id, text, parse_mode='', reply_id=''):
    response_msg = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_id:
        response_msg['reply_to_message_id'] = reply_id
    if parse_mode:
        response_msg['parse_mode'] = parse_mode
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

def db_init():
    global cursor
    #cursor.execute("DROP TABLE strikes")
    #cursor.execute("DROP TABLE efes")
    for table_name in DB_TABLES:
       table_description = DB_TABLES[table_name]
       try:
           print("Creating table {}: ".format(table_name), end='')
           cursor.execute(table_description)
       except mysql.connector.Error as err:
           if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
               print("already exists.")
           else:
               print(err.msg)
       else:
           print("OK")

def db_query(table_name, data):
    #print(DB_QUERIES[table_name]%data)
    cursor.execute(DB_QUERIES[table_name], data)
    return cursor.fetchall()

def db_insert(table_name, data):
    #print(DB_INSERTS[table_name]%data)
    cursor.execute(DB_INSERTS[table_name], data)
    mydb.commit()

def db_update(table_name, data):
    #print(DB_UPDATES[table_name]%data)
    cursor.execute(DB_UPDATES[table_name], data)
    mydb.commit()
    
def db_update_or_insert(table_name, data):
    response = db_query(table_name, data)
    if not response:
        db_insert(table_name, data)
    else:
        db_update(table_name, data)

def get_striked(chat_id):
    response = db_query('strikes', {'chat_id': chat_id})
    if response:
        return response[0][0]
    else: 
        return ''

def is_striked(chat_id, user):
    if user == '':
        return False
    return user == get_striked(chat_id)

def change_striked(chat_id, user):
    data = {'chat_id': chat_id, 'user': user}
    db_update_or_insert('strikes', data)
    

@app.route('/', methods=['POST'])
def main():
    global current_poll_info
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
            print(command)
            if command[0] == 'strike':
                posible_striked = command[1][0]
                striked = get_striked(chat_id)
                if not current_poll_info and posible_striked != striked:
                    current_poll_info = start_strike(chat_id, posible_striked)
                elif current_poll_info:
                    send_message(chat_id, 'No seas ansias @%s, ya hay una votación en curso'%message_usr)
                elif posible_striked == striked:
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
            elif command[0] == 'ftable':
                response = db_query('efes_all', {})
                msg = '*Tabla de clasificacion de Fs:*\n'
                i = 1
                for user, count in sorted(response, key=lambda x: x[1], reverse=True):
                    msg += '  %d. @%s con %d\n'%(i,user,count)
                    i += 1
                send_message(chat_id, msg, parse_mode='Markdown')
        else:
            ## Strike
            if is_striked(chat_id, message_usr):
                send_message(chat_id, '@'+ message_usr + ' ' + random_insult())

            ## Animations
            for possible_str, response_url in gif_responses.items():
                response_msg = {}
                if possible_str in message_txt:
                    send_animation(chat_id, response_url)

            ## Messages
            for possible_str, response_str in msg_responses.items():
                response_msg = {}
                if possible_str in message_txt:
                    send_message(chat_id, response_str)

            if message_usr and str(chat_id) == bsc_chat_id and message_txt == 'f':
                table_name = 'efes'
                data = {'user': message_usr, 'count': 1}
                response = db_query(table_name, data)
                if not response:
                    db_insert(table_name, data)
                else:
                    data['count'] += response[0][0]
                    db_update(table_name, data)
                
                if data['count']%10 == 0:
                    send_message(chat_id, 'Nuestro querido @%s acumula un total *%d* Fs. ¡Una F por él!'%(message_usr, data['count']), parse_mode='Markdown')

    if 'poll' in data and data['poll']['is_closed']:
        options = data['poll']['options']
        if 'chat_id' in current_poll_info:
            chat_id = current_poll_info['chat_id']
            user = current_poll_info['user']
            send_message(chat_id, 'Fin de la votacion para ' + '@' + user)
            striked = get_striked(chat_id)
            if options[0]['voter_count'] > options[1]['voter_count']:
                change_striked(chat_id, user)
                send_message(chat_id, 'Veredicto: estas jodido @' + user)
            elif options[0]['voter_count'] < options[1]['voter_count']:
                send_message(chat_id, 'Veredicto: sigues en la mierda @' + striked)
            else:
                new_striked = random.choice([striked, user])
                if striked == new_striked:
                    send_message(chat_id, 'Veredicto: gracias a random.choice sigues en la mierda @' + striked)
                else:
                    change_striked(chat_id, new_striked)
                    send_message(chat_id, 'Veredicto: gracias a random.choice estas jodido @' + striked)
            current_poll = {}

    # Edited messages
    if 'edited_message' in data and 'text' in data['edited_message']:
        message = data['edited_message']
        chat_id = message['chat']['id']
        send_animation(chat_id, gifs['edited'], message['message_id'])

    return ''

def create_app():
    scheduler.start()
    db_init()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    create_app()
