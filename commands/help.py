from Core.core import *


def dothis(message):
    COMMANDS = message.cls.GLOBAL_COMMANDS
    params = message.msg.split()
    if len(params) > 1:
        if params[1] in COMMANDS.keys():
            mreturn = Command.help[params[1]]
        else:
            mreturn = 'No command'
    else:
        mreturn = '\n'.join(''.join(i) for i in list(
            zip(map(lambda x: f'{x} - !', range(len(COMMANDS))), COMMANDS.keys())))
    return mreturn


def main():
    return "help", "help", dothis, '!help {command/page}\nВыводит информацию о команде', 0, None, None, None
    ACTIVATES.update({'help': {'help'}})
    name = 'help'
    currenthelp = '!help {command/page}\nВыводит информацию о команде'
    help = Command(name, currenthelp, dothis, 0)
    GLOBAL_COMMANDS[name] = help
