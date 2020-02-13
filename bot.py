# bot.py
import requests
import os
from flask import Flask, request# Add your telegram token as environment variable
BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'


app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():
    data = request.json

    print(data)  # Comment to hide what Telegram is sending you
    chat_id = data['message']['chat']['id']
    message = data['message']['text'].lower()

    message_url = BOT_URL + 'sendMessage'
    json_data = {}
    if 'arriba' in message:
        json_data = {
            "chat_id": chat_id,
            "text": 'pero no más arriba que ESPAÑA',
        }

    if json_data:
        requests.post(message_url, json=json_data)

    return ''


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)