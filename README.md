# julia_tarologEKB
🔮 Юля Таролог Екатеринбург
Юля — Telegram-бот, который делает смешные предсказания по картам Таро, гороскопам, книге перемен И-Цзин и даже даёт советы по диете!

📌 Возможности
🃏 Гадание на Таро – выбирает случайные карты и делает шуточное толкование.

🏯 Гадание по И-Цзин – выдаёт случайную гексаграмму с пародийным объяснением.

♈ Гороскоп – создаёт ежедневные предсказания для знаков зодиака.

🥑 Диеты – даёт юмористические советы по питанию.

🤖 Автоматический ответчик – отвечает на сообщения с упоминанием ключевых слов.

🎭 Эмодзификация – добавляет случайные эмодзи в сообщения.

🚀 Установка и запуск


Настройте токен Telegram-бота:
В файле config.py замените "ТОКЕН" на ваш API-ключ.


Запустите бота:
python main.py

📜 Доступные команды
Бот реагирует на ключевые слова и команды:

Команда	Описание

/start	Начало работы с ботом

/diag	Показать статус бота

/logon	Включить логирование

/logoff	Выключить логирование

/panic	Очистить данные пользователей


Бот также автоматически реагирует на ключевые слова:

"таро" – запускает гадание на Таро
"гороскоп" – показывает предсказание по знаку зодиака
"ицзин" – выдаёт гексаграмму из книги перемен
"диета" – даёт рекомендации по питанию
🛠 Используемые технологии
Python
Telegram Bot API
GPT (g4f) – генерация забавных ответов
JSON – хранение данных
