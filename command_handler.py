import logging
import time
import os
import json
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from handlers import initialize_variables, load_hexagram_count, handle_taro, handle_diet, handle_horoscope, handle_itchin
from config import LOG_MODE, TOKEN
import config_vars as config

PROMPT_FILE = 'prompt.txt'

def set_log_mode(mode):
    global LOG_MODE
    LOG_MODE = mode
    if mode == 1:
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Log mode enabled")
    else:
        logging.getLogger().setLevel(logging.WARNING)
        logging.info("Log mode disabled")

def read_prompt_file():
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Файл prompt.txt не найден."
    except Exception as e:
        return f"Ошибка чтения файла prompt.txt: {e}"

def write_prompt_file(new_prompt):
    try:
        with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write(new_prompt)
        return "Новый промпт успешно записан."
    except Exception as e:
        return f"Ошибка записи файла prompt.txt: {e}"

def handle_nut(update: Update, context: CallbackContext):
    prompt_content = read_prompt_file()
    update.message.reply_text(prompt_content)

def handle_nutedit(update: Update, context: CallbackContext):
    new_prompt = ' '.join(context.args)
    if new_prompt:
        result = write_prompt_file(new_prompt)
        update.message.reply_text(result)
    else:
        update.message.reply_text("Пожалуйста, укажите новый промпт после команды /nutedit.")

def diag(update: Update, context: CallbackContext):
    current_time = time.time()
    uptime = current_time - config.bot_start_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))

    if config.last_gpt_response_time is not None:
        last_gpt_response_seconds = int(current_time - config.last_gpt_response_time)
    else:
        last_gpt_response_seconds = 'Неизвестно'

    if config.last_successful_provider is None:
        config.last_successful_provider = 'None'

    hexagram_count = load_hexagram_count()

    logging.info(f"Current hexagram count: {hexagram_count}")
    response = (
        f"Статус режимов:\n"
        f"Логирование: {'Включено' if LOG_MODE else 'Выключено'}\n"
        f"Последний ответ g4f: {last_gpt_response_seconds} секунд назад\n"
        f"Последний успешный провайдер g4f: {config.last_successful_provider}\n"
        f"Количество выведенных гексаграмм: {hexagram_count}\n"
        f"Последний пользователь: {config.last_username}\n"
        f"Время работы бота: {uptime_str}\n"
    )

    update.message.reply_text(response)
    if LOG_MODE:
        logging.info("Diag command received. Status sent to user.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет, я Юля! Как я могу помочь вам сегодня?")
    if LOG_MODE:
        logging.info("Start command received")

def logon(update: Update, context: CallbackContext):
    set_log_mode(1)
    update.message.reply_text("Логирование включено.")
    if LOG_MODE:
        logging.info("Logon command received")

def logoff(update: Update, context: CallbackContext):
    set_log_mode(0)
    update.message.reply_text("Логирование выключено.")
    if LOG_MODE:
        logging.info("Logoff command received")

def handle_panic(update: Update, context: CallbackContext):
    if os.path.exists(config.USER_DATA_FILE):
        with open(config.USER_DATA_FILE, 'w') as file:
            json.dump({}, file)
        update.message.reply_text("Файл user_data.json успешно очищен.")
        if LOG_MODE:
            logging.info("User data file cleared by /panic command.")
    else:
        update.message.reply_text("Файл user_data.json не найден.")
        if LOG_MODE:
            logging.warning("User data file not found when /panic command was issued.")
