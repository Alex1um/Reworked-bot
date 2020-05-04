import os
from Core.core import Chat, Message, ChatSystem
import vk
import requests
import time
from types import *
import re


class VK(Chat):
    name = 'vk'
    LPS = 'server'
    vk_api = 'api'
    group_id = 123
    api_version = 0.
    msg_id = 0
    vk_api_user = 'api'
    find_id = re.compile(r'\[id(\d+)\|@\w+]')

    def input(self, res, id):
        try:
            if res is None or len(res['updates']) == 0:  # checking for right response
                pass
            else:
                for update in res['updates']:
                    if update['type'] == 'message_new':
                        Message(  # creating message
                            'vk',
                            id,
                            update,
                            self,
                        ).start()
        except KeyError:
            self.get_server()  # if error

    def send(self, res, id, rid, attachment=None):
        if not isinstance(res, (tuple, list)):
            res = [res]
        for text in res:
            if isinstance(text, str):
                self.vk_api.messages.send(peer_id=id,
                                          message=text,
                                          v=self.api_version,
                                          random_id=rid,
                                          attachment=attachment)  # sending message
            elif isinstance(text, GeneratorType):
                a = True
                for msg in text:
                    if a:
                        outid = self.vk_api.messages.send(peer_id=id,
                                                          message=msg,
                                                          v=self.api_version,
                                                          random_id=rid,
                                                          attachment=attachment)  # sending message
                        a = False
                    else:
                        self.vk_api.messages.edit(peer_id=id, message=msg, v=self.api_version, message_id=outid, attachment=attachment)

    def __init__(self, token, _group_id, v, main_system: ChatSystem):
        super().__init__(main_system)
        self.group_id = _group_id  # for group bots
        self.api_version = v  # api
        self.vk_api = vk.API(vk.Session(access_token=token))  # setting vk api
        self.get_server()

    def get_server(self):
        self.LPS = self.vk_api.groups.getLongPollServer(group_id=self.group_id, v=self.api_version)  # getting server

    def send_requsest(self, ts):
        link = f'{self.LPS["server"]}?act=a_check&key={self.LPS["key"]}&ts={ts}&wait=25'  # setting link
        res = requests.post(link).json()  # response
        if 'failed' in res.keys():
            if res['failed'] in (3, 4, 2):  # errors
                self.get_server()
                return None
        return res

    def run(self):
        while 1:
            try:  # for 'None' answer
                res = self.send_requsest(self.LPS['ts'])  # first request
                while 1:
                    res = self.send_requsest(res['ts'])  # next requests
                    print(res)
                    self.msg_id += 1
                    self.input(res, self.msg_id)
            except Exception as f:
                print(f)

    def message_parse(self, res):
        r_msg = ''
        attachments = res['object']['message']['attachments'] if not res['object']['message']['attachments'] else []
        if '-fwd' not in res['object']['message']['text'] or not res['object']['message']['fwd_messages']:  # for forward messages
            r_msg = res['object']['message']['text'].strip()
        else:  # для вложенных сообщений
            r_msg = res['object']['message']['text'][:res['object']['message']['text'].find('-fwd')]

            def find_fwd(fwd):
                msg = ''
                attach = []
                for message in fwd:
                    msg += message['text']
                    attach.extend(message['attachments'])
                    try:
                        ans = find_fwd(message['fwd_messages'])
                        msg += ans[0]
                        attach.extend(ans[1])
                    except KeyError:
                        continue
                return msg, attach

            ans = find_fwd(res['object']['message']['fwd_messages'])
            r_msg += ans[0]
            attachments.extend(ans[1])

            r_msg += res['object']['message']['text'][res['object']['message']['text'].find('-fwd') + 4::]
        r_date = res['object']['message']['date']  # date
        r_sendid = res['object']['message']['peer_id']  # from send
        r_userid = res['object']['message']['from_id']  # who send
        r_ctype = 'vk'
        r_attachments = {'image': [], 'sound': [], 'doc': []}
        for attachment in attachments:  # attachments
            if attachment['type'] == 'photo':
                r_attachments['image'].append(attachment['photo']['sizes'][-1]['url'])
            elif attachment['type'] == 'doc':
                if attachment['doc']['ext'] in {'wav', 'mp3'}:
                    r_attachments['sound'].append((attachment['doc']['url'], attachment['doc']['ext']))  # 0: link; 1: extension
            elif attachment['type'] == 'audio':
                r_attachments['sound'].append((attachment['audio']['url'], 'mp3'))
            elif attachment['type'] == 'audio_message':
                r_attachments['sound'].append((attachment['audio_message']['link_mp3'], 'mp3'))
        dbs = self.main_system.db_session
        session = dbs.create_session()
        set = session.query(dbs.Settings).filter((dbs.Settings.user_id == r_sendid) & (dbs.Settings.name == "active")).first()
        if set:
            if r_msg.find('end') != -1:  # exit from active commands
                if r_msg[:r_msg.find('end')] in self.main_system.defaut_command_symbols:
                    set.delete()
                    session.commit()
            else:
                r_msg = set.value + ' ' + r_msg
        for i in self.find_id.finditer(r_msg):  # for @links
            r_msg = r_msg[:i.start():] + i.group(1) + r_msg[i.end()::]
        return {'msg': r_msg,
                'date': r_date,
                'sendid': r_sendid,
                'type': r_ctype,
                'attachments': r_attachments,
                'userid': r_userid}

    def upload_doc(self, dir, from_id, type: 'audio_message' or 'doc'):
        pfile = requests.post(
            self.vk_api.docs.getMessagesUploadServer(
                type=type,
                peer_id=from_id,
                v=self.api_version)['upload_url'],
            files={'file': open(dir, 'rb')}).json()['file']
        doc = self.vk_api.docs.save(file=pfile, v=self.api_version)[type]
        return f"doc{doc['owner_id']}_{doc['id']}"

    def upload_photo(self, dir, from_id):
        pfile = requests.post(
            self.vk_api.photos.getMessagesUploadServer(
                peer_id=from_id,
                v=self.api_version
            )['upload_url'],
            files={'photo': open(dir, 'rb')}).json()
        doc = self.vk_api.photos.saveMessagesPhoto(server=pfile['server'],
                                                   photo=pfile['photo'],
                                                   hash=pfile['hash'],
                                                   v=self.api_version)[0]
        return f"photo{doc['owner_id']}_{doc['id']}"