import os
import random
import json
from pathlib import Path
from . import data_processor
from . import md_gen

MAIN_DIR = Path(os.path.dirname(__file__)).parent

DOCS_DIR = MAIN_DIR / 'docs'

JSON_PATH = MAIN_DIR / 'cache'
JSON_PATH_LIST = JSON_PATH / 'single_poems'
JSON_BASIC_DATA_FILENAME = 'all_poems.json'

# For a list of poems with basic data (no special attributes)
# Saves the list to a json file
def save_basic_data(poem_list):
    print(poem_list)
    path = JSON_PATH / JSON_BASIC_DATA_FILENAME
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(poem_list))

# Returns list of poems with basic data
# From the json file
def get_all_poems_data():
    all_poems = None
    path = os.path.join(JSON_PATH, JSON_BASIC_DATA_FILENAME)
    if os.path.exists(path):
        with open(path, 'r', encoding='UTF-8') as f:
            all_poems = json.load(f)
    return all_poems

# Returns the path to the json file with the poem of the given id
def get_single_json_path(id):
    return JSON_PATH_LIST / (str(id) + '.json')

# Saves a single poem to its json file
def save_json(poem):
    path = get_single_json_path(poem['id'])

    if os.path.exists(path):
        with open(path, 'r', encoding='UTF-8') as f:
            old_poem = json.load(f)
            if old_poem['special']:
                return

    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(poem, f)

# Checks if the poem of the given id is saved
def is_poem_saved(poem):
    path = get_single_json_path(poem['id'])
    return os.path.isfile(path)

# Checks if the poem of the given id has special attributes defined
def is_poem_special(poem):
    path = get_single_json_path(poem['id'])
    with open(path, 'r', encoding='UTF-8') as f:
        poem = json.load(f)
        return poem['special']

# Generates a list of poems with their basic data
def gen_poems_basic():
    poems = get_all_poems_data()

    if poems is None:
        poems = []
        for poem_html in data_processor.get_poems():
            poem = data_processor.gen_normal_attrs(poem_html)

            if not poem is None:
                poems.append(poem)
        save_basic_data(poems)

    poems.sort(key=lambda x: x['name'])

    for i in range(len(poems)):
        poems[i] = data_processor.set_id(poems[i], i)

    return poems

# Saves the poems that were not saved yet
def save_the_rest(the_rest):
    for poem in the_rest:
        if is_poem_saved(poem):
            continue
        poem['special'] = False
        save_json(poem)
        print(f"{poem['id']} was saved")

# Tries to generate poems with special attributes
# Then saves them
def save_poems():
    poems = gen_poems_basic()
    random.shuffle(poems) # To randomize the order of processing

    while len(poems) > 0:
        poem = poems.pop()

        if not is_poem_saved(poem) or not is_poem_special(poem):
            try:
                poem = data_processor.add_special_attrs(poem)
                save_json(poem)

                print(f"{poem['id']} got special attributes")

            except Exception as e:
                print(e)
                poems.append(poem)
                break
    save_the_rest(poems)

# Generates json files
# Then generates markdown files from them
def generate_from_files():
    save_poems()

    chosen_poems = []

    for file in os.listdir(JSON_PATH_LIST):
        path = JSON_PATH_LIST / file
        with open(path, 'r', encoding='UTF-8') as f:
            chosen_poems.append(json.load(f))

    chosen_poems.sort(key=lambda x: int(x['id']))

    md_gen.generate_default(chosen_poems, dir=DOCS_DIR)