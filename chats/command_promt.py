from Core.core import Chat, Message, ChatSystem
import datetime


class SimpleChat(Chat):
    """
    Chat from input
    """

    def __init__(self, main_system=ChatSystem):
        super().__init__(main_system)

    def run(self):
        """
        Just make message from input()
        :return:
        """
        msgid = 0
        while True:
            msg = input()
            if msg:
                Message('io', msgid, msg, self).start()
                msgid += 1

    def send(self, res, id, rid, attachment=None, keyboard=None):
        """
        print returned text
        :param res: command return text
        :param id: message id
        :param rid: send id
        :param attachment: attachments but not working there
        :param keyboard: Chat keyboard if available
        :return:
        """
        if not isinstance(res, (tuple, list)):
            res = [res]
        for text in res:
            print(text)

    def message_parse(self, res):
        """
        Parsing input message
        :param res: input text
        :return: Dict:
        'msg': full message without edit
        'date': message date
        'sendid' send to
        'type': chat type
        'attachments': attachments
        'userid': from user
        """
        r_msg = ''
        r_msg = res
        r_date = datetime.datetime.now()
        r_sendid = 1
        r_ctype = 'io'
        r_attachments = {'image': [], 'sound': [], 'doc': []}
        r_userid = 0

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

    def make_keyboard(self, *args, **kwargs):
        return None