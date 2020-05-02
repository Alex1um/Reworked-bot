from Core.core import *


def dothis(message):
    message.cls.ban(message.userid)
    return 'Ты сам этого захотел'


def main(ACTIVATES, GLOBAL_COMMANDS, *args):
    ACTIVATES.update({'ban': {'banme'}})
    name = 'ban'
    currenthelp = 'кто хочет забанится, пишите: !banme'
    ban = Command(name, currenthelp, dothis, 0)
    GLOBAL_COMMANDS[name] = ban
