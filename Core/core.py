import glob
import os
import pickle
import tempfile
from threading import Thread
from functools import partial
from .models import db_session


db_session.global_init("\\db\\default.sqlite")


def nothing(*chat, **kwargs):
    pass


def getcommand(value, cls):
    for k, v in cls.ACTIVATES.items():
        if value in v:
            return k
    else:
        return 'unknown'


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

    def __init__(self, _type, id, text, cls):
        Thread.__init__(self)
        parsed = cls.message_parse(text)
        self.wtype = parsed['type']
        self.attachments = parsed['attachments']
        self.msg = parsed['msg']
        self.date = parsed['date']
        self.sendid = parsed['sendid']
        self.userid = parsed['userid']
        self.sym = get_command_symbol(self.msg, cls)
        self.command = getcommand(self.msg[len(self.sym):self.msg.find(' ') if self.msg.find(' ') != -1 else None], cls) if self.sym is not None else None
        self.cls = cls
        self.text = self.msg[self.msg.find(' ') + 1:]
        self.msg_id = id
        self.params = self.msg.split()[1::]
        self.special_params = set(filter(lambda x: x[0] == '?', self.params))
        for param in self.special_params:
            self.params.remove(param)
        # print(self.special_params, self.params)
        if self.sendid not in cls.SETTINGS.keys():
            self.cls.SETTINGS[self.sendid] = Settings()
        if self.userid not in cls.SETTINGS.keys():
            self.cls.SETTINGS[self.userid] = Settings()
        cls.save_settings(_type)

    def run(self):
        if valid(self.cls, self.msg):
            # print(type(self.cls.GLOBAL_COMMANDS[self.command].level))
            # print(type(self.cls.SETTINGS[self.userid].level))
            ans = self.cls.GLOBAL_COMMANDS[self.command].dothis(self) \
                if self.cls.GLOBAL_COMMANDS[self.command].level <=\
                   self.cls.SETTINGS[self.userid].level\
                else "you don't have permission"
            self.send(ans)
        else:
            for action in self.cls.PASSIVE.values():
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


def valid(cls, text):
    command_symbol = get_command_symbol(text, cls)
    if command_symbol is not None:
        value = text[len(command_symbol):text.find(' ') if text.find(' ') != -1 else None]
        for v in cls.ACTIVATES.values():
            if value in v or value == v:
                return True
    return False


class Command:
    count = 0
    name = ''
    help = dict()
    calls = 0
    id = 0
    logs = []
    level = 0
    exit = None

    def dothis(self):
        ...

    def __init__(self, name, help, action, level, exit=nothing):
        self.id = Command.count
        Command.count += 1
        Command.help[name] = help
        self.name = name
        self.dothis = action
        self.level = level
        self.exit = exit


def get_command_symbol(text, cls):
    for i in cls.COMMAND_SYMBOL:
        if text[:len(i)] == i:
            return i
    else:
        return None


class Chat(Thread):
    bot_id = 0
    ACTIVATES = dict()
    GLOBAL_COMMANDS = dict()
    COMMAND_SYMBOL = set()
    ACTIVE_COMMANDS = dict()
    PASSIVE = dict()
    SETTINGS = dict()

    def __init__(self, modules, wtype):
        Thread.__init__(self)
        self.bot_id = Chat.bot_id
        Chat.bot_id += 1
        self.load_modules(modules)
        self.ACTIVE_COMMANDS = dict()
        try:
            with open(rf'.\\settings\\{wtype}_{self.bot_id}.sett', 'rb') as f:
                self.SETTINGS = pickle.load(f)
        except FileNotFoundError:
            self.SETTINGS = dict()

    def reload_modules(self, dirs):
        activats = dict()
        passive = dict()
        global_commands = dict()
        default_settings = dict()
        self.get_modules(dirs,
                         activats,
                         global_commands,
                         passive,
                         default_settings)
        self.ACTIVATES.update(activats)
        self.GLOBAL_COMMANDS.update(global_commands)
        self.DEFAULT_SETTINGS.update(default_settings)
        self.PASSIVE.update(passive)

    def load_modules(self, dirs={'commands': '@all'}, command_symbols=('!', 'abs')):
        self.ACTIVATES = dict()
        self.PASSIVE = dict()
        self.GLOBAL_COMMANDS = dict()
        self.COMMAND_SYMBOL = command_symbols
        self.DEFAULT_SETTINGS = dict()
        self.get_modules(dirs,
                         self.ACTIVATES,
                         self.GLOBAL_COMMANDS,
                         self.PASSIVE,
                         self.DEFAULT_SETTINGS)

    @staticmethod
    def get_modules(dirs, activates, global_commands, passive, default_settings):
        currentdir = os.path.abspath(os.curdir)
        for dir in dirs.keys():
            os.chdir(dir)
            files = glob.glob(r"*.py") if dirs[dir][0] == '@all' else dirs[dir]
            files = files if isinstance(files, tuple) or isinstance(files,
                                                                    set) or isinstance(
                files, list) else tuple(files)
            for i in files:
                if '!' + i not in dirs[dir] and i[0] != '!':
                    i = i[:-3]
                    exec(f'from {dir} import {i}')
                    exec(
                        f'{i}.main(activates, global_commands, passive, default_settings)')
                    exec(f'del {i}')
            os.chdir(currentdir)
        # f = tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=f'{currentdir}/globals', suffix='.py')

    def exit(self):
        for command in self.GLOBAL_COMMANDS.values():
            try:
                command.exit(self)
            except Exception as f:
                pass
        raise SystemExit(0)

    def send(self):
        ...

    def input(self):
        ...

    def save_settings(self, wtype):
        with open(rf'settings/{wtype}_{self.bot_id}.sett', 'wb') as f:
            pickle.dump(self.SETTINGS, f)

    def invoke_command(self, message, command: str) -> str and list:
        return self.GLOBAL_COMMANDS[command].dothis(message)


class Settings:
    random_talks_file = 'Trash'
    random_talks_enable = False
    level = 0
    salades_file = 'food'
    salades_max_in_row = 6
    ai_enabled = True

    def change(self, message, length, level, d=None, l=0):

        if d is None:
            d = message.cls.DEFAULT_SETTINGS
        if isinstance(d, tuple):
            return d[0](self, message, l - 1) if level >= d[1] else 'U dont have permissions'
        elif length > l:
            if message.params[l] in d.keys() and message.params[l - 1] != message.params[l]:
                return self.change(message, length, level, d[message.params[l]], l + 1)
        return '!settings ' + ' '.join(message.params) + ' ' + '{' + '|'.join(d.keys()) + '}'

    def __init__(self):
        self.random_talks_enable = False
        self.level = 0
