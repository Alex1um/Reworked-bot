def permissions(self, message, length):
    try:
        uid = message.params[length]
        ulevel = message.params[length + 1]
    except IndexError:
        uid = None
        ulevel = None
    otherid, level = int(uid) if uid != 'self' and uid.isdigit() else message.userid, int(
        ulevel) if ulevel.isdigit() else None
    if otherid in message.cls.SETTINGS.keys():
        if level is None:
            return message.cls.SETTINGS[otherid].level
        else:
            message.cls.SETTINGS[otherid].level = level
            return 'Success'
    return 'id not found'


def main(*args):
    args[3].update({'permissions': {
                'get': (permissions, 0),
                'set': (permissions, 8)}})