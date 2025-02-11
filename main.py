# main.py

import time
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers import handle_message, initialize_variables
from command_handler import start, diag, logon, logoff, handle_panic, set_log_mode, handle_nut, handle_nutedit
from config import TOKEN, LOG_MODE
import config_vars as config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    set_log_mode(LOG_MODE)  # Set initial log mode
    initialize_variables()  # Initialize all global variables

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("diag", diag))
    dp.add_handler(CommandHandler("logon", logon))
    dp.add_handler(CommandHandler("logoff", logoff))
    dp.add_handler(CommandHandler("panic", handle_panic))
    dp.add_handler(CommandHandler("nut", handle_nut))  # Register /nut command
    dp.add_handler(CommandHandler("nutedit", handle_nutedit))  # Register /nutedit command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

if __name__ == '__main__':
    main()
