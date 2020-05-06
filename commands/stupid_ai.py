from Core.core import *
from commands.stupidAI import parser


def sett(params, system: ChatSystem, message):
    param = message.params[-1]
    print(param)
    if param:
        session = system.db_session.create_session()
        sett = session.query(
            system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == 'stupid_ai')).first()
        if param in {'False', '0', 'false', 'no'}:
            if not sett:
                session.add(system.db_session.Settings(
                    message.userid,
                    'stupid_ai',
                    'disable'
                ))
        elif param in {'True', '1', 'true', 'yes'}:
            if sett:
                session.delete(sett)
        elif param == 'current':
            return str(not bool(sett))
        session.commit()
        return "Success"
    else:
        return "Не хватает параметра. Возможные варианты: {True | False}"


def analyze(message):
    session = message.get_session()
    # system: ChatSystem = message.cls.main_system
    # session = system.db_session.create_session()
    enable = message.get_setting(session, 'stupid_ai')
    # enable = session.query(
    #         system.db_session.Settings).filter(
    #         (system.db_session.Settings.user_id == message.userid) &
    #         (system.db_session.Settings.name == 'stupid_ai')).first() is None
    print(enable)
    if enable:
        # try:
        active_command = message.get_setting(session, 'active')
        # active_command = session.query(system.db_session.Settings).filter(
        #     (system.db_session.Settings.user_id == message.userid) &
        #     (system.db_session.Settings.name == 'active')).first()
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
        # except Exception as f:
        #     print('ERROR >>', f)


def main():
    sets = {
        'enable_stupid_ai': {
            'True': (sett, 0),
            'False': (sett, 0),
            '0': (sett, 0),
            '1': (sett, 1),
            'current': (sett, 0)
        }}
    return (
        "stupid_ai",
        "ai",
        analyze,
        "!ai Запрос\n"
        "Отвечает на заданный запрос. Можно спросить:"
        "\nНовости; реши {уравнение}; выбери {} или {}; выбери из",
        0,
        None,
        "Отвечает на заданный вопрос"
    ), (analyze, None, None), sets
