import os
from flask import Flask, request, Response
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)

# Set up Telegram bot API
TELEGRAM_API_TOKEN = os.environ['BOT_TOKEN']
bot = Bot(TELEGRAM_API_TOKEN)
user_chat_id = os.environ['CHANNEL_ID']

@app.route('/')
def hello():
    return 'Service for sending notifications to a telegram channel'

@app.route('/notify', methods=['POST', 'GET'])
def notify():
    logs = request.json
    if (len(logs) == 0):
        print("Empty logs array received, skipping")
    else:
        print(logs)
        category = ""
        try:
            category = logs['event']['activity'][0]['category']
        except:
            print("category not defined")
        if logs['webhookId'] == os.environ['ALCHEMY_KEY'] and category == 'token':
            # extract the necessary information
            txhash = str(logs['event']['activity'][0]['hash'])
            from_address = str(logs['event']['activity'][0]['fromAddress'])
            to_address = str(logs['event']['activity'][0]['toAddress'])
            token_symbol = str(logs['event']['activity'][0]['asset'])
            token_address = str(logs['event']['activity'][0]['rawContract']['address'])
            value = str(round(logs['event']['activity'][0]['value']))

            # get current price
            price = requests.get("https://api.coinmarketcap.com/v1/ticker/" + token_symbol + "/").json()[0]["price_usd"]

            # create the text string
            message = f'*Token transfer:* \n{txhash} \nfrom {from_address} \nto {to_address}: \nvalue: {value} *{token_symbol}* {token_address}\n\nCurrent price: ${price}'

            # add a button to the message
            button_text = "View chart"
            button_url = f"https://dexscreener.com/tokens/{token_symbol.lower()}"
            message += f"\n\n[**Button:** {button_text}](https://dexscreener.com/tokens/{token_symbol.lower()})"

            # Send the message to the Telegram channel
            bot.send_message(chat_id=user_chat_id, text=message, parse_mode='MarkdownV2')

    return Response(status=200)

updater = Updater(TELEGRAM_API_TOKEN)
# Start the bot
updater.start_polling()

if __name__ == '__main__':
    app.run()

