import os
import random
import json
import time
import logging
from telegram import Update
from telegram.ext import CallbackContext
from gpt_handler import get_gpt_response
from emojification import emojify

# Файлы для хранения данных
ITCHIN_FILE = 'itchin.txt'
USER_DATA_FILE = 'user_data.json'
HEXAGRAM_COUNT_FILE = 'hexagram_count.json'
ITCHIN_PROMPT_FILE = 'itchin_prompt.txt'

# Глобальные переменные
hexagram_count = 0
last_user_id = None
last_gpt_response_time = None
last_successful_provider = None

def save_hexagram_count(count):
    try:
        with open(HEXAGRAM_COUNT_FILE, 'w') as f:
            json.dump({'count': count}, f)
        logging.info(f"Hexagram count saved: {count}")
    except Exception as e:
        logging.error(f"Error saving hexagram count: {e}")

def load_hexagram_count():
    try:
        with open(HEXAGRAM_COUNT_FILE, 'r') as f:
            data = json.load(f)
            count = data.get('count', 0)
            logging.info(f"Hexagram count loaded: {count}")
            return count
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error loading hexagram count: {e}")
        return 0

def load_itchin_text():
    try:
        with open(ITCHIN_FILE, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            hexagrams = content.split('&')
            hexagrams = [h.strip() for h in hexagrams if h.strip()]
            return hexagrams
    except Exception as e:
        logging.error(f"Error loading itchin text: {e}")
        return []

HEXAGRAMS = load_itchin_text()

def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
    except Exception as e:
        logging.error(f"Error loading user data: {e}")
    return {}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(data, file)
        logging.info("User data saved")
    except Exception as e:
        logging.error(f"Error saving user data: {e}")

def get_random_hexagram(excluded):
    available_hexagrams = [h for i, h in enumerate(HEXAGRAMS) if str(i + 1) not in excluded]
    if not available_hexagrams:
        excluded.clear()
        available_hexagrams = HEXAGRAMS

    hexagram = random.choice(available_hexagrams)
    return hexagram, HEXAGRAMS.index(hexagram) + 1

def read_file_content(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error(f"{filename} not found.")
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
    return ""

def handle_itchin(update: Update, context: CallbackContext):
    global hexagram_count, last_user_id, last_gpt_response_time, last_successful_provider

    try:
        user_id = str(update.message.from_user.id)
        last_user_id = user_id
        user_data = load_user_data()

        current_time = time.time()
        if user_id in user_data:
            if isinstance(user_data[user_id], float):
                user_data[user_id] = {'timestamp': user_data[user_id], 'excluded': []}
            if current_time - user_data[user_id]['timestamp'] < 86400:
                update.message.reply_text("Вы уже получали гадание сегодня. Попробуйте снова через 24 часа.")
                return

        excluded = user_data.get(user_id, {}).get('excluded', [])
        hexagram, hexagram_number = get_random_hexagram(excluded)

        excluded.append(str(hexagram_number))
        user_data[user_id] = {'timestamp': current_time, 'excluded': excluded}
        save_user_data(user_data)

        original_response = f"{hexagram_number}. {hexagram}"
        hexagram_count += 1
        save_hexagram_count(hexagram_count)
        logging.info(f"Hexagram count incremented to: {hexagram_count}")

        itchin_prompt = read_file_content(ITCHIN_PROMPT_FILE)
        full_prompt = f"{itchin_prompt}\n\n{original_response}"
        g4f_response, provider = get_gpt_response(full_prompt, update, context)

        if g4f_response:
            emojified_response = emojify(g4f_response)
            update.message.reply_text(emojified_response)
            last_gpt_response_time = current_time
            last_successful_provider = provider
            logging.info(f"Updated last_gpt_response_time in handle_itchin: {last_gpt_response_time}")
            logging.info(f"Updated last_successful_provider in handle_itchin: {last_successful_provider}")
        else:
            emojified_original_response = emojify(original_response)
            update.message.reply_text(emojified_original_response)
            last_gpt_response_time = current_time
            last_successful_provider = None
            logging.info(f"Updated last_gpt_response_time in handle_itchin: {last_gpt_response_time}")
            logging.info("No successful provider in handle_itchin")
    except Exception as e:
        logging.error(f"Error in handle_itchin: {e}")

# Для отладки
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
    handle_itchin(update, context)
