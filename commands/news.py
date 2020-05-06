from Core.core import *
import schedule
from commands.site_parsers.news import *
from ast import literal_eval


# init
# getting news from yandex and triberkomo
def update_news(system: ChatSystem):

    def update(system):
        session = system.db_session.create_session()
        for sett in session.query(system.db_session.Settings).filter(
                system.db_session.Settings.name == 'news'):
            session.delete(sett)
        session.commit()
        system.module_news = set()
        apply_news(system.module_news)

    update(system)
    schedule.every(5).hours.do(update, system)
    # system.module_news = set()
    # apply_news(system.module_news)
# init


def dothis(message):
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    was = message.get_setting(session, 'news')
    was_set = literal_eval(was.value) if was else set()
    tags = set(message.params)
    if message.params:
        if message.params[0].isdigit():
            n = int(message.params[0])
    le = 0
    ans = ''
    for i, item in enumerate(system.module_news):
        item_lower = item[0].lower()
        if not tags or (item[1] in tags or any(
                map(lambda x: x in item_lower, tags))):
            le1 = len(item[0])
            if le1 + le > 4096:
                return ans
            elif i not in was_set:
                was_set.add(i)
                ans += item[0]
                le += le1
                break
    if not ans:
        return 'Ничего не найдено'
    if was:
        was.value = str(was_set)
        session.commit()
    else:
        message.add_setting(session, 'news', str(was_set))
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
