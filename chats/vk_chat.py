from Core.core import Chat, Message, ChatSystem
import vk
import requests
from types import *
from typing import *
import json


class VK(Chat):
    name = 'vk'
    LPS = 'server'
    vk_api = 'api'
    group_id = 123
    api_version = 0.
    msg_id = 0
    vk_api_user = 'api'

    def input(self, res, id):
        """
        catch messages from response
        :param res: json response from long poll server
        :param id: message id
        :return:
        """
        try:
            if res is None or len(
                    res['updates']) == 0:  # checking for right response
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

    def send(self, res, id, rid, attachment=None, keyboard=None):
        """
        sending message to user depending on the type returned by the command
        :param res: returned by command
        :param id: from user id
        :param rid: to user id
        :param attachment: attachments
        :param keyboard: keyboard if available
        :return:
        """
        if not isinstance(res, (tuple, list)):
            res = [res]
        for text in res:
            if isinstance(text, str):
                self.vk_api.messages.send(peer_id=id,
                                          message=text,
                                          v=self.api_version,
                                          random_id=rid,
                                          attachment=attachment,
                                          keyboard=keyboard
                                          )  # sending message
            elif isinstance(text, GeneratorType):  # generator type - edit
                first = True
                for msg in text:
                    if isinstance(msg, tuple):
                        answer, attachment = msg
                    elif isinstance(msg, dict):
                        k = msg.keys()
                        answer = msg['msg'] if 'msg' in k else '...'
                        attachment = msg['attachment'] if \
                            'attachment' in k else None
                        keyboard = msg['keyboard'] if 'keyboard' in k else None
                    else:
                        answer = msg
                    if first:
                        outid = self.vk_api.messages.send(peer_id=id,
                                                          message=answer,
                                                          v=self.api_version,
                                                          random_id=rid,
                                                          attachment=attachment,
                                                          keyboard=self.
                                                          make_keyboard(
                                                              *keyboard
                                                          )
                                                          )  # sending message
                        first = False
                    else:
                        self.vk_api.messages.edit(
                            peer_id=id,
                            message=msg,
                            v=self.api_version,
                            message_id=outid,
                            attachment=attachment,)

    def __init__(self, token, _group_id, v, main_system: ChatSystem):
        """
        initialising Vk chat
        :param token: Group token to use group features
        :param _group_id: group id
        :param v: api version
        :param main_system: ChatSystem class
        """
        super().__init__(main_system)
        self.group_id = int(_group_id)  # for group bots
        self.api_version = float(v)  # api
        self.vk_api = vk.API(vk.Session(access_token=token))  # setting vk api
        self.get_server()

    def get_server(self) -> None:
        """
        Getting long poll server
        :return: Nothing
        """
        self.LPS = self.vk_api.groups.getLongPollServer(
            group_id=self.group_id,
            v=self.api_version)  # getting server

    def send_requsest(self, ts):
        """
        sending requests to long poll server and getting updates
        :param ts: send id
        :return:
        """
        link = f'{self.LPS["server"]}?act=a_ch' \
               f'eck&key={self.LPS["key"]}&ts={ts}&wait=25'  # setting link
        res = requests.post(link).json()  # response
        if 'failed' in res.keys():
            if res['failed'] in (3, 4, 2):  # errors
                self.get_server()
                return None
        return res

    def run(self):
        """
        getting updates from long poll serer and make message
        :return:
        """
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
        """
        parsing input message to dict.
        Available recursion for forward messages
        :param res: input message as json(dict)
        :return:
        """
        r_msg = ''
        r_userid = res['object']['message']['from_id']  # who send
        session = self.main_system.db_session.create_session()
        is_fwding = session.query(self.main_system.db_session.Settings).filter(
            (self.main_system.db_session.Settings.user_id == r_userid) & (
                    self.main_system.db_session.Settings.name == "enable_fwd")
        ).first()
        attachments = res['object']['message']['attachments'] if res[
            'object']['message']['attachments'] else []
        # if is_fwding is None and res['object']['message']['fwd_messages'] or\
        #         '-fwd' not in res['object']['message']['text'] or \
        #         not res['object']['message'][
        #             'fwd_messages']:  # for forward messages
        if (is_fwding is None or '-fwd' in res[
            'object'
        ]['message'][
            'text'
        ]) and res[
            'object'
        ]['message']['fwd_messages']:  # для вложенных сообщений
            r_msg = res['object']['message']['text'][
                    :res['object']['message']['text'].find('-fwd')]

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

            r_msg += res['object']['message']['text'][
                     res['object']['message']['text'].find('-fwd') + 4::]
        else:
            r_msg = res['object']['message']['text'].strip()
        r_date = res['object']['message']['date']  # date
        r_sendid = res['object']['message']['peer_id']  # from send
        r_ctype = 'vk'
        r_attachments = {'image': [], 'sound': [], 'doc': []}
        for attachment in attachments:  # attachments
            if attachment['type'] == 'photo':
                r_attachments['image'].append(
                    attachment['photo']['sizes'][-1]['url'])
            elif attachment['type'] == 'doc':
                if attachment['doc']['ext'] in {'wav', 'mp3', 'wave'}:
                    r_attachments['sound'].append(
                        (attachment['doc']['url'],
                         attachment['doc']['ext'].replace("wave", 'wav')))
                    # 0: link; 1: extension
            elif attachment['type'] == 'audio':
                r_attachments['sound'].append(
                    (attachment['audio']['url'], 'mp3'))
            elif attachment['type'] == 'audio_message':
                r_attachments['sound'].append(
                    (attachment['audio_message']['link_mp3'], 'mp3'))
        dbs = self.main_system.db_session
        session = dbs.create_session()
        set = session.query(dbs.Settings).filter(
            (dbs.Settings.user_id == r_sendid) & (
                    dbs.Settings.name == "active")).first()
        if set:
            if r_msg.find('end') != -1:  # exit from active commands
                if r_msg[:r_msg.find(
                        'end')] in self.main_system.defaut_command_symbols:
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

    def upload_doc(self, dir, from_id, type: "audio_message" or 'doc') -> str:
        """
        Upload document
        :param dir: update from..
        :param from_id: user/chat id to upload file
        :param type: document type
        :return: string to pull with return message
        """
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

    @staticmethod
    def make_keyboard(button_names: List[List[Tuple[str, str] or str]],
                      one_time=True):
        """
        making keyboard with buttons
        max allow 40 buttons: 6 in row;
        10 in col
        :param button_names: List of rows with buttons
        button: tuple of label(and send message) and color or only name
        :param one_time: save keyboard
        :return:
        """
        if button_names is None:
            return None
        res = dict()
        res['one_time'] = one_time
        buttons = []
        for rows in button_names:
            row = []
            for item in rows:
                if isinstance(item, tuple):
                    button = {
                        'action': {'type': 'text',
                                   'label': item[0]},
                        'color': item[1]
                    }
                else:
                    button = {
                        'action': {'type': 'text',
                                   'label': item},
                    }
                row.append(button)
            buttons.append(row)
        res['buttons'] = buttons
        return json.dumps(res)