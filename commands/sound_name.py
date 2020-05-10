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
    """
    get sound name with acrcloud
    :param message:
    :return: possible song names
    """
    session = message.get_session()
    ans = ''
    current_cmd = message.get_setting(session, 'active')
    if message.attachments['sound']:
        try:
            for attachment in message.attachments['sound']:
                dir = os.path.abspath(os.curdir) + \
                      '/temp/' + \
                      time.strftime("%Y%m%d-%H%M%S") + \
                      '.' + \
                      attachment[1]
                urllib.request.urlretrieve(attachment[0], dir)

                res = eval(acrcloud.recognize_by_file(dir, 0))
                print(res)
                if 'error' in res['status']['msg'].lower():
                    if current_cmd:
                        message.delete_active(session)
                    return 'Произошла ошибка'
                if res['status']["msg"] != "No result":
                    # artist = re.search(r'"artists":\[{"name":"([^\"]+)"}]', a)
                    for song in res["metadata"]["music"]:
                        artist = ', '.join(map(lambda x: x['name'],
                                               song["artists"]))
                    # title = re.search(r'"title":"([^\"]+)"', a)
                        title = song['title']
                        new_song = f'>>{artist} - {title}'
                        if new_song not in ans:
                            ans += f'>>{artist} - {title}'
                            ans += '\n'
                else:
                    ans += 'Не найдено'
                yield ans
                ans += "\n"
                os.remove(dir)
        except Exception as f:
            ans += "Произошла непредвиденная ошибка: " + str(f) + "\n"
            raise f
        finally:
            if current_cmd:
                message.delete_active(session)
            yield str(ans)
    elif 'Выход' in message.params and current_cmd:
        session.delete(current_cmd)
        return {'msg': 'Успешно!', 'keyboard': [[], False]}
    else:
        if current_cmd is None:
            message.add_setting(session, 'active', 'name')
        yield {'msg': 'Прикрепите аудио или напишите Выход',
               'keyboard': [[[('Выход', 'negative')]], False]
               }


def main():
    return ("sound_name",
            "name",
            dothis,
            "name\n"
            "Найти назваине песни.\n"
            "Для работы нужно прикрепить аудио - голосовое сообщение или"
            " музыкальный файл",
            1,
            None,
            "Найти название песни"), None, None
