import os
from pathlib import Path


DEF_PATH = Path(os.path.dirname(__file__))

DEF_LIST_NAME = 'list'
DEF_LIST_PATH = DEF_PATH / DEF_LIST_NAME

LIST_DESC = "Lista zawierająca część wierszy Jacka Kaczmarskiego."

SCRAPED_SITE = '[kaczmarski.art.pl](https://www.kaczmarski.art.pl/tworczosc/wiersze/)'
MAIN_DESC = ("Strona poświęcona jest **twórczości** Jacka Kaczmarskiego, a dokładniej części jego wierszy. "
        f"Dane zostały pobrane z {SCRAPED_SITE}, "
        "a następnie przetworzone przy użyciu różnych narzędzi.\n\n"
        f"Każdy utwór zawiera link do oryginalnego tekstu oraz rok powstania (o ile taki został określony na stronie {SCRAPED_SITE}). " 
        "Ze względu na ograniczenia wyszukiwania w Google i YouTube oraz "
        "limit dziennych zapytań do OpenRoutera, jeszcze nie wszystkie wiersze zawierają dodatkowe informacje.\n\n"
        '[Lista utworów](list.md)\n\n'
        '[![Jacek Kaczmarski](https://upload.wikimedia.org/wikipedia/commons/d/d8/Jacek_Kaczmarski.jpg)]'
        '(https://pl.wikipedia.org/wiki/Jacek_Kaczmarski "Jacek Kaczmarski")')


# Googlesearch-python sometimes returns bugged results (urls aren't links)
def is_google_search_bugged(s):
    if 'http' not in s['url'] or 'search?num=' in s['url']:
        return True
    return False


# These characters could potentially break markdown formatting
BAD_CHARS = "\\[]{}()|\"*"

def erase_bad_chars(text):
    res = ""
    for c in text:
        if not c in BAD_CHARS:
            res += c
    return res

# Some titles start with three stars, which is a markdown formatting character
# This function replaces the starts with escaped ones
def replace_stars(text):
    return text.replace("*", "\\*")


# From a list of sites, generates a markdown string with links to them
# Example:
# [Strona główna](index.md) >> [Lista utworów](list.md) >> ...
def get_sites_path(sites):
    res = ''

    for site in sites:
        res += f'[{site[0]}]({site[1]}) >> '
    res = res[:-4] + '\n\n---\n\n'

    return res

# Generates index.md
def gen_index_md(filename, title, text, web_path, dir=None):
    if dir:
        path = dir / filename
    else:
        path = DEF_PATH / filename
    with open(path, 'w', encoding='UTF-8') as file:
        web_path = get_sites_path(web_path)
        file.write(f'{web_path}'
                    f'# {title}\n\n'
                    f'{text}\n\n')
    return path

# Adds leading zeros to date parts
def fix_date_format(date):
    if date == '-':
        return '?'
    date = date.split('.')
    ans = ""
    for w in date:
        if len(w) == 1:
            ans += '0'
        ans += w + '.'
    return ans[:-1]

# Checks how many special poems are in the list
def check_progress(poems):
    total = len(poems)
    done = 0
    for poem in poems:
        if poem['special']:
            done += 1
    return done, total

# Generates list.md
def gen_list_md(filename, title, text, _list, web_path, dir=None):
    def write_item(file, item):
        special = 'Tak' if item.get('special', False) else 'Nie'
        name = item['name']
        file.write(f'**{replace_stars(name)}** | '
                   f'{fix_date_format(item["year"])} | '
                   f'{item["id"]} | {special} | '
                   f'[Podstrona]({DEF_LIST_NAME}/{item["id"]}.md) | '
                   f'[kaczmarski.art.pl]({item["link"]})\n')

    if dir:
        path = dir / filename
    else:
        path = DEF_PATH / filename

    with open(path, 'w', encoding='UTF-8') as file:
        web_path = get_sites_path(web_path)
        done, total = check_progress(_list)
        progress = f'Postęp: {done}/{total} ({100 * (done/total):.2f} %)'
        print(progress)

        file.write(f'{web_path}'
                    f'# {title}\n\n'
                    f'{text}\n\n'
                    f'{progress}\n\n'
                    'Tytuł | Data Utworzenia | Id | Dodatkowe Informacje | Link Wewnętrzny | Link Zewnętrzny\n'
                    '--- | ---: | ---: | ---: | ---: | ---:\n')
        for item in _list:
            write_item(file, item)
    return path



