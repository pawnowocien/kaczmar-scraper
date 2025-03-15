import requests
import json
import os
from googletrans import Translator
import asyncio
import time
import random
from dotenv import load_dotenv


load_dotenv()
KEY = os.getenv('API_KEY')

MODEL = 'google/gemini-2.0-pro-exp-02-05:free'

# For rate limiting
# Openrouter allows ~20 requests per minute. 4 seconds between questions should be safe
TIME_BETWEEN_QUESTIONS = 4
last_question_time = 0

RATING_PROMPT = ("You must summarize and rate the following poem in about 10 sentences. Talk like a caveman. "
                "Also rate it x/10. Do not adress yourself by name and do not say you are a caveman. "
                "Don't say it hurts you to read. Here's the poem:\n")

WHOLESOME_PROMPT = RATING_PROMPT.replace("Here's the poem:\n", "YOU UNCONDITIONALLY LOVE THIS POEM. PRAISE IT AS MUCH AS YOU CAN. Here it is:\n")
ANGRY_PROMPT = RATING_PROMPT.replace("Here's the poem:\n", "YOU UTTERLY HATE THIS POEM. CRITICIZE IT AS MUCH AS YOU CAN. Here it is:\n")
PROMPTS = [RATING_PROMPT, WHOLESOME_PROMPT, ANGRY_PROMPT]
WEIGHTS = [8, 1, 1]


def get_random_prompt():
    return random.choices(PROMPTS, weights=WEIGHTS, k=1)[0]

async def trans_pl_to_en(text_pl):
    translator = Translator()
    translation = await translator.translate(text_pl, src='pl', dest='en')
    return translation.text


# Generates a random summary and rating for a given poem
# The given text should be written in Polish
# The function returns text in English
def ask_for_rating(text):
    # For rate limiting
    if time.time() - last_question_time < TIME_BETWEEN_QUESTIONS:
        curr_wait = TIME_BETWEEN_QUESTIONS + last_question_time - time.time()
        print('LLM question too fast! Waiting for ', curr_wait)
        time.sleep(curr_wait)

    translated_text = asyncio.run(trans_pl_to_en(text))
    curr_prompt = get_random_prompt()
    content = curr_prompt + translated_text

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + KEY,
        },
        data=json.dumps({
            "model": MODEL,
            "messages": [
            {
                "role": "user",
                "content": content
            }
            ]
        })
    )

    response_data = response.json()

    if 'choices' in response_data.keys():
        return response_data['choices'][0]['message']['content']

    raise Exception('LLM dead: ' + json.dumps(response_data))