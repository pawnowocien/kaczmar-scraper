from bs4 import BeautifulSoup
import requests
from . import searcher
from . import llm_chat

URL = 'https://www.kaczmarski.art.pl/tworczosc/wiersze/'
SEARCH_TERMS_PL = ['wiadomości', 'co to']

# Returns a list of all poems on the site
def get_poems():
    response = requests.get(URL)
    main_site = BeautifulSoup(response.text, 'html.parser')

    poems = main_site.find_all('ul', {'class': 'page-list'})[0]
    return poems.find_all('li')

# Checks if there is a signature of Jacek Kaczmarski on the site
def check_author(site):
    sign = site.find('div', {'class': 'fusion-text-2'})
    if sign is None:
        return False
    return 'kaczmarski' in sign.text.lower()

# Returns the date of the poem
def get_date(site):
    sign = site.find('div', {'class': 'fusion-text-2'})
    if sign is None:
        return '-'
    delete_these = [' ', '\n', '\r', 'kaczmarski', 'jacek', ',', 'berkeley', 'osowa', 'konstancin']
    date = sign.text.lower()
    for word in delete_these:
        date = date.replace(word, '')
    if date == '':
        return '-'
    
    print_it = False
    last_char_was_digit = date[0].isdigit()

    tmp = date
    date = ""

    for c in tmp:
        if not (c.isdigit() or c in '.-/'):
            print_it = True
            if last_char_was_digit:
                date += ' '
            last_char_was_digit = False
        else:
            if not last_char_was_digit:
                date += ' '
            last_char_was_digit = True
        date += c

    if print_it:
        print('Words in date:  ', date)
    return date

# Returns a poem with added id
def set_id(poem, _id):
    poem['id'] = str(_id)
    return poem

# Generates a poem with normal attributes
# (name, link, year, text)
def gen_normal_attrs(poem_html):
    _name = poem_html.find('a').text
    _href = poem_html.find('a').get('href')
    _site = BeautifulSoup(requests.get(_href).text, 'html.parser')

    if not check_author(_site):
        print('Skipping:  ', _name, _href)
        return None

    _text = _site.find('div', {'class': 'fusion-text-1'}).text
    _date = get_date(_site)

    return {'name': _name,
            'link': _href,
            'year': _date,
            'text': _text,
            'special_attrs': {}
            }

# Adds special attributes to the poem
# (the ones that require additional processing)
def add_special_attrs(poem):

    poem['special_attrs']['search'] = searcher.get_searches(poem['name'], SEARCH_TERMS_PL, 3)
    poem['special_attrs']['yt_search'] = searcher.yt_search(poem['name'] + ' Jacek Kaczmarski')
    poem['special_attrs']['rating'] = llm_chat.ask_for_rating(poem['text'])

    poem['special'] = True

    return poem