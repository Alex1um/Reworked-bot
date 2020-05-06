import pickle


def dothis(message):

    def replace(lst1, lst2, text, a=True):
        text = text.strip().lower()
        res = [0] * len(text)
        i = 0
        while i < len(text):
            if text[i:i + 2] in lst1 if i < len(text) - 1 else False:
                res[i] = lst2[lst1.index(text[i:i + 2])]
                i += 1
            elif text[i] in lst1:
                res[i] = lst2[lst1.index(text[i])]
            elif a and text[i:i + 2] in lst2 if i < len(text) - 1 else False:
                res[i] = lst1[lst2.index(text[i:i + 2])]
                i += 1
            elif a and text[i] in lst2:
                res[i] = lst1[lst2.index(text[i])]
            else:
                res[i] = text[i]
            i += 1
        return ''.join(filter(lambda x: x != 0, res))

    def code(message, dd, mode):
        if mode == 'en':  # кодирование
            message = message.upper()
            message = message.replace(' ', '%321')  # кодирование символов
            message = message.replace('-', '—')
            message = message.replace('.', '...... ')
            message = message.replace('%321', '-...- ')
            for k, v in dd.items():  # остальные символы
                message = message.replace(k, v)
            return message.replace('.', '•').replace('-', '−')
        elif mode == 'de':  # декодирование
            message = message.replace('•', '.').replace('−', '-')
            if message[-1] != ' ':
                message += ' '
            message = message.replace('...... ', '%3213')  # символы используемые в морзе
            message = message.replace('-...- ', '%111')
            for k, v in dd.items():  # все символы
                message = message.replace(v, k)
            message = message.replace('%3213', '.')  # символы используемые в морзе
            message = message.replace('%111', ' ')
            return message.lower()

    p = message.params
    if len(p) > 0:
        try:
            if p[0] == 'er':
                return replace(
                    ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', "o", 'p', '[', ']', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.'),
                    ('й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э', 'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю'), ' '.join(p[1::]), False)
            elif p[0] == 'tr1':
                return replace(
                    ('sh', "sh", 'ch', 'ja', "'u", "'", 'y', 'u', 'k', 'e', 'n', 'g', 'z', 'h', "'", 'f', 'i', 'v', 'a', 'p', 'r', 'o', 'l', 'd', 'j', "e", 's', 'm', 'i', 't', 'b',  'c'),
                    ('ш',  'щ',  'ч',  'я',  'ю',  'ь', 'й', 'у', 'к', 'е', 'н', 'г', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э', 'с', 'м', 'и', 'т', 'б',  'ц'), ' '.join(p[1::]))
            elif p[0] == 'tr2':
                return replace(
                    ("'a", "'u", 'y', 'c', 'u', 'k', 'e', 'n', 'g', 'w', "w", 'z', 'h', "'", 'f', 'i', 'v', 'a', 'p', 'r', 'o', 'l', 'd', 'j', "e", '4', 's', 'm', 'i', 't', "'", 'b'),
                    ('я',  'ю',  'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б'), ' '.join(p[1::]))
            elif p[0] == 'morse':
                if p[1] in {'rus', 'eng'}:
                    if p[2] in {'en', 'de'}:
                        f = open(fr'commands\\files\\morse_{p[1]}.tr', 'rb')
                        return code(' '.join(p[3::]), pickle.load(f), p[2])
                        f.close()
                return '!translate morse {rus|eng} {en|de} {text}'
        except:
            pass
    return '!translate {er|tr1|tr2|morse} {text}'


def main():
    return ("translate",
            "tr translate",
            dothis,
            'translate | tr {er | tr1 | tr2}\n'
            'translate | tr morse {rus | eng} {en | de}\n'
            'Перевод текста ',
            0,
            None,
            "Перевод текста"), None, None
