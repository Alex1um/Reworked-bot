from Core.core import ChatSystem


def permissions(params, system: ChatSystem, message):
    try:
        uid = params[0]
        ulevel = params[1]
    except IndexError:
        uid = None
        ulevel = None
    otherid, level = int(uid) if uid != 'self' and uid.isdigit() else message.userid, int(
        ulevel) if ulevel.isdigit() else None
    other = system.db_session.create_session().query(system.db_session.User).get(otherid)
    if other:
        if level is None:
            return other.level
        else:
            other.level = level
            return 'Success'
    return 'id not found'


def main():
    return None, None, {'permissions': {'get': (permissions, 0), 'set': (permissions, 8)}}