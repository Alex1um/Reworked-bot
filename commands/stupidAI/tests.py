from commands.stupidAI import parser
from commands.stupidAI.tools import *

a = {'а': {'a'},
            "б": {'b'},
            "в": {'v'},
            "г": {'g'},
            "д": {'d'},
            "е": {'e'},
            "ё": {'jo', 'yo'},
            "ж": {'zh'},
            "з": {'z'},
            "и": {'i'},
            "й": {'j'},
            "к": {'k'},
            "л": {'l'},
            "м": {'m'},
            "н": {'n'},
            "о": {'o'},
            "п": {'p'},
            "р": {'r'},
            "с": {'s'},
            "т": {'t'},
            "у": {'u'},
            "ф": {'f'},
            "х": {'h', 'x'},
            "ц": {'c'},
            "ч": {'ch'},
            "ш": {'sh'},
            "щ": {'shh', 'w'},
            "ъ": {'##', '#', '/', 'tz'},
            "ы": {'y'},
            "ь": {"'", '"', 'mz'},
            "э": {'je'},
            "ю": {'ju', 'yu'},
            "я": {'ja', 'ya', 'q'}}
# ns = {}
# for k, v in a.items():
#     for vv in v:
#         ns[vv] = k
# print(dict(sorted(ns.items(), key=lambda x: len(x[0]), reverse=1)))
# a = r"qwertyuiop[]asdfghjkl;'zxcvbnm,.`"
# b = r"йцукенгшщзхъфывапролджэячсмитьбюё"
# print(dict(zip(a, b)))
# print(parser.sent_correction('ghbdtn vbh!'))
# print(parser.sent_correction('yjdjcnb cgjhn dbhec'))
# print(parser.sent_correction('htib'))
# print(parser.sent_correction('reshi'))
# print(parser.alternative_analyzer('yjdjcnb cgjhn'))
# print(parser.alternative_analyzer('новости спорт'))
print(ChemicalEquations.solve_equation(ChemicalEquations.is_equation('h2so4+koh')))