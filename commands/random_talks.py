from Core.core import ChatSystem
import glob
import random
import pickle
import re
from functools import partial
import gtts
import time
import os


def table_file(params, system: ChatSystem, message):
    session = message.get_session()
    tr_file = message.get_setting(session, 'random_talks_file')
    value = tr_file.value if tr_file else None
    param = message.params[len(message.params) - len(params) - 1]
    if param:
        if param == 'default':
            session.delete(tr_file)
            value = None
        elif param == 'current':
            return value if value else 'youtube'
        elif param == 'list':
            return '\n'.join(map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):],
                                 glob.glob("commands\\files\\*.table")))
        elif params:
            name = params[0]
            if param == 'add':
                open(fr'commands\\files\\{name}.table', 'w')
                value = name
            elif param == 'switch':
                if name in map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):],
                               glob.glob("commands\\files\\*.table")):
                    value = name
                else:
                    return 'Файл не найден'
            elif param == 'rename':
                os.rename(rf'commands\\files\\{value}.table',
                          rf'commands\\files\\{name}.table')
                value = name
        else:
            return "недостаточно параметров"
    else:
        return 'Нет параметров. Введите нежный параметр'
    if value:
        if tr_file:
            tr_file.value = value
        else:
            message.add_setting(session, 'random_talks_file', value)
    session.commit()
    return 'Success'


def enable_record(params, system: ChatSystem, message):
    session = message.get_session()
    sett = message.get_setting(session, 'random_talks_disable')
    param = message.params[-1]
    if param:
        if param in {'1', 'True', 'true', 'yes'}:
            if sett:
                session.delete(sett)
        elif param in {'0', 'False', 'false', 'no'}:
            if sett is None:
                message.add_setting(session, 'random_talks_disable', 'yes')
        else:
            return 'False' if sett else 'True'
        session.commit()
        return 'Success'
    return "недостаточно параметров"


def dothis(message):
    session = message.get_session()
    tr_file = message.get_setting(session, 'random_talks_file')
    file = tr_file.value if tr_file else 'youtube'
    try:
        with open(rf"commands\\files\\{file}.table", 'rb') as f:
            w_table = pickle.load(f)
    except Exception as f:
        return str(f)
    try:
        count = random.randint(11, 100)
        word = random.choice(
            list(w_table.keys())
        ) if not message.params else message.params[0].lower()
        res = word.title()
        i = 0
        while i != count - 1:
            word = random.choice(w_table[word]).lower()
            if res[-1] in {'.', '!', '?'}:
                res += ' ' + word.title()
            else:
                res += ' ' + word
            i += 1
            if word[0] == ',':
                count += 1
    except Exception as f:
        pass
    finally:
        res += '.'
        res = res.replace(' ,', ', ').replace(
            '.,', '.').replace(' .', '.').replace('..', '.').replace(',.', '.')
        if '-audio' in message.special_params:

            tmp_name = f"temp\\{str(time.time())}.tmpmp3"
            gtts.gTTS(res, lang='ru').save(tmp_name)

            attach = message.cls.upload_doc(tmp_name,
                                            message.sendid, 'audio_message')
            os.remove(tmp_name)
            if '?notext' in message.special_params:
                res = None
            return res, attach
        return res


def update_table(message):
    session = message.get_session()
    tr_file = message.get_setting(session, 'random_talks_file')
    sett = message.get_setting(session, 'random_talks_disable')
    file = tr_file.value if tr_file else 'youtube'
    if sett is None:
        try:
            with open(rf"commands\\files\\{file}.table", 'rb') as f:
                w_table = pickle.load(f)
        except EOFError:
            w_table = dict()
        words = message.msg.lower().replace(
            '(', ''
        ).replace(
            ')', ''
        ).replace('[', '').replace(']', '').replace('\n', ' ')  # format
        while '  ' in words or '**' in words:
            words = words.replace('  ', ' ').replace('**', '*')
        words = words.split()
        setted = set(words)
        words_str = ' '.join(words).replace(' , ', ' ,')
        for w in setted:
            n = list(
                set(
                    map(
                        lambda x: x.split()[
                            1
                        ], re.findall(fr'{w} [\S\,\.]+', words_str))))
            if len(n) > 0:
                if w in w_table.keys():
                    w_table[w].extend(n)
                else:
                    w_table[w] = n
        with open(fr"commands\\files\\{file}.table", 'wb') as f:
            pickle.dump(w_table, f)


def main():
    setts = {
        'random_talks': {
            'table': {  # for table
                'add': (table_file, 5),
                'default': (table_file, 0),
                'switch': (table_file, 0),
                'current': (table_file, 0),
                'list': (table_file, 0),
                'rename': (table_file, 5)},
            'record': {  # for record
                '1': (enable_record, 0),
                'True': (enable_record, 0),
                'yes': (enable_record, 0),
                '0': (enable_record, 10),
                'no': (enable_record, 0),
                'False': (enable_record, 0),
                'current': (enable_record, 0)}}}
    return ("random_talk",
            "talk",
            dothis,
            '!talk {необязательно - слово, с которого начинается}\n'
            'Рандомная фраза, основанная на сообщениях пользователей боту.'
            'Вы можите поменять таблицу со словами, используя настройки',
            0,
            None,
            'Рандомная фраза'), (update_table, None, None), setts
