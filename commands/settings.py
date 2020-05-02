from Core.core import *


def dothis(message):
    try:
        return message.cls.SETTINGS[message.sendid].change(message, len(message.params), message.cls.SETTINGS[message.userid].level)
    except Exception as f:
        return str(f)


def exitf(chat):
    chat.save_settings()


def main(ACTIVATES, GLOBAL_COMMANDS, *args):
    ACTIVATES.update({'settings': {'set', 'settings'}})
    name = 'settings'
    currenthelp = '{!set|!settings} {module} {setting} {parameter} {name}\nНастройки'
    settings = Command(name, currenthelp, dothis, 0, exitf)
    GLOBAL_COMMANDS[name] = settings
