from Core.core import *


def dothis(message):
    # try:
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    status = session.query(system.db_session.Settings).filter(
        (system.db_session.Settings.user_id == message.userid) & (
                system.db_session.Settings.name == "settings")).first()
    current_set = system.SETTINGS
    if status and not message.params:
        session.delete(status)
        status = None
        session.commit()
    new_bar = " "
    new = True
    if status:
        for n in status.value.split():
            new_bar += n + " "
            current_set = current_set[n]
        new = False
    params = message.params.copy()
    if params:
        while isinstance(current_set, dict) and\
                params and params[0] in current_set.keys():
            param = params.pop(0)
            current_set = current_set[param]
            new_bar += param + " "
    if isinstance(current_set, tuple):
        if message.user.level >= current_set[1]:
            # if not new:
            #     session.delete(status)
            #     session.commit()
            return current_set[0](params, system, message)
        else:
            return "Не хватает прав"
    else:
        if new_bar.strip():
            if new:
                session.add(system.db_session.Settings(message.userid,
                                                       "settings",
                                                       new_bar.strip()))
                session.commit()
            else:
                status.value = new_bar
                session.commit()
        return "!settings" + new_bar + ' ' + '{' + '|'.join(
            current_set.keys()) + '}'


def exitf(chat_system: ChatSystem):
    chat_system.db_session.create_session().commit()


def main():
    return ("settings",
            "set settings",
            dothis,
            'set | settings {предложанный вариант}\n'
            'Настройки\n'
            'После каждого ввода команды, вам предлагаются варианты. '
            'Для выбора варианта введите команд'
            'у и один из вариантов через пробел. '
            'Чтобы вернуться к первоначальному выбору настроек, '
            'введите команду set без параметров',
            0,
            None,
            "Настройки"), (None, exitf, None), None
