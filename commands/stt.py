import os
import time
import urllib
import subprocess
from Core.core import *
from speech_recognition import AudioFile, Recognizer

langs = {'ru': 'ru-RUS', 'en': 'en-EN'}
witkey = 'GQ2ITHTRXYD2WVOPYOZ3AEY3NRBLNIS3'


def dothis(message):
    if message.attachments['sound']:
        try:
            r = Recognizer()
            mode = 'google'
            lang = 'ru-RUS'
            ans = ''
            for attachment in message.attachments['sound']:
                print(attachment, message.attachments)
                ext = attachment[1]
                path = os.path.abspath(os.curdir)
                fname = time.strftime("%Y%m%d-%H%M%S") + '.'
                dir = path + '\\temp\\' + fname
                urllib.request.urlretrieve(attachment[0], dir + ext)  # getting file

                if ext != 'wav':
                    subprocess.run(['ffmpeg', '-i', dir + ext, dir + 'wav'])
                    os.remove(dir + ext)

                with AudioFile(dir + 'wav') as source:
                    song = r.record(source)
                os.remove(dir + 'wav')

                if len(message.params) > 0:
                    lang = langs[message.params[0]].lower() if message.params[0].lower() in langs.keys() else 'en-EN'
                    if len(message.params) > 1:
                        mode = 'wit' if message.params[1].lower() == 'wit' else 'google'
                ans += f">>>>>>{r.recognize_google(song, language=lang) if mode == 'google' else r.recognize_wit(song, witkey)}\n"
                print(ans)
                yield ans
        except Exception as f:
            ans = f
        finally:
            try:
                del message.cls.ACTIVE_COMMANDS[message.sendid]
            except KeyError as f:
                pass
            del message.attachments['sound']
            yield str(ans)
    else:
        message.cls.ACTIVE_COMMANDS[message.sendid] = message.msg
        return 'Your sound?'


def main(ACTIVATES, GLOBAL_COMMANDS, *args):
    ACTIVATES.update({'speech_to_text': {'stt'}})
    name = 'speech_to_text'
    currenthelp = '!stt\nРаспознование песни'
    stt = Command(name, currenthelp, dothis, 0)
    GLOBAL_COMMANDS[name] = stt
