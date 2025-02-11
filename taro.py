import json
import os
import random
import logging
import time
from telegram import Update
from telegram.ext import CallbackContext
from gpt_handler import get_gpt_response
from emojification import emojify

# Константы
TARO_DATA_FILE = 'taro_data.json'
TARO_PROMPT_FILE = 'taro_prompt.txt'
COOLDOWN_PERIOD = 60  # Cooldown period in seconds

# Глобальная переменная для хранения времени последнего запроса
last_taro_request_time = None

# Функция загрузки данных Таро
def load_taro_data():
    try:
        with open(TARO_DATA_FILE, 'r', encoding='utf-8') as file:
            taro_data = json.load(file)
            logging.info(f"Taro data loaded successfully: {taro_data}")
            return taro_data
    except Exception as e:
        logging.error(f"Error loading taro data: {e}")
        return []

# Функция загрузки промпта Таро
def load_taro_prompt():
    try:
        with open(TARO_PROMPT_FILE, 'r', encoding='utf-8') as file:
            prompt = file.read().strip()
            logging.info(f"Taro prompt loaded successfully: {prompt}")
            return prompt
    except Exception as e:
        logging.error(f"Error loading taro prompt: {e}")
        return "Предсказание Таро:"

# Инициализация данных Таро и промпта
TARO_CARDS = load_taro_data()
TARO_PROMPT = load_taro_prompt()

# Функция выбора случайных карт Таро
def get_random_taro_cards(count=3):
    if count > len(TARO_CARDS):
        count = len(TARO_CARDS)  # Ограничить количество доступным числом карт
    selected = random.sample(TARO_CARDS, count)
    print(f"Selected {count} cards: {selected}")
    return selected

# Основная функция обработки Таро
def handle_taro(update: Update, context: CallbackContext):
    global last_taro_request_time

    current_time = time.time()

    # Проверка кулдауна
    if last_taro_request_time and current_time - last_taro_request_time < COOLDOWN_PERIOD:
        update.message.reply_text('💅')
        return

    last_taro_request_time = current_time

    try:
        count = int(context.args[0]) if context.args else 3
        if count < 1:
            count = 3  # По умолчанию 3 карты, если указано меньше 1

        selected_cards = get_random_taro_cards(count)
        logging.info(f"Selected cards: {selected_cards}")
        original_response = "Таро расклад:\n\n" + "\n\n".join([f"{card['name']}: {card['meaning']}" for card in selected_cards])
        
        # Формируем полный промпт для g4f
        full_prompt = f"{TARO_PROMPT}\n\n{original_response}"
        g4f_response, provider = get_gpt_response(full_prompt, update, context)
        
        if g4f_response:
            emojified_response = emojify(g4f_response)
            update.message.reply_text(emojified_response)
        else:
            emojified_original_response = emojify(original_response)
            update.message.reply_text(emojified_original_response)
            
    except Exception as e:
        logging.error(f"Error in handle_taro: {e}")
        update.message.reply_text("Произошла ошибка при получении расклада Таро.")

# Для отладки
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
    handle_taro(update, context)
