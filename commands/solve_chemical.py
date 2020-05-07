from Core.core import *
from commands.stupidAI.tools import ChemicalEquations as Ce
from bs4 import BeautifulSoup as bs
import requests
import re


index_dict = {'0': '₀',
              '1': '₁',
              '2': '₂',
              '3': '₃',
              '4': '₄',
              '5': '₅',
              '6': '₆',
              '7': '₇',
              '8': '₈',
              '9': '₉'}


def dothis(msg: Message):
    img, url = Ce.solve_equation(Ce.is_equation(msg.text))

    if url:
        # ff = session.get(img)
        # img = Image.open(io.BytesIO(ff.content))
        page = requests.get(url)
        page.encoding = 'utf-8'
        parsed = bs(page.content, 'html.parser')
        text = parsed.find('div', {'class': 'reactBody'}).contents[0].strip()
        equation = repr(parsed.find('div', {'class': 'reacth2'}).contents[0])[4:-5]
        for k, v in index_dict.items():
            equation = equation.replace(f'<sub>{k}</sub>', v)
        return text + '\n' + equation
    else:
        return 'Реакции не найдено'


def main():
    return ("solve_chemical",
            "solchem",
            dothis,
            'solchem {химическое уравнение}\n'
            'Решить зимическое уравнение - Получить полное уравнение реакции'
            ' по реагентам или продуктам\n'
            'Например при вводе реакции {HCl + NaOH}, выведеться\n'
            '{HCl + NaOH = NaCl + H2O}',
            0,
            None,
            'решение химических уравнений'), None, None