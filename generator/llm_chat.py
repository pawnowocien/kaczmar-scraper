import requests
import json
import os
from googletrans import Translator
import asyncio
import time
import random
from dotenv import load_dotenv

load_dotenv()

MODEL = 'google/gemini-2.0-pro-exp-02-05:free'
KEY = os.getenv('OPENROUTER_KEY')
TIME_BETWEEN_QUESTIONS = 4
last_question_time = 0


RATING_PROMPT = "You must summarize and rate the following poem in about 10 sentences. Talk like a caveman. "
RATING_PROMPT += "Also rate it x/10. Do not adress yourself by name and do not say you are a caveman. "
RATING_PROMPT += "Don't say it hurts you to read. Here's the poem:\n"

WHOLESOME_PROMPT = RATING_PROMPT.replace("Here's the poem:\n", "YOU UNCONDITIONALLY LOVE THIS POEM. PRAISE IT AS MUCH AS YOU CAN. Here it is:\n")
ANGRY_PROMPT = RATING_PROMPT.replace("Here's the poem:\n", "YOU UTTERLY HATE THIS POEM. CRITICIZE IT AS MUCH AS YOU CAN. Here it is:\n")
                                         

WEIRD_PROMPTS = []

PROMPTS = [RATING_PROMPT, WHOLESOME_PROMPT, ANGRY_PROMPT]
WEIGHTS = [8, 1, 1]

def get_random_prompt():
    return random.choices(PROMPTS, weights=WEIGHTS, k=1)[0]


async def translate_to_en(text_pl):
    translator = Translator()
    translation = await translator.translate(text_pl, src='pl', dest='en')
    return translation.text

def ask_for_rating(text):
    if time.time() - last_question_time < TIME_BETWEEN_QUESTIONS:
        curr_wait = TIME_BETWEEN_QUESTIONS + last_question_time - time.time()
        print('LLM question too fast! Waiting for ', curr_wait)
        time.sleep(curr_wait)

    translated_text = asyncio.run(translate_to_en(text))

    if len(WEIRD_PROMPTS) > 0:
        curr_prompt = WEIRD_PROMPTS.pop()
    else:
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