from random import sample, randint, shuffle
from pickle import load
from Core.core import *
from ast import literal_eval
import os


def salades_op(self, message, length):
    p = message.params[length]
    args = message.params[length + 1:]
    if p == 'current':
        return self.salades_file
    elif p == 'switch' and args:
        if args[0] in map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):], glob.glob("commands\\files\\*.saladict")):
            self.random_talks_file = args[0]
        else:
            return 'No file'
    elif p == 'list':
        return '\n'.join(map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):], glob.glob("commands\\files\\*.saladict")))
    elif p == 'default':
        self.random_talks_file = Settings.random_talks_file
    elif p == 'max':
        if args:
            self.salades_max_in_row = int(args[0])
        else:
            return self.salades_max_in_row
    return 'Success'


def dothis(message):

    def conc(a: list, b: list):
        shuffle(a)
        shuffle(b)
        la = len(a)
        lb = len(b)
        a1, b1, a2, b2 = a[:la // 2], a[la // 2:], b[:lb // 2], b[lb // 2:]
        a1, b1, a2 = mutate(a1 + b1, b1 + a2, a1 + b2)
        return [list(set(a1)), list(set(b1)), list(set(a2))]

    def mutate(*args):
        args = list(args)
        for i, e in enumerate(args):
            le = len(e)
            args[i] = sample(e, randint(le // 2 + 1, le)) + sample(words, randint(0, message.cls.SETTINGS[message.sendid].salades_max_in_row - le))
        print(args, '---------------------')
        return args

    words = []
    salades = []
    with open(fr"{os.getcwd()}\\commands\\files\\{message.cls.SETTINGS[message.sendid].salades_file}.saladict", 'rb') as f:
        words = load(f)
    if not message.params:
        salades = [sample(words, randint(4, 6)), sample(words, randint(4, 6)), sample(words, randint(4, 6))]
        message.cls.ACTIVE_COMMANDS[message.sendid] = message.msg + ' ' + str(salades).replace(' ', '')
    else:
        try:
            kill = int(message.params[1])
            salades = literal_eval(message.params[0])
            salades.pop(kill - 1)
            salades = conc(*salades)
            message.cls.ACTIVE_COMMANDS[message.sendid] = message.sym + message.command + ' ' + str(salades).replace(' ', '')
        except Exception as f:
            return f
    return '!end to close\nВыберите худшую комбинацию:\n' + '\n'.join((str(n + 1) + '.' + str(salad) for n, salad in enumerate(salades)))


def main(ACTIVATES, GLOBAL_COMMANDS, *args):
    ACTIVATES.update({'salades': {'salades', 'Салатики'}})
    name = 'salades'
    currenthelp = '!salades\nИгра на генетичеком алгоритме'
    stt = Command(name, currenthelp, dothis, 0)
    args[1].update({
        'salades': {
            'file': {
                'current': (salades_op, 0),
                'switch': (salades_op, 5),
                'list': (salades_op, 0)},
            'max': (salades_op, 5)}})
    GLOBAL_COMMANDS[name] = stt