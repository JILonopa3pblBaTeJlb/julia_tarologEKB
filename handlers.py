import random
import logging
import time
import json
from telegram import Update
from telegram.ext import CallbackContext
from gpt_handler import get_gpt_response, send_random_emoji
from config import DIALOGUE_LIST, KEYWORDS_HANDLERS, BOT_NAMES, LOG_MODE
from taro import handle_taro
from diet import handle_diet
from horoscope import handle_horoscope
from itchin import handle_itchin
from emojification import emojify
import config_vars as config

def initialize_variables():
    config.last_gpt_response_time = None
    config.hexagram_count = 0
    config.last_user_id = None
    config.last_username = None
    config.bot_start_time = time.time()  # Initialize bot_start_time
    config.last_successful_provider = None
    logging.info(f"Variables initialized: bot_start_time={config.bot_start_time}, hexagram_count={config.hexagram_count}")

def load_hexagram_count():
    try:
        with open(config.HEXAGRAM_COUNT_FILE, 'r') as f:
            data = json.load(f)
            count = data.get('count', 0)
            logging.info(f"Hexagram count loaded: {count}")
            return count
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error loading hexagram count: {e}")
        return 0

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if LOG_MODE:
        logging.info(f"Received message: {text}")

    # Unconditional responses to reply messages
    if update.message.reply_to_message:
        # Check if the replied message was sent by the bot
        if update.message.reply_to_message.from_user.username == context.bot.username:
            # Проверяем ключевые слова в ответе на сообщение
            for keyword, handler_name in KEYWORDS_HANDLERS.items():
                if keyword in text:
                    handler_function = globals().get(handler_name)
                    if handler_function:
                        handler_function(update, context)
                        config.last_username = update.message.from_user.username
                        return
            respond_to_message(update, context, text)
            return

    # Unconditional responses to messages with specific keywords
    for keyword, handler_name in KEYWORDS_HANDLERS.items():
        if keyword in text:
            if LOG_MODE:
                logging.info(f"Detected keyword '{keyword}'. Calling handler '{handler_name}'.")
            handler_function = globals().get(handler_name)
            if handler_function:
                handler_function(update, context)
                config.last_username = update.message.from_user.username
                return
            else:
                logging.error(f"Handler function '{handler_name}' not found for keyword '{keyword}'")
                update.message.reply_text(f"Handler function '{handler_name}' not found.")
                return

    # Unconditional responses to messages containing bot names
    if any(name in text for name in BOT_NAMES):
        respond_to_message(update, context, text)
        return

    # Handling other messages with 0.00001 probability
    if random.random() < 0.0001:
        if random.random() < 0.5:
            # Send random dialogue response
            response = random.choice(DIALOGUE_LIST)
            if response:
                response = emojify(response)
                if LOG_MODE:
                    logging.info("Sending random dialogue response.")
                update.message.reply_text(response)
                config.last_username = update.message.from_user.username
            else:
                send_random_emoji(update, context)
                config.last_username = update.message.from_user.username
        else:
            respond_to_message(update, context, text)
    else:
        if LOG_MODE:
            logging.info("No keyword or bot name found, and decided not to respond.")

def respond_to_message(update: Update, context: CallbackContext, text: str):
    response, provider = get_gpt_response(text, update, context)
    if response:
        response = emojify(response)
        update.message.reply_text(response)
        config.last_gpt_response_time = time.time()
        config.last_successful_provider = provider
        config.last_username = update.message.from_user.username
        logging.info(f"Updated last_gpt_response_time: {config.last_gpt_response_time}")
        logging.info(f"Updated last_successful_provider: {config.last_successful_provider}")
    else:
        send_random_emoji(update, context)
        config.last_username = update.message.from_user.username

# For debugging purposes
if __name__ == "__main__":
    class MockUpdate:
        class Message:
            from_user = type('obj', (object,), {'id': 123456})
            def reply_text(self, text):
                print(f"Replying with text: {text}")
        message = Message()

    class MockContext:
        args = []

    update = MockUpdate()
    context = MockContext()
    handle_message(update, context)
