import os
import random
import utils
import json
import md_gen
from pathlib import Path

MAIN_DIR = Path(os.path.dirname(__file__)).parent

DOCS_DIR = MAIN_DIR / 'docs'

JSON_PATH = MAIN_DIR / 'cache'
JSON_PATH_LIST = JSON_PATH / 'single_poems'

JSON_LIST_FILENAME = 'all_poems.json'

def save_all_poems_data(poems):
    path = JSON_PATH / JSON_LIST_FILENAME
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(poems))

def get_all_poems_data():
    all_poems = None
    path = os.path.join(JSON_PATH, JSON_LIST_FILENAME)
    if os.path.exists(path):
        with open(path, 'r', encoding='UTF-8') as f:
            all_poems = json.load(f)
    return all_poems

def get_single_json_path(id):
    return JSON_PATH_LIST / (str(id) + '.json')


def save_json(poem):
    path = get_single_json_path(poem['id'])

    if os.path.exists(path):
        with open(path, 'r', encoding='UTF-8') as f:
            old_poem = json.load(f)
            if old_poem['special']:
                return

    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(poem, f)

def is_poem_saved(poem):
    path = get_single_json_path(poem['id'])
    return os.path.isfile(path)

def is_poem_special(poem):
    # return True
    path = get_single_json_path(poem['id'])
    with open(path, 'r', encoding='UTF-8') as f:
        poem = json.load(f)
        return poem['special']

def gen_poems_with_ids():
    poems = get_all_poems_data()

    if poems is None:
        poems = []
        for poem_html in utils.get_poems():
            poem = utils.gen_normal_attrs(poem_html)

            if not poem is None:
                poems.append(poem)
        save_all_poems_data(poems)


    poems.sort(key=lambda x: x['name'])

    for i in range(len(poems)):
        poems[i] = utils.set_id(poems[i], i)

    random.shuffle(poems)

    return poems

def weak_better_attrs(poem):
    poem = utils.gen_special_attrs(poem)
    poem['special'] = True
    return poem


def save_the_rest(the_rest):
    for poem in the_rest:
        if is_poem_saved(poem):
            continue
        poem['special'] = False
        save_json(poem)
        print('Saved ' + poem['id'])

def save_poems():
    poems = gen_poems_with_ids()
    while len(poems) > 0:
        poem = poems.pop()

        if not is_poem_saved(poem) or not is_poem_special(poem):
            try:
                poem = weak_better_attrs(poem)
                save_json(poem)


                print(f"{poem['id']} saved")

            except Exception as e:
                print(e)
                poems.append(poem)
                break
    save_the_rest(poems)

def generate_from_files():
    # save_poems()

    chosen_poems = []

    for file in os.listdir(JSON_PATH_LIST):
        path = JSON_PATH_LIST / file
        with open(path, 'r', encoding='UTF-8') as f:
            chosen_poems.append(json.load(f))

    chosen_poems.sort(key=lambda x: int(x['id']))

    md_gen.generate_default(chosen_poems, dir=DOCS_DIR)

generate_from_files()