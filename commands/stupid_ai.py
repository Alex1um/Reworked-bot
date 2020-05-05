from Core.core import *
from commands.stupidAI import parser


def sett(params, system: ChatSystem, message):
    if params:
        session = system.db_session.create_session()
        sett = session.query(
            system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == 'stupid_ai')).first()
        if params[0] in {'True', '1', 'true', 'yes'}:
            if not sett:
                session.add(system.db_session.Settings(
                    message.userid,
                    'stupid_ai',
                    'False'
                ))
        elif params[0] in {'False', '0', 'false', 'no'}:
            if sett:
                session.delete(sett)
        session.commit()
        return "Success"
    else:
        return "Не хватает параметра. Возможные варианты: {True | False}"


def analyze(message):
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    if session.query(
            system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == 'stupid_ai')).first() is None:
        # try:
        active_command = session.query(system.db_session.Settings).filter(
            (system.db_session.Settings.user_id == message.userid) &
            (system.db_session.Settings.name == 'active')).first()
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
        'stupid_ai': {
            'True': (sett, 0),
            'False': (sett, 0),
            '0': (sett, 0),
            '1': (sett, 1)
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
