from Core.core import *
import random
import pickle
import re
import requests
import gtts
import time
import os


def table_file(self, message, length):
    param = message.params[length]
    name = message.params[length + 1:]
    if name:
        name = name[0]
        if param == 'add':
            open(fr'commands\\files\\{name[0]}.table', 'w')
            self.random_talks_file = name
        elif param == 'switch':
            if name in map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):], glob.glob("commands\\files\\*.table")):
                self.random_talks_file = name
            else:
                return 'No file'
        elif param == 'rename':
            os.rename(rf'commands\\files\\{self.random_talks_file}.table',
                      rf'commands\\files\\{name}.table')
            self.random_talks_file = name
    elif param == 'default':
        self.random_talks_file = Settings.random_talks_file
    elif param == 'current':
        return self.random_talks_file
    elif param == 'list':
        return '\n'.join(map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):], glob.glob("commands\\files\\*.table")))
    return 'Success'


def enable_record(c, self, message, length):
    if c is not None:
        self.random_talks_enable = c
        return 'Success'
    else:
        return self.random_talks_enable


def dothis(message):
    try:
        with open(rf"commands\\files\\{message.cls.SETTINGS[message.sendid].random_talks_file}.table", 'rb') as f:
            w_table = pickle.load(f)
    except Exception as f:
        return str(f)
    try:
        count = random.randint(11, 100)
        word = random.choice(list(w_table.keys())) if not message.params else message.params[0].lower()
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
        res = res.replace(' ,', ', ').replace('.,', '.').replace(' .', '.').replace('..', '.').replace(',.', '.')
        if '?audio' in message.special_params:

            tmp_name = f"temp\\{str(time.time())}.tmpmp3"
            gtts.gTTS(res, lang='ru').save(tmp_name)

            attach = message.cls.upload_doc(tmp_name, message.sendid, 'audio_message')
            os.remove(tmp_name)
            if '?notext' in message.special_params:
                res = None
            return res, attach
        return res


def update_table(message):
    if message.cls.SETTINGS[message.sendid].random_talks_enable:
        try:
            with open(rf"commands\\files\\{message.cls.SETTINGS[message.sendid].random_talks_file}.table", 'rb') as f:
                w_table = pickle.load(f)
        except EOFError:
            w_table = dict()
        words = message.msg.lower().replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('\n', ' ')  # format
        while '  ' in words or '**' in words:
            words = words.replace('  ', ' ').replace('**', '*')
        words = words.split()
        setted = set(words)
        words_str = ' '.join(words).replace(' , ', ' ,')
        for w in setted:
            n = list(set(map(lambda x: x.split()[1], re.findall(rf'{w} [\S\,\.]+', words_str))))
            if len(n) > 0:
                if w in w_table.keys():
                    w_table[w].extend(n)
                else:
                    w_table[w] = n
        with open(fr"commands\\files\\{message.cls.SETTINGS[message.sendid].random_talks_file}.table", 'wb') as f:
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
                '1': (partial(enable_record, True), 0),
                'True': (partial(enable_record, True), 0),
                'yes': (partial(enable_record, True), 0),
                '0': (partial(enable_record, False), 10),
                'no': (partial(enable_record, False), 0),
                'False': (partial(enable_record, False), 0),
                'current': (partial(enable_record, None), 0)}}}
    return ("random_talk", "talk", dothis, '!talk\nРандомная фраза', 0, None), (update_table, None), setts
