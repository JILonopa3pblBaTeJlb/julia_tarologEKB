# config_vars.py

import time

# Global variables initialization
bot_start_time = time.time()
last_gpt_response_time = None
hexagram_count = 0
last_user_id = None
last_username = None
last_successful_provider = None

# File paths
HEXAGRAM_COUNT_FILE = 'hexagram_count.json'
USER_DATA_FILE = 'user_data.json'
