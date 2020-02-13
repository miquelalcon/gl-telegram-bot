# bot.py
import requests
import os
from flask import Flask, request # Add your telegram token as environment variable
import schedule
import time

BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
MESSAGE_URL = BOT_URL + 'sendMessage'
LUNCH_TIME = '23:28'


app = Flask(__name__)

msg_dict = {
    'arriba': 'pero no más arriba que ESPAÑA',
}

def lunch_time():
    response_msg = {
        "text": 'Todos p\'abajo y arriba España, son las ' + LUNCH_TIME,
    }
    if response_msg:
        requests.post(MESSAGE_URL, json=response_msg)


schedule.every().monday.at(LUNCH_TIME).do(lunch_time)
schedule.every().tuesday.at(LUNCH_TIME).do(lunch_time)
schedule.every().wednesday.at(LUNCH_TIME).do(lunch_time)
schedule.every().thursday.at(LUNCH_TIME).do(lunch_time)
schedule.every().friday.at(LUNCH_TIME).do(lunch_time)

@app.route('/', methods=['POST'])
def main():
    data = request.json

    print(data)  # Comment to hide what Telegram is sending you
    chat_id = data['message']['chat']['id']
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

    return ''


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)