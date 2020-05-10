import glob
import os
from threading import Thread
from .models import db_session
from typing import *
import re
import schedule
import time


def nothing(*chat, **kwargs):
    pass


def fix_paths(paths: List[str]) -> List[str]:
    """
    Making path for linux and windows
    :param paths: List of paths
    :return: edited list of paths
    """
    new_paths = []
    for path in paths:
        new_paths.append(path.replace('\\', '/'))
    return new_paths


class ChatSystem:
    """
    Class to control all chats
    """
    system_id = 0
    ACTIVE_ACTIONS = dict()
    PASSIVE_ACTIONS = list()
    SETTINGS = dict()
    EXITS = list()
    ON_LOAD = list()

    def __init__(self, modules: Dict[str, str], db_file=None,
                 default_command_symbols=("!", "test>"),
                 mode: Union['full', 'commands', None]="commands",
                 update_status=0):
        """
        Initialising all commands and data base

        :type 'full': str
        :type 'commands': str
        :param modules: Dictionary of modules - Path: files or @all for all
        files with !file for exclude files
        :param db_file: path for database file may be None
        :param default_command_symbols: default symbols to invoke most commands
        :param mode: initialising mode:
        'full' - for delete database;
        'commands' - for save users and their settings;
        """
        self.update_status = float(update_status)
        self.defaut_command_symbols = default_command_symbols
        self.system_id = ChatSystem.system_id
        ChatSystem.system_id += 1
        if db_file is None:
            db_file = fr"./Core/db/db-{ChatSystem.system_id}.sqlite"
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
        Thread(target=self.shedule_run).start()

    def shedule_run(self) -> NoReturn:
        """
        Function to update schedule

        TODO: Need to put on level up
        :return: Nothing
        """
        while 1:
            schedule.run_pending()
            time.sleep(1)

    def reload(self) -> None:
        """
        run all functions on load
        :return: None
        """
        for action in self.ON_LOAD:
            action(self)

    def load_modules(self, dirs, init=True) -> NoReturn:
        """
        loading modules with import and execute their main function

        :param dirs: Paths for files
        :param init: Add new commands?
        :return:
        """
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

    def exit(self) -> NoReturn:
        """
        Running exit functions for commands
        :return:
        """
        for command in self.EXITS:
            try:
                command(self)
            except Exception:
                pass

    def clear_database(self, table) -> NoReturn:
        """
        delete all values in column

        :param table: table for delete
        :return:
        """
        session = self.db_session.create_session()
        if table:
            for user in session.query(table):
                session.delete(user)
            session.commit()
        else:
            meta = self.db_session.SqlAlchemyBase.metadata
            for table in reversed(meta.sorted_tables):
                session.execute(table.delete())
            session.commit()

    def invoke_command(self, message, command_name: str) -> str and list:
        return self.ACTIVE_ACTIONS[command_name](message)

    def getcommand(self, value) -> Optional:
        """
        getting command name with sql;

        :param value: activation command(may be)
        :return:
        """
        session = self.db_session.create_session()
        v = " " + value + " "
        k = session.query(self.db_session.CommandTable).filter(
            self.db_session.CommandTable.activates.contains(v) | (
                    self.db_session.CommandTable.name == v.strip())).first()
        if k:
            return k
        return None

    def get_command_symbol(self, text: str) -> Optional[str]:
        """
        find symbol before command

        :param text:
        :return:
        """
        for i in self.defaut_command_symbols:
            if text[:len(i)] == i:
                return i
        else:
            return None

    def valid(self, text):
        """
        Is this command?

        :param text: message
        :return:
        """
        command_symbol = self.get_command_symbol(text)
        if command_symbol is not None:
            value = text[len(command_symbol):text.find(' ') if text.find(
                ' ') != -1 else None]
            if self.getcommand(value):
                return True
        return False


class Chat(Thread):
    """
    Default struct for chat
    """
    id = 0
    find_id = re.compile(r'\[id(\d+)\|@\w+]')

    def __init__(self, main_system: ChatSystem):
        """
        Initialising with setting id and schedule to update status
        :param main_system: class of ChatSystem
        """
        self.id = Chat.id
        Chat.id += 1
        super().__init__()
        self.main_system = main_system
        if main_system.update_status:
            schedule.every(main_system.update_status).minutes.do(
                self.update_status
            )

    def update_status(self) -> None:
        """
        Updating status by writing time to file
        :return: Nothing
        """
        with open(f'./status/{self.id}.status', 'w') as f:
            f.write(str(time.time()))

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
    sendid = ''  # to send
    userid = 0  # sender(bot) id
    msg = ''  # message text
    date = ''  # message date
    text = ''  # message text without command
    cls = None  # system class
    attachments = dict()  # photos, audios...
    sym = ''  # symbol before command

    def __init__(self, _type, id, text, cls: Chat):
        """
        Parsing text and making Message
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
        self.user = session.query(
            system.db_session.User
        ).filter(
            (
                    system.db_session.User.id == self.userid
            ) & (
                    system.db_session.User.type == self.wtype
            )
        ).first()

        self.sym = system.get_command_symbol(self.msg)
        self.command = system.getcommand(
            self.msg[len(self.sym):self.msg.find(
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

    def run(self) -> None:
        """
        Getting user and adding to database
        run passive actions if command is not found
        :return: None
        """
        system = self.cls.main_system
        session = system.db_session.create_session()
        if self.user is None:
            self.user = system.db_session.User(self.userid, self.wtype, 0)
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
                except Exception:
                    pass
            # self.cls.send('Wrong', self.sendid, self.msg_id)

    def send(self, msg: Union[str, Tuple, Dict, List, Generator]):
        """
        sends messages depending on its type
        :param msg: Return of command
        :return: Nothing
        """
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
                              keyboard=self.cls.make_keyboard(*msg['keyboard'])
                              if 'keyboard' in msg.keys() else None
                              )
            else:
                self.cls.send(msg, self.sendid, self.msg_id)

    def get_setting(self, session, setting: str) -> Optional:
        """
        Getting setting from sql with given name
        :param session: database session
        :param setting: setting name
        :return: Founded sqlalchemy type
        """
        return session.query(
            self.cls.main_system.db_session.Settings
        ).filter(
            (
                    self.cls.main_system.
                    db_session.Settings.user_id == self.userid
            ) & (
                    self.cls.main_system.db_session.Settings.name == setting
            )
        ).first()

    def add_setting(self, session, setting: str, value: Optional[str] = None):
        """
        Adding setting to sql settings table
        if setting is active:
        put default command setting before value
        :param session:
        :param setting:
        :param value:
        :return:
        """
        session.add(
            self.cls.main_system.db_session.Settings(
                self.userid,
                setting,
                value if setting != 'active' else self.sym + value
            )
        )
        session.commit()

    def delete_active(self, session) -> None:
        """
        delete active setting
        :param session: sqlalchemy sesion
        :return:
        """
        self.delete_setting(session, 'active')
        session.commit()

    def delete_setting(self, session, setting: str):
        """
        Delete setting with given name
        :param session:
        :param setting:
        :return:
        """
        session.delete(self.get_setting(session, setting))
        session.commit()

    def get_session(self):
        """
        Getting sqlalchemy session
        :return:
        """
        return self.cls.main_system.db_session.create_session()
