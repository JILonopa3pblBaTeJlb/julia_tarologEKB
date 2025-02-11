# emojification.py
import random
import logging
from config import EMOJIS

def emojify(text, emojis=EMOJIS, bypass=False):
    if bypass:
        logging.info("Bypassing emojification")
        return text

    # Remove asterisks and double spaces from the text
    text = text.replace('*', '')
    while '  ' in text:
        text = text.replace('  ', ' ')

    words = text.split()
    emojified_text = []

    i = 0
    while i < len(words):
        emojified_text.append(words[i])
        if (i + 1) < len(words):  # Ensure not to add emoji at the end
            if random.random() < 0.35:  
                step = 2
            else:
                step = 3  # 1% вероятность после каждого третьего слова

            if (i + step) < len(words):
                if step == 3 and random.random() < 0.1:
                    emoji = random.choice(emojis)
                    emojified_text.append(emoji)
                    logging.info(f"Added emoji: {emoji}")
                elif step == 2:
                    emoji = random.choice(emojis)
                    emojified_text.append(emoji)
                    logging.info(f"Added emoji: {emoji}")
        i += 1

    return ' '.join(emojified_text)

# For debugging purposes
if __name__ == "__main__":
    text = "Я всегда радостно встречаю своих клиентов в Екатеринбурге!  *"
    logging.basicConfig(level=logging.INFO)
    print(emojify(text))
