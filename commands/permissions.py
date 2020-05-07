from Core.core import ChatSystem


def permissions(params, system: ChatSystem, message):
    '''
    Add permission control
    :param params: param[0] - other id; param[1](option) - level
    :param system: ChatSystem obj
    :param message: Message obj
    :return:
    '''
    if params:
        otherid = int(
            params[0]) if params[0] != 'self' and params[
            0].isdigit() else message.userid
        other = system.db_session.create_session().query(
            system.db_session.User).filter(
            system.db_session.User.id == message.userid).first()
        if other:
            if len(params) > 1 and params[1].isdigit():
                other.level = int(params[1])
                return "Success"
            else:
                return str(other.level)
        else:
            return "Неправильный id", False
    return "Не хватает параметров. Необходимые параметры: {id}" \
           " или self; число", False


def main():
    return None, None, {
        'permissions': {'get': (permissions, 0), 'set': (permissions, 8)}}
