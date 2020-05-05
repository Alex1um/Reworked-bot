from random import sample, randint, shuffle
from pickle import load
from Core.core import *
from ast import literal_eval
import os


def salades_op(params, system: ChatSystem, message):
    session = system.db_session.create_session()
    salades_file = session.query(system.db_session.Settings).filter(
        (system.db_session.Settings.user_id == message.userid) &
        (system.db_session.Settings.name == "salades_file")).first()

    file = salades_file.value if salades_file else None
    prev_param = message.params[-1]
    if prev_param == 'current':
        return file if file else 'food'
    elif prev_param == 'switch' and params:
        if params[0] in map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):],
                            glob.glob("commands\\files\\*.saladict")):
            file = params[0]
        else:
            return 'Файл не найден'
    elif prev_param == 'list':
        return '\n'.join(map(lambda x: x[x.rfind('\\') + 1:x.rfind('.'):],
                             glob.glob("commands\\files\\*.saladict")))
    elif prev_param == 'default':
        session.delete(salades_file)
        file = None
    elif prev_param == 'max':
        salades_max = session.query(system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == "salades_max")).first()

        if params and params[0] != '4' and params[0].isdigit():
            if salades_max is None:
                session.add(system.db_session.Settings(message.userid,
                                                       'salades_max',
                                                       params[0]))
            else:
                salades_max.value = int(params[0])
        else:
            return salades_max.value if salades_max else '4'
    if file:
        if salades_file:
            salades_file.value = file
        else:
            session.add(system.db_session.Settings(
                message.userid, 'random_talks_file', file))
    session.commit()
    return 'Success'


def dothis(message):
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    salades_file = session.query(system.db_session.Settings).filter(
        (system.db_session.Settings.user_id == message.userid) &
        (system.db_session.Settings.name == "salades_file")).first()
    salades_file = salades_file.value if salades_file else 'food'
    salades_max = session.query(system.db_session.Settings).filter(
        (system.db_session.Settings.user_id == message.userid) &
        (system.db_session.Settings.name == "salades_max")).first()
    salades_max = int(salades_max.value) if salades_max else 4

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
            args[i] = sample(e, randint(le // 2 + 1, le)) + sample(words, randint(0, salades_max - le))
        print(args, '---------------------')
        return args

    words = []
    salades = []
    with open(fr"{os.getcwd()}\\commands\\files\\{salades_file}.saladict", 'rb') as f:
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


def main():
    setts = {
        'salades': {
            'file': {
                'current': (salades_op, 0),
                'switch': (salades_op, 5),
                'list': (salades_op, 0)},
            'max': (salades_op, 5)}}
    return (
        'salades',
        'salades',
        dothis,
        'salades\nИгра в салатики. Выберите из списка тот, который нужно убрать',
        0,
        None,
        'Игра в салатики'
    ), None, setts
