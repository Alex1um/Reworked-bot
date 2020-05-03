from Core.core import *
import schedule
from commands.site_parsers.news import *


# init
# getting news from yandex and triberkomo
__news = set()
apply_news(__news)
print(__news)
# init


def dothis(message):
    tags = set(message.params)
    n = 1
    if message.params:
        if message.params[0].isdigit():
            n = int(message.params[0])
    le = 0
    ans = ''
    i = 0
    for item in __news:
        item_lower = item[0].lower()
        if n == 0:
            break
        if not tags or (item[1] in tags or any(map(lambda x: x in item_lower, tags))):
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


def update_news(message):
    print('Updated!')


def main():
    return ("get_news", "news", dothis, '!news {необязательно: тема}\nПолучить свежие новости по теме или без', 0, None), None, None
