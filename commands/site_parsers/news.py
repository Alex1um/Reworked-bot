from bs4 import BeautifulSoup
import requests


def parse_triberkomo() -> set:
    """
    Parsing site triberkomo
    :return: set of news
    """
    res = requests.get(r'http://triberkomo.ru/')
    res.encoding = 'utf-8'
    titles = BeautifulSoup(res.content, 'html.parser').findAll('div', {
        'class': 'strokanew'})
    return set(map(lambda item: (
        item.contents[5].get_text().strip(),
        item.contents[1].get_text().lower()), titles))


def parse_yandex() -> set:
    """
    Parsing site yandex
    :return: set of news
    """
    res = requests.get(r'https://yandex.ru/news')
    res.encoding = 'utf-8'
    titles = BeautifulSoup(res.content, 'html.parser').findAll('div', {
        'class': 'story story_view_short story_notags'})
    ans = set()
    for obj in titles:
        title_date = obj.find('div', {'class': 'story__date'}).text.split()
        time = title_date[-1]
        title = ' '.join(title_date[:-1])
        contents = obj.find('div', {'class': 'story__topic'}).contents
        content = contents[0].text.lower()
        # topic = contents[0].text.lower()
        ans |= {(content + '\n' + time, title)}
    return ans


def apply_news(struct: set) -> None:
    """
    apply parsed news to set
    :param struct:
    :return: None
    """
    struct |= parse_yandex()
    struct |= parse_triberkomo()
    print('News updated!')
