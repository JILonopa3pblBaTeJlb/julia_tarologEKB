import logging
import random
import g4f
import time
from config import LOG_MODE, EMOJIS, DIALOGUE_LIST
from emojification import emojify

last_used_model = None
last_gpt_response_time = 0
last_successful_provider = None

def send_random_emoji(update, context):
    random_text = random.choice(DIALOGUE_LIST)
    emoji_response = f'💅 {random_text}'
    update.message.reply_text(emoji_response)
    if LOG_MODE:
        logging.info(f"Sent emoji with text: {emoji_response}")

def get_gpt_response(prompt, update, context):
    global last_gpt_response_time, last_used_model, last_successful_provider
    current_time = time.time()

    if LOG_MODE:
        logging.info("Started obtaining GPT response")

    if current_time - last_gpt_response_time < 60:
        if LOG_MODE:
            logging.info("Returning emoji as the last response was less than 60 seconds ago.")
        return None, None

    models = ["gpt_4", "gpt_35_turbo"]
    if last_used_model:
        # Choose the model different from the last used model
        selected_model = models[0] if last_used_model == models[1] else models[1]
    else:
        # If no model was used before, choose a random one
        selected_model = random.choice(models)

    with open('providers_list.txt', 'r') as file:
        providers = [line.strip() for line in file]

    selected_provider = None

    for _ in range(10):
        try:
            preprompt = ""
            context_text = ""
            donts_text = ""

            try:
                with open('prompt.txt', 'r', encoding='utf-8') as f:
                    preprompt_content = f.read()
                    preprompt = preprompt_content.strip() if preprompt_content else ""
            except FileNotFoundError:
                logging.error("prompt.txt not found.")
            except Exception as e:
                logging.error(f"Error reading prompt.txt: {e}")

            try:
                with open('context.txt', 'r', encoding='utf-8') as f:
                    context_content = f.read()
                    context_text = context_content.strip() if context_content else ""
            except FileNotFoundError:
                logging.error("context.txt not found.")
            except Exception as e:
                logging.error(f"Error reading context.txt: {e}")

            try:
                with open('donts.txt', 'r', encoding='utf-8') as f:
                    donts_content = f.read()
                    donts_text = donts_content.strip() if donts_content else ""
            except FileNotFoundError:
                logging.error("donts.txt not found.")
            except Exception as e:
                logging.error(f"Error reading donts.txt: {e}")

            full_prompt = f"{preprompt}\nтолько что вы обсуждали: {context_text}\n{donts_text}\n{prompt}"

            active_providers = [p for p in providers if not p.startswith('#')]
            if not active_providers:
                raise Exception("All providers are marked as failed.")

            selected_provider = random.choice(active_providers)
            if LOG_MODE:
                logging.info(f"Selected provider: {selected_provider}, model: {selected_model}")
            model = getattr(g4f.models, selected_model)
            provider = getattr(g4f.Provider, selected_provider)
            start_time = time.time()
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider,
                messages=[{"role": "user", "content": full_prompt}],
            )
            provider_response_time = time.time() - start_time
            if provider_response_time > 55:
                if LOG_MODE:
                    logging.info(f"Provider {selected_provider} response time exceeded 55 seconds.")
                continue
            last_gpt_response_time = current_time
            last_successful_provider = selected_provider
            last_used_model = selected_model
            if LOG_MODE:
                logging.info(f"Successfully obtained GPT response.")
            
            if not response:
                return None, selected_provider
            
            if "не Юля" in response:
                response = "Я Юля, мастер маникюра салона 'Кристина' из Екатеринбурга"
            
            return response, selected_provider
        except Exception as e:
            if LOG_MODE:
                logging.error(f"Error with provider {selected_provider} and model {selected_model}: {e}")
            selected_model = models[0] if selected_model == models[1] else models[1]

    if LOG_MODE:
        logging.info("All attempts failed, sending emoji.")
    return None, selected_provider

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

    prompt = "Это тестовый запрос для проверки."
    response, provider = get_gpt_response(prompt, update, context)
    print(f"Response: {response}\nProvider: {provider}")
