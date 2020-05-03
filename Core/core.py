import glob
import os
import pickle
import tempfile
from threading import Thread
from functools import partial
from .models import db_session
from typing import *


def nothing(*chat, **kwargs):
    pass


class ChatSystem:
    system_id = 0
    ACTIVE_ACTIONS = dict()
    PASSIVE_ACTIONS = list()
    SETTINGS = dict()
    EXITS = list()
    ON_LOAD = list()

    def __init__(self, modules: Dict[str, str], db_file=None, default_command_symbols=("!", "test>")):
        self.defaut_command_symbols = default_command_symbols
        self.system_id = ChatSystem.system_id
        ChatSystem.system_id += 1
        if db_file is None:
            db_file = f"\\Core\\db\\db-{ChatSystem.system_id}.sqlite"
        exists = os.path.exists(db_file)
        self.db_session = db_session.DataBaseSession(db_file)
        self.load_modules(modules, not exists)
        self.reload()

    def reload(self):
        for action in self.ON_LOAD:
            action(self)

    def load_modules(self, dirs, init=True):
        session = self.db_session.create_session()
        currentdir = os.path.abspath(os.curdir)
        for dir in dirs.keys():
            os.chdir(dir)
            files = glob.glob(r"*.py") if dirs[dir][0] == '@all' else dirs[dir]
            files = files if isinstance(files, tuple) or isinstance(files,
                                                                    set) or isinstance(
                files, list) else tuple(files)
            for i in files:
                if '!' + i not in dirs[dir] and i[0] != '!':
                    if i[:-3] == ".py":
                        i = i[:-3]
                    print(dir, i)
                    exec(f'from {dir} import {i}')
                    _cmd, _additional, _setts = eval(f'{i}.main()')
                    __passivef, __exitf, __onloadf = _additional if _additional else (None, None, None)
                    exec(f'del {i}')
                    if len(_cmd) >= 5 and not all(map(lambda x: x is None, _cmd[:4])):
                        __name, __activates, __action, __help, __level, __symbol = _cmd
                        __activates = " " + __activates.strip() + " "
                        if __symbol is None:
                            __symbol = self.defaut_command_symbols[0]
                        if init:
                            session.add(self.db_session.CommandTable(__name, __activates, __help, __level, __symbol))
                        self.ACTIVE_ACTIONS[__name] = __action
                    if __passivef:
                        self.PASSIVE_ACTIONS.append(__passivef)
                    if __exitf:
                        self.EXITS.append(__exitf)
                    if _setts:
                        self.SETTINGS.update(_setts)
                    if __onloadf:
                        self.ON_LOAD.append(__onloadf)

        session.commit()
        os.chdir(currentdir)

    def exit(self):
        for command in self.EXITS:
            try:
                command(self)
            except Exception as f:
                pass

    def save_settings(self):
        self.db_session.create_session().commit()

    def invoke_command(self, message, command_name: str) -> str and list:
        return self.ACTIVE_ACTIONS[command_name](message)

    def getcommand(self, value):
        session = self.db_session.create_session()
        v = " " + value + " "
        k = session.query(self.db_session.CommandTable).filter(self.db_session.CommandTable.activates.contains(v)).first()
        if k:
            return k
        return None

    def get_command_symbol(self, text):
        for i in self.defaut_command_symbols:
            if text[:len(i)] == i:
                return i
        else:
            return None

    def valid(self, text):
        command_symbol = self.get_command_symbol(text)
        if command_symbol is not None:
            value = text[len(command_symbol):text.find(' ') if text.find(
                ' ') != -1 else None]
            if self.getcommand(value):
                return True
        return False


class Chat(Thread):

    def __init__(self, main_system: ChatSystem):
        super().__init__()
        self.main_system = main_system

    def send(self):
        pass

    def input(self):
        pass

    def message_parse(self):
        pass


class Settings:
    random_talks_file = 'Trash'
    random_talks_enable = False
    level = 0
    salades_file = 'food'
    salades_max_in_row = 6
    ai_enabled = True

    def change(self, message, length, level, d=None, l=0):

        if isinstance(d, tuple):
            return d[0](self, message, l - 1) if level >= d[1] else 'U dont have permissions'
        elif length > l:
            if message.params[l] in d.keys() and message.params[l - 1] != message.params[l]:
                return self.change(message, length, level, d[message.params[l]], l + 1)
        return '!settings ' + ' '.join(message.params) + ' ' + '{' + '|'.join(d.keys()) + '}'

    def __init__(self):
        self.random_talks_enable = False
        self.level = 0


class Message(Thread):
    wtype = ''
    command = ''
    msg_id = 0
    sendid = ''
    userid = 0
    msg = ''
    date = ''
    text = ''
    cls = None
    attachments = dict()
    sym = ''

    def __init__(self, _type, id, text, cls: Chat):
        system: ChatSystem = cls.main_system
        session = system.db_session.create_session()
        Thread.__init__(self)
        parsed = cls.message_parse(text)
        self.wtype = parsed['type']
        self.attachments = parsed['attachments']
        self.msg = parsed['msg']
        self.date = parsed['date']
        self.sendid = parsed['sendid']
        self.userid = parsed['userid']
        self.user = session.query(system.db_session.User).get(self.userid)
        if self.user is None:
            self.user = system.db_session.User(self.userid, 'vk', 0)
            session.add(self.user)
            session.commit()
        self.sym = system.get_command_symbol(self.msg)
        self.command = system.getcommand(self.msg[len(self.sym):self.msg.find(' ') if self.msg.find(' ') != -1 else None]) if self.sym is not None else None
        self.cls: Chat = cls
        self.text = self.msg[self.msg.find(' ') + 1:]
        self.msg_id = id
        self.params = self.msg.split()[1::]
        self.special_params = set(filter(lambda x: x[0] == '?', self.params))
        for param in self.special_params:
            self.params.remove(param)
        # print(self.special_params, self.params)

    def run(self):
        system = self.cls.main_system
        session = system.db_session.create_session()
        if self.command:
            ans = system.ACTIVE_ACTIONS[self.command.name](self) if self.command.level <= self.user.level else "you don't have permission"
            self.send(ans)
        else:
            for action in system.PASSIVE_ACTIONS:
                try:
                    ans = action(self)
                    self.send(ans)
                except Exception as f:
                    pass
            # self.cls.send('Wrong', self.sendid, self.msg_id)

    def send(self, msg):
        if msg is not None:
            if isinstance(msg, tuple):
                if msg[0] is None:
                    self.cls.send(res='...', id=self.sendid, rid=self.msg_id, attachment=msg[1])
                else:
                    self.cls.send(msg[0], self.sendid, self.msg_id, attachment=msg[1])
            elif isinstance(msg, list):
                for i in msg:
                    self.send(i)
            else:
                self.cls.send(msg, self.sendid, self.msg_id)
        self.cls.main_system.save_settings()