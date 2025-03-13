import time
from googlesearch import search as google_search
import re
import requests
from bs4 import BeautifulSoup
import random

last_yt_search_time = 0

TIME_BETWEEN_SEARCHES = (2, 4)
TIME_BETWEEN_GOOGLE_SEARCHES = (1, 2)
MAX_RETRIES = 1

def wait_for(_range):
    time.sleep(random.random() * (_range[1] - _range[0]) + _range[0])

def search(name, term, num):
    search_term = name + ' ' + term
    res = []
    retries = 0
    while True:
        try:
            # for found_site in google_search(search_term, num_results=num * 2, unique=True, advanced=True):
            #     res.append(found_site.url)
            # for url in google_search(search_term, stop=num):
            #     res.append(url)
            google_search_thingies = google_search(search_term, num_results=num * 2, unique=True, advanced=True)

            res = []
            for google_search_thingy in google_search_thingies:
                res.append({
                'title': google_search_thingy.title,
                'url': google_search_thingy.url,
                'desc': google_search_thingy.description
            })
            return res
        except Exception as e:
            if retries == MAX_RETRIES:
                res.append("ERROR:   GOOGLE SEARCH FAILED TOO MANY TIMES")
                print(f'Google search failed ({retries}), ending the pain')
                raise e
            print(f'Google search failed ({retries}), trying again in: {2 ** retries}s')
            retries += 1
            time.sleep(2 ** retries)
        
def get_searches(name, terms, num):
    ans = {}
    for term in terms:
        ans[term] = search(name, term, num)
        wait_for(TIME_BETWEEN_GOOGLE_SEARCHES)
    return ans



def get_yt_title(url):
    time.sleep(random.random() * 1.2)
    response = requests.get(url)
    data = BeautifulSoup(response.text, 'html.parser')
    return data.find('title').text

def yt_search(term):
    global last_yt_search_time

    wait_for = random.random() * (TIME_BETWEEN_SEARCHES[1] - TIME_BETWEEN_SEARCHES[0]) + TIME_BETWEEN_SEARCHES[0]

    if time.time() - last_yt_search_time < wait_for:
        curr_wait = last_yt_search_time + wait_for - time.time()
        print('YT search too fast! Waiting for ', curr_wait)
        time.sleep(curr_wait)

    url = 'https://www.youtube.com/results?search_query=' + term.replace(' ', '+')
    response = requests.get(url)
    data = BeautifulSoup(response.text, 'html.parser')
    
    last_yt_search_time = time.time()

    ids = []

    matches = re.findall(r'/watch\?v=[\w-]+', str(data))[:]

    for m in matches:
        if m not in ids:
            ids.append(m)
        if len(ids) == 3:
            break

    res = []

    for vid_id in ids:
        url = 'https://www.youtube.com' + vid_id
        title = get_yt_title(url)
        res.append({
            'url': url,
            'title': title
        })

    return res