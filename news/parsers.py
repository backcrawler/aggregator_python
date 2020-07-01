import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin
from datetime import datetime

from .utils import append_slash, ResponceCodeError

heading = {'User-agent': 'my bot 0.9'}
web_dev_set = {'flask', 'django', 'разработка веб-сайтов', 'fastapi', 'aiohttp', 'веб-', 'web ', 'web-dev'}
data_science_set = {'машинное обучение', 'искусственный интеллект',
                    'data science', 'pandas', 'machine learning', 'data-science'}


def get_soup(link):
    '''Basic function for bs4-like sources, reduces boilerplate'''
    r = requests.get(link, headers=heading)
    if r.status_code != 200:
        raise ResponceCodeError(r.status_code)
    content = r.content
    soup = BeautifulSoup(content, "html.parser")
    return soup


def get_base(link):
    '''Returns "base" url'''
    parsed = urlparse(link)
    base = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
    return base


def reddit_base(link):
    '''Basic parser for reddit-related links'''
    r = requests.get(urljoin(link, '.json'), headers=heading)
    if r.status_code != 200:
        raise ResponceCodeError(r.status_code)
    json_obj = json.loads(r.content)
    children = json_obj['data']['children']
    base = get_base(link)
    posts = []
    for i in range(len(children)):
        if children[i]['data']['score'] < 20:
            continue
        instance = dict()
        instance['title'] = children[i]['data']['title']
        instance['ref'] = urljoin(base, children[i]['data']['permalink'])
        posts.append(instance)
    if len(posts) > 20:
        posts = posts[:20]
    return posts


def reddit_python_parser(link):
    '''Parses r/python section of Reddit'''
    posts = reddit_base(link)
    return posts


def reddit_datascience_parser(link):
    '''Parses r/datascience section of Reddit'''
    posts = reddit_base(link)
    for post in posts:
        post['category'] = 'data_science'
    return posts


def reddit_django_parser(link):
    '''Parses r/django section of Reddit'''
    posts = reddit_base(link)
    for post in posts:
        post['category'] = 'web_dev'
    return posts


def habr_parser(link):
    '''Parses Python section on Habr'''
    soup = get_soup(link)
    articles = soup.findAll('article', class_="post_preview")
    posts = []
    for article in articles:
        ref = article.find('a', class_="post__title_link")
        hub_list = article.find('ul', class_="post__hubs")
        cat = None
        for hub in hub_list.findAll('li'):
            a = hub.find('a')
            if a.text.lower() in web_dev_set:
                cat = 'web_dev'
                break
            if a.text.lower() in data_science_set:
                cat = 'data_science'
                break
        base = get_base(link)
        instance = {'title': ref.text, 'ref': urljoin(base, ref['href']), 'category': cat}
        posts.append(instance)
    # posts_list = soup.find('div', class_="posts_list")
    # refs = posts_list.findAll('a', class_="post__title_link")
    # base = get_base(link)
    # posts = [{'title': elem.text, 'ref': urljoin(base, elem['href'])} for elem in refs]
    return posts


def pypi_parser(link):
    '''Parses trending packages on PyPi'''
    soup = get_soup(link)
    trending_packages = soup.find('ul', {"aria-labelledby": "pypi-trending-packages"})
    elems = trending_packages.findAll('a', class_="package-snippet")
    base = get_base(link)
    posts = []
    for elem in elems:
        instance = dict()
        instance['ref'] = urljoin(base, elem['href'])
        instance['title'] = elem.find('span', class_="package-snippet__name").text + " " + \
                            elem.find('span', class_="package-snippet__version").text + ": " + \
                            elem.find('p', class_="package-snippet__description").text
        posts.append(instance)
    return posts


def official_python_parser(link):
    '''Parses Official Python site for new events'''
    soup = get_soup(link)
    latest_news = soup.find('div', {"class": ["blog-widget", "medium-widget"]})
    li_s = latest_news.findAll('li')
    posts = []
    for elem in li_s:
        a = elem.find('a')
        posts.append({'title': a.text, 'ref': a['href']})
    return posts


def official_django_parser(link):
    '''Parses news from official Django site'''
    today = datetime.today()
    month = today.strftime('%b').lower()
    year = str(today.year)
    link = urljoin(append_slash(urljoin(link, year)), month)
    soup = get_soup(link)
    list_news = soup.find('ul', class_='list-news')
    h2_s = list_news.findAll('h2')
    posts = []
    for h2 in h2_s:
        a = h2.find('a')
        posts.append({'title': a.text, 'ref': a['href'], 'category': 'web_dev'})
    return posts


def tproger_parser(link):
    '''Parses TProger Python section'''
    soup = get_soup(link)
    main_columns = soup.find('div', id='main_columns')
    articles = main_columns.findAll('article', {'class': ['box', 'item', 'post']})
    posts = []
    for article in articles:
        h2_title = article.find('h2', class_='entry-title').text
        a = article.find('a', class_='article-link')
        cat = None
        for tag in web_dev_set:
            if tag in h2_title.lower():
                cat = 'web_dev'
                break
        if not cat:
            for tag in data_science_set:
                if tag in h2_title.lower():
                    cat = 'data_science'
                    break
        posts.append({'title': h2_title, 'ref': a['href'], 'category': cat})
    if len(posts) > 20:
        posts = posts[:20]
    return posts


def realpython_parser(link):
    '''Parses realpython posts'''
    soup = get_soup(link)
    cards = soup.findAll('div', class_='card-body')
    base = get_base(link)
    posts = []
    for card in cards:
        h2 = card.find('h2')
        a = card.find('a', class_='')  # this gotta be the 1st link
        if h2 is None:
            break
        cat = None
        p = card.find('p')
        if p:
            for a_tag in p.findAll('a'):
                if a_tag.text in web_dev_set:
                    cat = 'web_dev'
                    break
                if a_tag.text in data_science_set:
                    cat = 'data_science'
                    break
        posts.append({'title': h2.text, 'ref': urljoin(base, a['href']), 'category': cat})
    if len(posts) > 20:
        posts = posts[:20]
    return posts


def medium_parser(link):
    '''Parses Python section on Medium'''
    soup = get_soup(link)
    articles = soup.findAll('div', {'class': 'postArticle'})
    posts = []
    for article in articles:
        h3 = article.find('h3', {'class': 'graf'})
        readmore = article.find('div', {'class': 'postArticle-readMore'})
        a = readmore.find('a')
        cat = None
        for tag in web_dev_set:
            if tag in h3.text.lower():
                cat = 'web_dev'
                break
        if not cat:
            for tag in data_science_set:
                if tag in h3.text.lower():
                    cat = 'data_science'
                    break
        posts.append({'title': h3.text, 'ref': a['href'], 'category': cat})
    if len(posts) > 20:
        posts = posts[:20]
    return posts