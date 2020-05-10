from Core.core import *
from commands.stupidAI import parser


def sett(params, system: ChatSystem, message):
    """
    Control work
    :param params:
    :param system:
    :param message:
    :return:
    """
    param = message.params[-1]
    print(param)
    if param:
        session = system.db_session.create_session()
        sett = session.query(
            system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == 'stupid_ai')).first()
        if param in {'False', '0', 'false', 'no'}:
            if sett:
                session.delete(sett)

        elif param in {'True', '1', 'true', 'yes'}:
            if not sett:
                session.add(system.db_session.Settings(
                    message.userid,
                    'stupid_ai',
                    'disable'
                ))
        elif param == 'current':
            return str(bool(sett))
        session.commit()
        return "Success"
    else:
        return "Не хватает параметра. Возможные варианты: {True | False}"


def analyze(message):
    """
    Use commands based on input sentence
    :param message:
    :return:
    """
    session = message.get_session()
    enable = message.get_setting(session, 'stupid_ai')
    print(enable)
    if enable:
        active_command = message.get_setting(session, 'active')
        if active_command:
            ans, stat = parser.parse2(parser.normalize_sent(message.msg))
            if stat == 'acpt':
                session.delete(active_command)
                return ans
            else:
                return ans
        else:
            ans, stat = parser.parse2(parser.normalize_sent(message.msg))
            if stat == 'acpt':
                return ans
            elif stat == 'add':
                active_command.value = message.text
                return ans
            elif stat == 'invoke':
                return message.cls.main_system.invoke_command(message, ans)


def main():
    sets = {
        'enable_stupid_ai': {
            'True': (sett, 0),
            'False': (sett, 0),
            'current': (sett, 0)
        }}
    return (
        "stupid_ai",
        "ai",
        analyze,
        "!ai Запрос\n"
        "Отвечает на заданный запрос. По умолчанию сканирует"
        " все входищие сообщения на наличие запроса.\n"
        "Можно отключить в настройках\n"
        "Можно спросить:"
        "\nНовости;\n"
        "выбери {} или {};\n"
        "Скажи что такое {название}",
        0,
        None,
        "Отвечает на заданный вопрос"
    ), (analyze, None, None), sets
