import os
import re
import time
import urllib.request

from Core.core import *
from acrcloud.recognizer import ACRCloudRecognizer

config = {
                    'host': 'identify-eu-west-1.acrcloud.com',
                    'access_key': 'd21cbdca7a7047fcf3480ba1260933c7',
                    'access_secret': 'u7fjeQULm6egJFu4mqWYjYRtHhfwRITuBnCG3n0V',
                    'debug': False,
                    'timeout': 10
                }

acrcloud = ACRCloudRecognizer(config)


def dothis(message):
    ans = ''
    if message.attachments['sound']:
        try:
            for attachment in message.attachments['sound']:
                dir = os.path.abspath(os.curdir) + \
                      '\\temp\\' + \
                      time.strftime("%Y%m%d-%H%M%S") + \
                      '.' + \
                      attachment[1]
                urllib.request.urlretrieve(attachment[0], dir)

                a = acrcloud.recognize_by_file(dir, 0)
                artist = re.search(r'"artists":\[{"name":"([^\"]+)"}]', a)
                title = re.search(r'"title":"([^\"]+)"', a)
                ans += f'>>>{artist.group(1)} - {title.group(1)}'\
                    if artist is not None and title is not None \
                    else '>>>Not found'
                ans += '\n'
                os.remove(dir)
        except Exception as f:
            ans = f
        finally:
            try:
                del message.cls.ACTIVE_COMMANDS[message.sendid]
            except KeyError:
                pass
            del message.attachments['sound']
            return str(ans)
    else:
        message.cls.ACTIVE_COMMANDS[message.sendid] = '!name'
        return 'Your sound?'


def main(ACTIVATES, GLOBAL_COMMANDS, *args):
    ACTIVATES.update({'sound_name': {'name'}})
    name = 'sound_name'
    currenthelp = '!name\nВыводит название песни'
    GLOBAL_COMMANDS[name] = Command(name, currenthelp, dothis, 0)