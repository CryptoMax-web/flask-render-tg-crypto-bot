import os
import datetime
import pandas as pd
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
            # extract the necessary information
            txhash = from_address = "[" + str(logs['event']['activity'][0]['hash']) + "](https://etherscan.io/tx/" + str(logs['event']['activity'][0]['hash']) + ")"

            from_address = "[" + str(logs['event']['activity'][0]['fromAddress']) + "](https://etherscan.io/address/" + str(logs['event']['activity'][0]['fromAddress']) + "#tokentxns)"
            to_address = "[" + str(logs['event']['activity'][0]['toAddress']) + "](https://etherscan.io/address/" + str(logs['event']['activity'][0]['toAddress']) + "#tokentxns)"

            token_symbol = logs['event']['activity'][0]['asset']
            token_address = "[" + str(logs['event']['activity'][0]['rawContract']['address']) + "](https://etherscan.io/address/" + str(logs['event']['activity'][0]['rawContract']['address']) + ")"

            value = str(round(logs['event']['activity'][0]['value']))

            # create the text string
            message = f'*Token transfer:*\n{txhash}\nfrom {from_address} \nto {to_address}: \nvalue: {value} *{token_symbol}* {token_address}'
            if token_symbol is not None and token_symbol not in ['USDT', 'USDC', 'WBTC', 'WETH','DAI', 'ETH'] and float(value) >= 1000 and value != 0:
                # add the record to the Excel file
                with open(os.path.join(os.path.expanduser("~"), "Desktop", "token_transfers.xlsx"), "a") as f:
                    record = {
                        "txhash": txhash,
                        "token_symbol": token_symbol,
                        "value": value,
                        "time": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    }
                    df = pd.DataFrame.from_dict([record], orient='index', columns=['txhash', 'token_symbol', 'value', 'time'])
                    df.to_excel(f, sheet_name="Token transfers", index=False)

                # send a notification to the Telegram channel
                bot.send_message(chat_id=user_chat_id, text=message, parse_mode='MarkdownV2'

