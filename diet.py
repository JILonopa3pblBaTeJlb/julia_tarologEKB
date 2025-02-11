import json
import random
import logging
from telegram import Update
from telegram.ext import CallbackContext
from gpt_handler import get_gpt_response
from emojification import emojify

# Константы
DIET_DATA_FILE = 'diet_data.json'
DIET_PROMPT_FILE = 'diet_prompt.txt'

# Функция загрузки данных диет
def load_diet_data():
    try:
        with open(DIET_DATA_FILE, 'r', encoding='utf-8') as file:
            diet_data = json.load(file)
            logging.info(f"Diet data loaded successfully: {diet_data}")
            return diet_data
    except Exception as e:
        logging.error(f"Error loading diet data: {e}")
        return {"foods": []}

DIET_DATA = load_diet_data()

# Функция загрузки промпта диет
def load_diet_prompt():
    try:
        with open(DIET_PROMPT_FILE, 'r', encoding='utf-8') as file:
            prompt = file.read().strip()
            logging.info(f"Diet prompt loaded successfully: {prompt}")
            return prompt
    except Exception as e:
        logging.error(f"Error loading diet prompt: {e}")
        return "Generate a diet plan:"

DIET_PROMPT = load_diet_prompt()

# Функция получения случайных продуктов
def get_random_foods(food_list, count):
    return random.sample(food_list, count)

# Основная функция обработки диет
def handle_diet(update: Update, context: CallbackContext):
    try:
        food_list = DIET_DATA.get('foods', [])
        if not food_list:
            update.message.reply_text("No diet data available.")
            return

        eat_foods = get_random_foods(food_list, 5)
        avoid_foods = get_random_foods([food for food in food_list if food not in eat_foods], 5)

        original_response = f"Кушайте: {', '.join(eat_foods)}\nНе кушайте: {', '.join(avoid_foods)}"
        
        full_prompt = f"{DIET_PROMPT}\n\n{original_response}"
        g4f_response, provider = get_gpt_response(full_prompt, update, context)

        if g4f_response:
            emojified_response = emojify(g4f_response)
            update.message.reply_text(emojified_response)
        else:
            emojified_original_response = emojify(original_response)
            update.message.reply_text(emojified_original_response)
            
    except Exception as e:
        logging.error(f"Error in handle_diet: {e}")
        update.message.reply_text("Произошла ошибка при генерации плана диеты.")

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
    handle_diet(update, context)
