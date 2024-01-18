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
    return 'Service for sending notifications to a telegram channel '

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
            # Get the necessary information from the incoming logs

            # Get the type of action
            action_type = logs['event']['activity'][0]['type']

            # Get the sender address
            sender_address = logs['event']['activity'][0]['sender']

            # Get the recipient address
            recipient_address = logs['event']['activity'][0]['recipient']

            # Get the amount of tokens
            amount = str(round(logs['event']['activity'][0]['value']))

            # Get the token symbol
            token_symbol = logs['event']['activity'][0]['asset']

            # Get the token price in USDT
            usdt_price = get_usdt_price(token_symbol)

            # Construct the message string

            if action_type == "Transfer":
                message = f'**Swap:**\n{amount} {token_symbol}\n**From:** {sender_address}\n**To:** {recipient_address}\n**On:**\nUniswap V3'
            elif action_type == "Create":
                message = f'**Create Contract:**\n{token_symbol}\n**By:** {sender_address}'
            elif action_type == "Delete":
                message = f'**Delete Contract:**\n{token_symbol}\n**By:** {sender_address}'
            else:
                message = f'**Action:** {action_type}\n**From:** {sender_address}\n**To:** {recipient_address}\n**Amount:** {amount} {token_symbol}\n**USDT Value:** {amount} * {usdt_price} = {usdt_price * amount}\n'

            # Send the message to the Telegram channel
            bot.send_message(chat_id=user_chat_id, text=message, parse_mode='MarkdownV2')

    return Response(status=200)

updater = Updater(TELEGRAM_API_TOKEN)
# Start the bot
updater.start_polling()

if __name__ == '__main__':
    app.run()

