import time
import urllib
import subprocess
from Core.core import *
from speech_recognition import AudioFile, Recognizer

langs = {'ru': 'ru-RUS', 'en': 'en-EN'}
witkey = 'GQ2ITHTRXYD2WVOPYOZ3AEY3NRBLNIS3'


def dothis(message):
    """
    From speech to text
    :param message:
    :return: text
    """
    session = message.get_session()
    ans = ''
    current_cmd = message.get_setting(session, 'active')
    if message.attachments['sound']:
        try:
            r = Recognizer()
            mode = 'google'
            lang = 'ru-RUS'
            ans = ''
            for attachment in message.attachments['sound']:
                ext = attachment[1]
                path = os.path.abspath(os.curdir)
                fname = time.strftime("%Y%m%d-%H%M%S") + '.'
                dir = path + '/temp/' + fname
                urllib.request.urlretrieve(
                    attachment[0], dir + ext)  # getting file

                if ext != 'wav':
                    subprocess.run(['ffmpeg', '-i', dir + ext, dir + 'wav'])
                    os.remove(dir + ext)

                with AudioFile(dir + 'wav') as source:
                    song = r.record(source)
                os.remove(dir + 'wav')

                if "en" in message.params:
                    lang = 'en-EN'
                if 'wit' in message.params:
                    mode = 'wit'
                recg = r.recognize_google(
                    song,
                    language=lang
                ) if mode == 'google' else r.recognize_wit(song, witkey)
                ans += f">>>>>>{recg}\n\n"
                yield ans
        except Exception as f:
            ans += "Произошла непредвиденная ошибка: " + str(f) + "\n"
        finally:
            if current_cmd:
                message.delete_active(session)
            yield str(ans)
    elif 'Выход' in message.params and current_cmd:
        message.delete_active(session)
        yield {'msg': 'Успешно!', 'keyboard': [[], False]}
    else:
        if current_cmd is None:
            message.add_setting(session, 'active', 'stt')
        yield {'msg': 'Прикрепите аудио или напишите Выход',
               'keyboard': [[[('Выход', 'negative')]], False]
               }


def main():
    return ("speech_to_text",
            'stt',
            dothis,
            'stt {язык(ru - по умолчанию | en)} {система(google - '
            'по умолчанию | wit)}\n'
            'Прикрепите аудио - голосовое сообщение или аудиофайл\n'
            'Распознование речи в аудио или голосовом сообщении',
            0,
            None,
            "Распознование речи в аудио"), None, None
