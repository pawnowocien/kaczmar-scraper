import os
from pathlib import Path
import utils

# DEF_NAME = 'md_files'
# DEF_PATH = Path(os.path.dirname(__file__)) / DEF_NAME

DEF_PATH = Path(os.path.dirname(__file__))

DEF_LIST_NAME = 'list'
DEF_LIST_PATH = DEF_PATH / DEF_LIST_NAME

LIST_DESC = "Lista zawierająca część wierszy Jacka Kaczmarskiego."

STRONA_KAP = '[kaczmarski.art.pl](https://www.kaczmarski.art.pl/tworczosc/wiersze/)'
MAIN_DESC = ("Strona poświęcona jest **twórczości** Jacka Kaczmarskiego, a dokładniej części jego wierszy. "
        f"Dane zostały pobrane z {STRONA_KAP}, "
        "a następnie przetworzone przy użyciu różnych narzędzi.\n\n"
        f"Każdy utwór zawiera link do oryginalnego tekstu oraz rok powstania (o ile taki został określony na stronie {STRONA_KAP}). " 
        "Ze względu na ograniczenia wyszukiwania w Google i YouTube oraz "
        "limit dziennych zapytań do OpenRoutera, jeszcze nie wszystkie wiersze zawierają dodatkowe informacje.\n\n"
        '[Lista utworów](list.md)\n\n'
        '[![Jacek Kaczmarski](https://upload.wikimedia.org/wikipedia/commons/d/d8/Jacek_Kaczmarski.jpg)](https://pl.wikipedia.org/wiki/Jacek_Kaczmarski "Jacek Kaczmarski")')

def is_google_search_bugged(s):
    if 'http' not in s['url'] or 'search?num=' in s['url']:
        return True

BAD_CHARS = "\\[]{}()|\"*"

def char_ok(char):
    return not char in BAD_CHARS

def replace_bad_chars(text):
    res = ""
    for c in text:
        if char_ok(c):
            res += c
    return res

def replace_stars(text):
    return text.replace("*", "\\*")

# if not DEF_PATH.exists():
#     DEF_PATH.mkdir()

# if not DEF_LIST_PATH.exists():
#     DEF_LIST_PATH.mkdir()

def get_sites_path(sites):
    res = ''

    for site in sites:
        res += f'[{site[0]}]({site[1]}) >> '
    res = res[:-4] + '\n\n'
    res += '---\n\n'

    return res


def gen_main_md(filename, title, text, web_path, dir=None):
    if dir:
        path = dir / filename
    else:
        path = DEF_PATH / filename
    with open(path, 'w', encoding='UTF-8') as file:
        file.write(get_sites_path(web_path))
        file.write(f'# {title}\n\n')
        file.write(f'{text}\n\n')
    return path


def gen_list_md(filename, title, text, _list, web_path, dir=None):
    def write_item(file, item):
        special = 'Tak' if item.get('special', False) else 'Nie'
        name = item['name']
        file.write(f'**{replace_stars(name)}** | {utils.fix_date_format(item["year"])} | {item["id"]} | {special} | [Podstrona]({DEF_LIST_NAME}/{item["id"]}.md) | [kaczmarski.art.pl]({item["link"]})\n')

    if dir:
        path = dir / filename
    else:
        path = DEF_PATH / filename

    with open(path, 'w', encoding='UTF-8') as file:
        file.write(get_sites_path(web_path))
        file.write(f'# {title}\n\n')
        file.write(f'{text}\n\n')
        file.write('Tytuł | Data Utworzenia | Id | Dodatkowe Informacje | Link Wewnętrzny | Link Zewnętrzny\n')
        file.write('--- | ---: | ---: | ---: | ---: | ---:\n')
        for item in _list:
            write_item(file, item)
    return path





def gen_yt_embed(yt_element, pure_md = True):
    link = yt_element['url']
    yt_id = link[32:]
    if pure_md:
        yt_title = replace_bad_chars(yt_element['title'])

        md_text = f'[![{yt_title}]'
        md_text += f'(http://img.youtube.com/vi/{yt_id}/0.jpg)]'
        md_text += f'({link} "{yt_title}")\n\n'
        return md_text
    else:
        return ('<iframe '
        'width="560" height="315" '
        f'src="https://www.youtube.com/embed/{yt_id}?si=IdontcarewhotheIRSsendsImnotpayingtaxes" '
        'title="YouTube video player" '
        'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>'
        '</iframe>\n\n')

def gen_yt_search_text(element, pure_md = True):
    text = '## Rezultaty wyszukiwania na YouTube\n\n'
    for i in range(3):
        text += gen_yt_embed(element['special_attrs']['yt_search'][i], pure_md=pure_md)
    return text




def gen_llm_text(element):
    return ('## Ocena wystawiona przez google gemini\n\n' + element['special_attrs']['rating'])




def gen_single_google_search_text(google_search_item):
    title = google_search_item['title']

    if title.startswith("***"):
        title = replace_bad_chars(title)
        title = f"\\*\\*\\* {title[1:]}"
    else:
        title = replace_bad_chars(title)
    url = google_search_item['url']
    desc = replace_bad_chars(google_search_item['desc'])

    if title == '':
        return f'- <{url}>\n'
    
    if desc == '':
        return ( f'- **{title}**\n\n'
            f'   <{url}>\n')
    
    return ( f'- **{title}**\n\n'
            f'   {desc}\n\n'
            f'   <{url}>\n')

def gen_google_search_text(element, amount=4):
    title = replace_stars(element['name'])

    text = f'\n\n## {title} — odpowiedzi z google search\n\n'

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
            raise Exception(f"TOO FEW WORKING GOOGLE SEARCHES ({element['id']})")
        for google_search_element in good_searches[:amount]:
            text += gen_single_google_search_text(google_search_element)
        text += '\n'
    return text

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
            file.write(gen_yt_search_text(element, pure_md=False))

            file.write(gen_llm_text(element))

            file.write(gen_google_search_text(element))

        else:
            file.write("Element pospolity, nic ciekawego.")


def generate_default(poems, dir=None):

    for poem in poems:
        gen_item_md(f'{poem["id"]}.md', poem, [('Strona główna', '../index.md'), ('Lista utworów', '../list.md')], dir)

    gen_list_md('list.md', 'Wiersze Jacka Kaczmarskiego', LIST_DESC, poems, [('Strona główna', 'index.md'), ('Lista utworów', 'list.md')], dir)

    gen_main_md('index.md', 'Wiersze Jacka Kaczmarskiego', MAIN_DESC, [('Strona główna', 'index.md')], dir)