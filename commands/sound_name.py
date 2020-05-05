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
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    ans = ''
    current_cmd = session.query(
        system.db_session.Settings).filter(
        (system.db_session.Settings.user_id == message.userid) &
        (system.db_session.Settings.name == "active")).first()
    print(message.attachments)
    if message.attachments['sound']:
        try:
            for attachment in message.attachments['sound']:
                dir = os.path.abspath(os.curdir) + \
                      '\\temp\\' + \
                      time.strftime("%Y%m%d-%H%M%S") + \
                      '.' + \
                      attachment[1]
                urllib.request.urlretrieve(attachment[0], dir)

                res = eval(acrcloud.recognize_by_file(dir, 0))
                print(res)
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
                    os.remove(dir)
                else:
                    ans += 'Не найдено'
                yield ans
                ans += "\n"
        except Exception as f:
            ans += "Произошла непредвиденная ошибка: " + str(f) + "\n"
            raise f
        finally:
            if current_cmd:
                session.delete(current_cmd)
                session.commit()
            return str(ans)
    elif '-exit' in message.params and current_cmd:
        session.delete(current_cmd)
        session.commit()
    else:
        if current_cmd is None:
            session.add(system.db_session.Settings(
                message.userid,
                'active',
                system.defaut_command_symbols[0] + "name"))
            session.commit()
        return 'Прикрепите аудио или напишите -exit'


def main():
    return ("sound_name",
            "name",
            dothis,
            "name\n"
            "Найти назваине песни. Нужно прикрепить аудио",
            0,
            None,
            "Найти название песни"), None, None
