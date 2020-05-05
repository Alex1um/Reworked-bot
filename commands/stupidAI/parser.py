import nltk
from pymorphy2.analyzer import MorphAnalyzer
# from .tools import Equations as Eq
from commands.stupidAI.tools import Equations as Eq
from commands.stupidAI.tools import ChemicalEquations as Ce
import wikipedia
from string import ascii_lowercase
import random
import re

analyzer = MorphAnalyzer()
signs = re.compile(r'[!?,.]')
translit = {'shh': 'щ', 'jo': 'ё', 'yo': 'ё', 'zh': 'ж', 'ch': 'ч', 'sh': 'ш', '##': 'ъ', 'tz': 'ъ', 'mz': 'ь', 'je': 'э', 'ju': 'ю', 'yu': 'ю', 'ja': 'я', 'ya': 'я', 'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'e': 'е', 'z': 'з', 'i': 'и', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'f': 'ф', 'x': 'х', 'h': 'х', 'c': 'ц', 'w': 'щ', '/': 'ъ', '#': 'ъ', 'y': 'ы', '"': 'ь', "'": 'ь', 'q': 'я'}
error = {'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю', '`': 'ё'}


def from_translit(word: str, trs: dict = translit):
    i = 0
    formated = ''
    ll = len(word)
    while ll != i:
        for k, v in trs.items():
            ll1 = len(k)
            if word[i:ll1 + i] == k:
                formated += v
                i += ll1
                break
        else:
            if word[i].isalpha():
                formated += word[i]
            i += 1
        l1 = len(word)
    return formated


# print(from_translit('ty zhopa'))
# print(from_translit('ты молодец, а я нет privet'))
def sent_correction(string: str):
    corrected = ''
    for word in string.split():
        parsed = analyzer.parse(from_translit(word))
        if parsed[0].score >= 0.65 and parsed[0].tag.POS:
            corrected += parsed[0].word + " "
        else:

            parsed = analyzer.parse(from_translit(word, error))
            if parsed[0].score >= 0.3 and parsed[0].tag.POS:
                corrected += parsed[0].word + " "
            else:
                corrected += word + " "
    return corrected.strip()


def normalize_sent(string: str) -> str:
    try:
        self_string = signs.sub('', string)
    except re.error:
        self_string = string
    for word in set(string.split(' ')):
        pw = analyzer.parse(word)[0]
        if pw.score > 0.9:
            self_string = self_string.replace(word, pw.word)
    return self_string


def alternative_analyzer(sent: str) -> dict:
    parsed = {'subject': [],
              'predicate': [],
              'addition': [],
              'circumstance': [],
              'definition': []}
    words = sent_correction(sent).split()
    # words = sent.split()
    print(words)
    tags = tuple(map(lambda x: analyzer.parse(x)[0].tag, words))
    print(tags)
    for i in range(len(sent.split())):
        if words[i] in {'-', '—'} and parsed['subject']:
            parsed['predicate'].extend([(words[j], tags[j]) for j in range(i + 1, len(words))])
        if tags[i].POS == 'NOUN':  # существительное
            if tags[i].case == 'nomn':
                parsed['subject'].append((words[i], tags[i]))
            else:
                parsed['addition'].append((words[i], tags[i]))
        elif tags[i].POS == 'NPRO':  # местоимение
            if tags[i].case == 'nomn':
                parsed['subject'].append((words[i], tags[i]))
        elif tags[i].POS in {'VERB', 'ADJS'}:  # сказуемое
            parsed['predicate'].append((words[i], tags[i]))
        elif tags[i].POS == 'INFN':
            if words[i - 1] in parsed['predicate']:
                parsed['predicate'].append((words[i], tags[i]))
        elif tags[i].POS == 'NUMR':
            if tags[i + 1].POS == 'NOUN':
                parsed['subject'].append((words[i], tags[i]))
        elif tags[i].POS == 'PREP':
            if tags[i - 1].POS == 'NOUN':
                parsed['subject'].append((words[i], tags[i]))
    return parsed

# print(alternative_analyzer("reshi h2so4+hcl"))
# print(alternative_analyzer("новости спорт"))


def get_info(word: str, addition=None) -> (str, bool):
    wikipedia.set_lang('ru' if word[0] not in ascii_lowercase else 'en')
    res = wikipedia.search(word if addition is None else word + ' ' + addition, results=1)
    if res:
        try:
            return wikipedia.summary(res[0]), 'acpt'
        except Exception as f:
            return f, 'add'


def parse2(string: str, string2: str = None):
    res = ''
    parsed = alternative_analyzer(string.lower())
    # print(parsed)
    if parsed['predicate']:
        if parsed['predicate'][0][0] in {'реши', 'вычисли', 'посчитай'}:
            # print(1, string)
            eqs = Eq.find_eq(string)
            if eqs:  # решить уравнение
                print("this is equation ")
                for eq in eqs:
                    eq, roots = Eq.parse_eq(eq)
                    res = Eq.solve_equation(eq, roots)
                    res = 'x ∈ ' + str(res) if len(res) <= roots else None
                    stat = 'acpt'
                    return res, stat
            elif Ce.is_equation(string):
                print("this is chemical equation!")
                return 'solve_chemical', 'invoke'
                # stat = 'acpt'
                # return Ce.solve_equation(eq), stat
        elif parsed['predicate'][0][0] in {'скажи', 'напиши'} and parsed['subject']:
            print(2)
            req = ' '.join(i[0] for i in parsed['subject'] if i[1].POS not in {'CONJ'})  # получить информаци.
            res, stat = get_info(req, string2)
        elif parsed['predicate'][0][0] in {'выбери', 'скажи'} and bool(parsed['subject']):
            print(3)
            return 'я думаю ' + str(random.choice(tuple(map(lambda x: x[0], parsed['subject'] + parsed['addition'])))), 'acpt'
        elif parsed['predicate'][0][0] in {'переведи'}:
            print(4)
            return 'speech_to_text', 'invoke'
        elif parsed['predicate'][0][0] in {'распознай'}:
            print(5)
            return 'sound_name', 'invoke'
    elif parsed['predicate'] and parsed['predicate'][0][0] in {'происходит'} and parsed['addition'][0][0] in {'мире'} or parsed['addition'][0][0] in {'новости'}:
        print(6)
        return 'get_news', 'invoke'
    return res, stat


# print(parse2("реши h2so4 + naoh"))
# print(parse2("reshi h2so4 + naoh"))
# print(parse2('реши: x**2-8x+3'))
# parse2('Моя мама (кто она такая?) — швея')
# parse2('скажи что такое Человек')
# parse2('Кто такой билл гейтс')
# parse2('Что такое сверчок')
# parse2('Скажи пожалуйста кто такой билл гейтс')
# parse2('Сколько будет 2+2?')