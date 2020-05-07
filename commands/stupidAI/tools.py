import math
import re
from string import ascii_lowercase
from typing import *
# import numpy as np
# from scipy.optimize import fsolve
from bs4 import BeautifulSoup as bs
import requests

names = {i for i in dir(math) if i[:2] != '__'}
names |= set(ascii_lowercase)


def make_fun_stable(f, default=None):
    def new_fun(*args, **kwargs):
        nonlocal f, default
        try:
            return f(*args, **kwargs)
        except Exception:
            return default

    return new_fun


class ChemicalEquations:
    _elements = {'pa', 'cd', 'er', 'n', 'am', 'fr', 'au', 'db', 'po', 'nh', 'k', 'ra', 'f', 'pu', 'cf', 'co', 'eu', 'rn', 'cs', 'mn', 'ag', 'sn', 'he', 'np', 'nb', 'bk', 'ga', 'fl', 'es', 'y', 'zn', 'al', 'sm', 'h', 'na', 'pr', 'pm', 'cr', 'tm', 'p', 'cu', 'gd', 'ce', 'v', 'in', 'md', 'tc', 'rb', 'br', 'pt', 'sg', 'tb', 'ge', 'cm', 'rg', 'ac', 'b', 'fm', 'mo', 'nd', 'li', 'mc', 'ne', 'ir', 'pd', 'ta', 'ba', 'sb', 'dy', 'og', 'at', 'rf', 'ca', 'lr', 'u', 'yb', 'i', 'lv', 'cn', 'kr', 'mg', 'bi', 'c', 'mt', 'fe', 's', 'hs', 'ts', 'os', 'hg', 'sr', 'la', 'ho', 'ru', 'si', 'zr', 'xe', 'as', 'bh', 'ds', 'lu', 'ar', 'tl', 'te', 'rh', 'pb', 'th', 'be', 'hf', 'no', 'ti', 'o', 'se', 'cl', 're', 'w', 'sc', 'ni'}
    _re_subs = re.compile(r'(\d?\w+)[^+\-]?')

    @staticmethod
    def is_equation(s: str):
        eq = ''
        for matter in ChemicalEquations._re_subs.findall(s.lower()):
            for i in range(1, len(matter)):
                if all(i not in ChemicalEquations._elements for i in (matter[i], matter[i - 1:i + 1], matter[i: i + 2])) and not matter[i].isdigit():
                    break
            else:
                eq += matter + '+'
        return eq[:-1]

    @staticmethod
    def solve_equation(reaction: str) -> str and str or None and None:
        """
        get solved equation
        :param reaction:
        :return: link for image
        """
        req = 'https://chemiday.com/search/'
        params = {"q": reaction,
                  "m": "board"}

        res = requests.get(req, params)
        res.encoding = 'utf-8'
        parsed = bs(res.content, 'html.parser')
        img = parsed.find("img", {"alt": "Реакция"})
        addit = parsed.find("div", {'class': "rus"})
        return ("https://chemiday.com" + img['src'], addit.contents[0]['href']) if img and addit else (None, None)


print(ChemicalEquations.solve_equation('Hcl+Naoh'))
# print(ChemicalEquations.is_equation("Сделай это: H2SO4 + NaOH"))
# print(1)
# print(ChemicalEquations.is_equation("вот уравнение: nacl+AgNO3"))
# print(ChemicalEquations.is_equation("naoh + hcl"))
# print(ChemicalEquations.is_equation('h2o2+KMnO4+h2so4'))

class Equations:
    __wrong_power = re.compile(r'\d[a-z(]')
    __any_sym = re.compile(r'[+\-*/()^\[\]a-z\d\s]+')
    re_any_word = re.compile(r'[a-z]+')
    __re_pow = re.compile(r'\*\*(\d*)')

    @staticmethod
    def is_equation(s: str) -> bool:
        if s != ' ':
            return False if set(Equations.re_any_word.findall(s.lower())) - names else True

    @staticmethod
    def parse_eq(eq: str) -> Callable and int:
        parsed = eq
        a = Equations.__wrong_power.findall(parsed)
        for e in a:
            ne = e[0] + '*' + e[1]
            parsed = parsed.replace(e, ne).replace('^', '**')
        try:
            # return vectorize(make_fun_stable(eval('lambda x: ' + parsed))),\
            #        int(max(Equations.__re_pow.findall(parsed), key=lambda x: int(x)))
            return make_fun_stable(eval('lambda x: ' + parsed)), \
                   int(max(Equations.__re_pow.findall(parsed),
                           key=lambda x: int(x)))
        except Exception as f:
            return f

    @staticmethod
    def solve_equation(eq: Callable, roots: int) -> set or Exception:
        try:
            # a = np.round(fsolve(eq, np.arange(-100, 100, 200 / roots / 5), xtol=1e-12), 3)
            a = "not working yet"
            return set(a)
        except Exception as f:
            return f

    @staticmethod
    def find_eq(text) -> tuple:
        return tuple(i for i in Equations.__any_sym.findall(text) if Equations.is_equation(i))


# eqs = Equations.find_eq("x**2-2x-5")
# for eq in eqs:
#     eq, roots = Equations.parse_eq(eq)
#     rest = Equations.solve_equation(eq, roots)
#     print(rest)
#     res = 'x ∈ ' + str(rest) if len(rest) <= roots else None
#     print(res)
#     stat = 'acpt'