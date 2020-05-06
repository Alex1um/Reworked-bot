import time
import urllib
import subprocess
from Core.core import *
from speech_recognition import AudioFile, Recognizer

langs = {'ru': 'ru-RUS', 'en': 'en-EN'}
witkey = 'GQ2ITHTRXYD2WVOPYOZ3AEY3NRBLNIS3'


def dothis(message):
    # system: ChatSystem = message.cls.main_system
    # session = system.db_session.create_session()
    session = message.get_session()
    ans = ''
    current_cmd = message.get_setting(session, 'active')
    # current_cmd = session.query(
    #     system.db_session.Settings).filter(
    #     (system.db_session.Settings.user_id == message.userid) &
    #     (system.db_session.Settings.name == "active")).first()
    print(message.attachments)
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
                dir = path + '\\temp\\' + fname
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
                session.delete(current_cmd)
                session.commit()
            yield str(ans)
    elif '-exit' in message.params and current_cmd:
        session.delete(current_cmd)
        session.commit()
    else:
        if current_cmd is None:
            session.add(system.db_session.Settings(
                message.userid,
                'active',
                system.defaut_command_symbols[0] + "stt"))
            session.commit()
        yield 'Прикрепите аудио или напишите -exit'


def main():
    return ("speech_to_text",
            'stt',
            dothis,
            'stt {язык(ru - по умолчанию | en)} {система(google - '
            'по умолчанию | wit)}прикрепите аудиофайл\nРаспозновани'
            'е речи в аудио',
            0,
            None,
            "Распознование речи в аудио"), None, None
