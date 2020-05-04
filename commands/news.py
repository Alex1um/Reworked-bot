from Core.core import *
import schedule
from commands.site_parsers.news import *


# init
# getting news from yandex and triberkomo
def update_news(system: ChatSystem):
    system.module_news = set()
    apply_news(system.module_news)
# init


def dothis(message):
    system = message.cls.main_system
    tags = set(message.params)
    n = 1
    if message.params:
        if message.params[0].isdigit():
            n = int(message.params[0])
    le = 0
    ans = ''
    i = 0
    for item in system.__news:
        item_lower = item[0].lower()
        if n == 0:
            break
        if not tags or (item[1] in tags or any(
                map(lambda x: x in item_lower, tags))):
            n -= 1
            le1 = len(item[0])
            if le1 + le > 4096:
                return ans
            else:
                ans += item[0]
                le += le1
        i += 1
    if not ans:
        return 'Ничего не найдено'
    return ans


def main():
    return ("get_news",
            "news",
            dothis,
            '!news {необязательно: тема}\n'
            'Получить свежие новости по теме или без',
            0,
            None,
            "Свежие новости"), (None, None, update_news), None
