from Core.core import ChatSystem
import random


def dothis(message):
    array_calls = ('ar', 'array', 'shuffle')
    situations = {
        'int': lambda x, y: random.randint(x, y),
        'i': lambda x, y: random.randint(x, y),
        'f': lambda x, y: random.uniform(x, y),
        'float': lambda x, y: random.uniform(x, y),
        'array': lambda x, y=None: random.choice(x),
        'ar': lambda x, y=None: random.choice(x),
        'coin': lambda x=None, y=None: random.choice(('HEADS', 'TAILS')),
        'shuffle': lambda x, y=None: ' '.join((random.shuffle(x), x)[1]),
        'r': lambda x=None, y=None: random.random(),
        'random': lambda x=None, y=None: random.random()
    }
    p = message.params
    mode = p[0] if len(p) > 0 and p[0] in situations.keys() else 'i'
    if mode in array_calls:
        return str(situations[mode](p[1::]))
    else:
        a = int(p[1]) if len(p) > 1 else 0
        b = int(p[2]) if len(p) > 2 else 0 if len(p) == 2 else 100
        return str(situations[mode](min(a, b), max(b, a)))


def main():
    help_msg = """!random | !r {int|float|coin|array|shuffle|random} {value} {value} | values...
    int - случайное целое число в заданном диапазоне(от 0 до 100 по умолчанию)
    float - случайное дробное число в заданном диапазоне(от 0 до 100 по умолчанию)
    coin - бросить монетку
    array - выбрать случайный член из заданного через пробел списка
    shuffle - перемешать заданный через пробел список
    random - случайное число от 0 до 1"""
    return ("random",
            'r random',
            dothis,
            help_msg,
            0,
            None,
            "Рвзличный рандом"), None, None
