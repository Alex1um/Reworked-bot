from random import sample, randint, shuffle
from pickle import load
from Core.core import *
from ast import literal_eval
import os


def salades_op(params, system: ChatSystem, message):
    session = system.db_session.create_session()
    salades_file = message.get_setting(session, 'salades_file')

    file = salades_file.value if salades_file else None
    prev_param = message.params[-1]
    if prev_param == 'current':
        return file if file else 'food'
    elif prev_param == 'switch' and params:
        if params[0] in map(lambda x: x[x.rfind('/') + 1:x.rfind('.'):],
                            glob.glob("commands/files/*.saladict")):
            file = params[0]
        else:
            return 'Файл не найден'
    elif prev_param == 'list':
        return '\n'.join(map(lambda x: x[x.rfind('/') + 1:x.rfind('.'):],
                             glob.glob("commands/files/*.saladict")))
    elif prev_param == 'default':
        session.delete(salades_file)
        file = None
    elif prev_param == 'max':
        salades_max = message.get_setting(session, 'salades_max')

        if params and params[0] != '4' and params[0].isdigit():
            if salades_max is None:
                message.add_setting(session, 'salades_max', params[0])
            else:
                salades_max.value = int(params[0])
        else:
            return salades_max.value if salades_max else '4'
    if file:
        if salades_file:
            salades_file.value = file
        else:
            message.add_setting(session, 'random_talks_file', file)
            # session.add(system.db_session.Settings(
            #     message.userid, 'random_talks_file', file))
    session.commit()
    return 'Success'


def dothis(message):
    session = message.get_session()
    salades_file = message.get_setting(session, 'salades_file')
    salades_file = salades_file.value if salades_file else 'food'
    salades_max = message.get_setting(session, 'salades_max')
    salades_max = int(salades_max.value) if salades_max else 6
    salades_set = message.get_setting(session, 'salades')
    active = message.get_setting(session, 'active')
    if active and 'Выход' in message.params:
        message.delete_active(session)
        return {'msg': 'Успешно!', 'keyboard': [[], False]}
    elif active is None:
        message.add_setting(session, 'active', 'salades')

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
            args[i] = sample(
                e, randint(le // 2 + 1, le)
            ) + sample(words, randint(0, salades_max - le))
        return args

    words = []
    with open(f"{os.getcwd()}/commands/"
              f"files/{salades_file}.saladict", 'rb') as f:
        words = load(f)
    if salades_set is None:
        salades = [sample(words, randint(4, salades_max)),
                   sample(words, randint(4, salades_max)),
                   sample(words, randint(4, salades_max))]
        message.add_setting(session, 'salades', str(salades))
    else:
        salades = literal_eval(salades_set.value)
    if message.params and message.params[0].isdigit():
        kill = int(message.params[0])
        salades.pop(kill - 1)
        salades = conc(*salades)
        salades_set.value = str(salades)
        session.commit()
    ans = '\n'.join(
        (
            str(n + 1) + '.' + str(
                salad
            )[1:-1].replace("'", '') for n, salad in enumerate(salades)))
    return {'msg': 'Ваша задача получить лечший по вашему мнению салатик.\n'
                   'Для этого выберите(напишите) номер худшего салатика.\n'
                   '(или напишите Выход для выхода из игры)\n\n' + ans,
            'keyboard': [[['1', '2', '3'], [('Выход', 'negative')]], False]}


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
        'salades, далее просто {число}\n'
        'Игра в салатики.\n'
        'Игра основанна на генетическом алгоритме. В каждом поколении вам'
        ' предлагается выбрать один из 3-х "салатиков", по вашему мнению '
        'худший. Таким образом убираются худшие ингредиенты, а остальные '
        'перемешиваются и составляются новые салатики.\n'
        'Салатики могут мутировать, т.е. '
        'в них могут появиться или исчезнуть новые ингедиенты',
        0,
        None,
        'Игра в салатики'
    ), None, setts
