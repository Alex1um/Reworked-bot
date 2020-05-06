import glob
import os
from threading import Thread
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

    def __init__(self, modules: Dict[str, str], db_file=None,
                 default_command_symbols=("!", "test>"),
                 mode: Union['full', 'commands', None]="commands"):
        """
        Initialising all commands and data base

        :param modules: Dictionary of modules - Path: files or @all for all
        files with !file for exclude files
        :param db_file: path for database file may be None
        :param default_command_symbols: default symbols to invoke most commands
        :param mode: initialising mode:
        'full' - for delete database;
        'commands' - for save users and their settings;
        """
        self.defaut_command_symbols = default_command_symbols
        self.system_id = ChatSystem.system_id
        ChatSystem.system_id += 1
        if db_file is None:
            db_file = f".\\Core\\db\\db-{ChatSystem.system_id}.sqlite"
        exists = os.path.exists(db_file)
        self.db_session = db_session.DataBaseSession(db_file)
        is_init = not exists
        if exists:
            if mode == "full":
                self.clear_database(False)
                is_init = True
            elif mode == "commands":
                self.clear_database(self.db_session.CommandTable)
                is_init = True
        self.load_modules(modules, is_init)
        self.reload()

    def reload(self):
        for action in self.ON_LOAD:
            action(self)

    def load_modules(self, dirs, init=True):
        '''
        loading modules with import and execute main function

        :param dirs: Paths for files
        :param init: Add new commands?
        :return:
        '''
        session = self.db_session.create_session()
        currentdir = os.path.abspath(os.curdir)
        for dir in dirs.keys():
            os.chdir(dir)
            files = glob.glob(r"*.py") if dirs[dir][0] == '@all' else dirs[dir]
            files = files if isinstance(
                files, tuple) or isinstance(files,
                                            set) or isinstance(
                files, list) else tuple(files)
            for i in files:
                if '!' + i not in dirs[dir] and i[0] != '!':
                    if i[-3:] == ".py":
                        i = i[:-3]
                    print(dir, i)
                    exec(f'from {dir} import {i}')
                    _cmd, _additional, _setts = eval(f'{i}.main()')
                    if _additional:
                        __passivef, __exitf, __onloadf = _additional
                    else:
                        __passivef, __exitf, __onloadf = None, None, None
                    exec(f'del {i}')
                    if _cmd and len(_cmd) >= 3 and not all(
                            map(lambda x: x is None, _cmd[:3])):
                        __name, __activates, __action = _cmd[:3]
                        __activates = " " + __activates.strip() + " "
                        if init:
                            session.add(self.db_session.CommandTable(
                                __name,
                                __activates,
                                *_cmd[3:],
                                default_sym=self.defaut_command_symbols[0]))
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
        '''
        Uses exit functions for commands

        :return:
        '''
        for command in self.EXITS:
            try:
                command(self)
            except Exception as f:
                pass

    def clear_database(self, table):
        '''
        delete all values in column

        :param table: table for delete
        :return:
        '''
        session = self.db_session.create_session()
        if table:
            for user in session.query(table):
                session.delete(user)
            session.commit()
        else:
            meta =self.db_session.SqlAlchemyBase.metadata
            for table in reversed(meta.sorted_tables):
                session.execute(table.delete())
            session.commit()

    def invoke_command(self, message, command_name: str) -> str and list:
        return self.ACTIVE_ACTIONS[command_name](message)

    def getcommand(self, value):
        '''
        getting command name with sql;

        :param value: activation command(may be)
        :return:
        '''
        session = self.db_session.create_session()
        v = " " + value + " "
        k = session.query(self.db_session.CommandTable).filter(
            self.db_session.CommandTable.activates.contains(v)).first()
        if k:
            return k
        return None

    def get_command_symbol(self, text):
        '''
        symbol before command

        :param text:
        :return:
        '''
        for i in self.defaut_command_symbols:
            if text[:len(i)] == i:
                return i
        else:
            return None

    def valid(self, text):
        '''
        Is this command?

        :param text: message
        :return:
        '''
        command_symbol = self.get_command_symbol(text)
        if command_symbol is not None:
            value = text[len(command_symbol):text.find(' ') if text.find(
                ' ') != -1 else None]
            if self.getcommand(value):
                return True
        return False


class Chat(Thread):
    '''
    Default struct for chat

    '''

    def __init__(self, main_system: ChatSystem):
        super().__init__()
        self.main_system = main_system

    def send(self):
        pass

    def input(self):
        pass

    def message_parse(self):
        pass


class Message(Thread):
    wtype = ''  # chat type
    command = ''  # command name
    msg_id = 0  # message id
    sendid = ''
    userid = 0  # sender id
    msg = ''  # message text
    date = ''  # message date
    text = ''  # message text without command
    cls = None  # system class
    attachments = dict()  # photos, audios...
    sym = ''  # symbol before command

    def __init__(self, _type, id, text, cls: Chat):
        """


        :param _type: Chat type
        :param id: message id
        :param text: - send text
        :param cls: - Chat type
        """
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

        self.sym = system.get_command_symbol(self.msg)
        self.command = system.getcommand(
            self.msg[
            len(self.sym):self.msg.find(
                ' ') if self.msg.find(
                ' ') != -1 else None]) if self.sym is not None else None
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
        if self.user is None:
            self.user = system.db_session.User(self.userid, 'vk', 0)
            session.add(self.user)
            session.commit()
            self.send(
                "Добро пожаловать!" 
                " напишит"
                "е " + self.cls.main_system.defaut_command_symbols[0] + "help д"
                                                                        "ля пол"
                                                                        "учения"
                                                                        " пом"
                                                                        "ощи")
        if self.command:
            ans = system.ACTIVE_ACTIONS[
                self.command.name](
                self) if self.command.level <= self.user.level else "you d" \
                                                                    "on't h" \
                                                                    "ave pe" \
                                                                    "rmission"
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
                self.cls.send(msg[0] if msg[0] else '...',
                              self.sendid,
                              self.msg_id,
                              attachment=msg[1]
                              )
            elif isinstance(msg, list):
                for i in msg:
                    self.send(i)
            elif isinstance(msg, dict):
                self.cls.send(msg['msg'] if 'msg' in msg.keys() else '...',
                              self.sendid,
                              self.msg_id,
                              attachment=msg['attachment'] if
                              'attachment' in msg.keys() else None,
                              keyboard=msg['keyboard'] if
                              'keyboard' in msg.keys() else None
                              )
            else:
                self.cls.send(msg, self.sendid, self.msg_id)

    def get_setting(self, session, setting: str):
        return session.query(
            self.cls.main_system.db_session.Settings
        ).filter(
            (
                    self.cls.main_system.db_session.Settings.user_id == self.userid
            ) & (
                    self.cls.main_system.db_session.Settings.name == setting
            )
        ).first()

    def add_setting(self, session, setting, value=None):
        session.add(
            self.cls.main_system.db_session.Settings(
                self.userid,
                setting,
                value if setting != 'active' else self.sym + value
            )
        )
        session.commit()

    def delete_active(self, session):
        self.delete_setting(session, 'active')
        session.commit()

    def delete_setting(self, session, setting: str):
        session.delete(self.get_setting(session, setting))
        session.commit()

    def get_session(self):
        return self.cls.main_system.db_session.create_session()