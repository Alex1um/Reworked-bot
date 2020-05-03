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
    mode = p[0] if len(p) > 0 else 'i'
    if mode in array_calls:
        return str(situations[mode](p[1::]))
    else:
        a, b = int(p[1]) if len(p) > 1 else 0, int(p[2]) if len(p) > 2 else 0 if len(p) == 2 else 100
        return str(situations[mode](min(a, b), max(b, a)))


def main():
    return ("random", 'r random', dothis, '!random / !r {int|float|coin|array|shuffle|random} {value} {value} | values...', 0, None), None, None