# SINGLE POEM SITE GENERATION

# Generates video embed from youtube search result
def gen_yt_embed(yt_element):
    link = yt_element['url']
    yt_id = link[32:]
    return ('<iframe '
            'width="560" height="315" '
            f'src="https://www.youtube.com/embed/{yt_id}?si=IdontcarewhotheIRSsendsImnotpayingtaxes" '
            'title="YouTube video player" '
            'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>'
            '</iframe>\n\n')

# Generates youtube search results section
def gen_yt_search_text(element):
    text = '## Rezultaty wyszukiwania na YouTube\n\n'
    for i in range(3):
        text += gen_yt_embed(element['special_attrs']['yt_search'][i])
    return text


# Generates llm rating section
def gen_llm_text(element):
    return ('## Ocena wystawiona przez Google Gemini\n\n' + element['special_attrs']['rating'])


# Generates single google search result text
def gen_single_google_search_text(google_search_item):
    title = str(google_search_item['title']).strip()

    if title.startswith("***"):
        title = erase_bad_chars(title)
        title = f"\\*\\*\\* {title[1:]}"
    else:
        title = erase_bad_chars(title)
    url = google_search_item['url']
    desc = erase_bad_chars(google_search_item['desc'])

    if title == '':
        return f'- <{url}>\n'
    
    if desc == '':
        return ( f'- **{title}**\n\n'
            f'   <{url}>\n')
    
    return ( f'- **{title}**\n\n'
            f'   {desc}\n\n'
            f'   <{url}>\n')

# Generates google search results section
def gen_google_search_text(element, amount=4):
    title = replace_stars(element['name'])

    text = f'\n\n## {title} — odpowiedzi z Google\n\n'

    title = f'"{title}"'
    for key, _list in element['special_attrs']['search'].items():
        if key == '':
            key_title = title
        else:
            key_title = title + ' — ' + key.capitalize()
        text += f'### {key_title}\n\n'
        good_searches = []
        for google_search_thingy in _list:
            if not is_google_search_bugged(google_search_thingy):
                good_searches.append(google_search_thingy)
        if len(good_searches) < amount:
            print(f"WARNING: Too few google searches for {element['id']} ({len(good_searches)})")
        for google_search_element in good_searches[:amount]:
            text += gen_single_google_search_text(google_search_element)
        text += '\n'
    return text

# Generates single poem site
def gen_item_md(filename, element, web_path, dir=None):
    assert isinstance(element, dict)
    if dir:
        path = dir / DEF_LIST_NAME / filename
    else:
        path = DEF_LIST_PATH / filename

    title = element['name']

    web_path.append((replace_stars(element['name']), filename))

    with open(path, 'w', encoding='UTF-8') as file:
        file.write(get_sites_path(web_path))
        file.write(f'# {title}\n\n')
        link = element['link']
        file.write(f'Tekst: [kaczmarski.art.pl]({link})\n\n')
        if element['special']:
            file.write(gen_yt_search_text(element))

            file.write(gen_llm_text(element))

            file.write(gen_google_search_text(element))

        else:
            file.write("Element pospolity, nic ciekawego.")


# DEFAULT MARDKOWN GENERATION
def generate_default(poems, dir=None):

    for poem in poems:
        gen_item_md(f'{poem["id"]}.md', poem, [('Strona główna', '../index.md'), ('Lista utworów', '../list.md')], dir)

    gen_list_md('list.md', 'Wiersze Jacka Kaczmarskiego', LIST_DESC, poems, [('Strona główna', 'index.md'), ('Lista utworów', 'list.md')], dir)

    gen_index_md('index.md', 'Wiersze Jacka Kaczmarskiego', MAIN_DESC, [('Strona główna', 'index.md')], dir)