from Core.core import Command
import time
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import requests

def asd(message):
    if message.params[0] != 'test':
        for i in range(int(message.params[0])):
            yield str(i) + ' ' + morph.parse('манул')[0].make_agree_with_number(i).word
            time.sleep(0.5)
    else:
        try:
            # print(1)
            # server = message.cls.vk_api.docs.getMessagesUploadServer(
            #     type='audio_message', peer_id=message.sendid,
            #     v=message.cls.api_version)
            # pfile = requests.post(server['upload_url'],
            #                       files={'file': open('1.wav', 'rb')}).json()
            # print(2)
            # doc = message.cls.vk_api.docs.save(file=pfile['file'],
            #                                    title='test',
            #                                    v=message.cls.api_version)
            # print(3)
            # return 'Do not play thiz', f'doc{doc["audio_message"]["owner_id"]}_{doc["audio_message"]["id"]}' #doc['audio_message']
            attach = message.cls.upload_doc('1.mp3', message.sendid, 'audio_message')
            return 'hello', attach
        except FileNotFoundError:
            print('not found')
            return 0


def main(activates: dict, global_commands: dict, passive: list, global_settings: dict):
    activates.update({'test': ('t', 'test')})
    global_commands['test'] = Command('test', '', asd, 8)
