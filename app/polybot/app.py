import flask
from flask import request
import os
from bot import Bot, QuoteBot, ImageProcessingBot


app = flask.Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_APP_URL = os.getenv('TELEGRAM_APP_URL')
MY_TELEGRAM_URL = 'https://t.me/MyImageProcBot'


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    QuoteBot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    QuoteBot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
    app.run(host='0.0.0.0', port=8443)

