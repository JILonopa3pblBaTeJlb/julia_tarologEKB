import json
import random
import time
import os
import logging
from telegram import Update
from telegram.ext import CallbackContext
from emojification import emojify
from gpt_handler import get_gpt_response

HOROSCOPE_DATA_FILE = 'horoscope_data.json'
HOROSCOPE_PROMPT_FILE = 'horoscope_prompt.txt'
DAILY_HOROSCOPE_FILE = 'daily_horoscope.json'
COOLDOWN_PERIOD = 86400  # 24 hours in seconds

def load_horoscope_data():
    try:
        with open(HOROSCOPE_DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(f"Horoscope data loaded successfully: {data}")
            return data
    except Exception as e:
        logging.error(f"Error loading horoscope data: {e}")
        return {"zodiac_signs": [], "predictions": {}}

def load_horoscope_prompt():
    try:
        with open(HOROSCOPE_PROMPT_FILE, 'r', encoding='utf-8') as file:
            prompt = file.read().strip()
            logging.info(f"Horoscope prompt loaded successfully: {prompt}")
            return prompt
    except Exception as e:
        logging.error(f"Error loading horoscope prompt: {e}")
        return "Generate an emojified daily horoscope for all zodiac signs:"

def load_daily_horoscope():
    try:
        if os.path.exists(DAILY_HOROSCOPE_FILE):
            with open(DAILY_HOROSCOPE_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logging.info(f"Daily horoscope loaded successfully: {data}")
                return data
    except Exception as e:
        logging.error(f"Error loading daily horoscope: {e}")
    return {}

def save_daily_horoscope(data):
    try:
        with open(DAILY_HOROSCOPE_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file)
            logging.info("Daily horoscope saved")
    except Exception as e:
        logging.error(f"Error saving daily horoscope: {e}")

HOROSCOPE_DATA = load_horoscope_data()
HOROSCOPE_PROMPT = load_horoscope_prompt()

def generate_daily_horoscope():
    predictions = HOROSCOPE_DATA['predictions']['general']
    horoscope = {sign: random.choice(predictions) for sign in HOROSCOPE_DATA['zodiac_signs']}
    return horoscope

def split_message(text, max_length=4096):
    """Splits a message into chunks that do not exceed the max_length."""
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

def handle_horoscope(update: Update, context: CallbackContext):
    current_time = time.time()

    daily_horoscope_data = load_daily_horoscope()

    # Check if a daily horoscope exists and is still valid
    if 'timestamp' in daily_horoscope_data and current_time - daily_horoscope_data['timestamp'] < COOLDOWN_PERIOD:
        daily_horoscope = daily_horoscope_data['horoscope']
    else:
        # Generate a new daily horoscope
        daily_horoscope = generate_daily_horoscope()
        daily_horoscope_data = {
            'timestamp': current_time,
            'horoscope': daily_horoscope
        }
        save_daily_horoscope(daily_horoscope_data)

    original_horoscope = "\n\n".join([f"{sign}: {prediction}" for sign, prediction in daily_horoscope.items()])
    full_prompt = f"{HOROSCOPE_PROMPT}\n\n{original_horoscope}"
    gpt_response, provider = get_gpt_response(full_prompt, update, context)

    if gpt_response:
        emojified_response = emojify(gpt_response)
        messages = split_message(emojified_response)
    else:
        emojified_original_response = emojify(original_horoscope)
        messages = split_message(emojified_original_response)

    for message in messages:
        update.message.reply_text(message)

# For debugging purposes
if __name__ == "__main__":
    class MockUpdate:
        class Message:
            from_user = type('obj', (object,), {'id': 123456})
            def reply_text(self, text):
                print(f"Replying with text: {text}")
        message = Message()

    class MockContext:
        pass

    update = MockUpdate()
    context = MockContext()
    handle_horoscope(update, context)
