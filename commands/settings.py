from Core.core import *


def dothis(message):
    system: ChatSystem = message.cls.main_system
    session = message.get_session()
    status = message.get_setting(session, 'active')
    current_set = system.SETTINGS
    if 'Выход' in message.params:
        message.delete_active(session)
        return {'msg': 'Успешно!', 'keyboard': [[], False]}
    new_bar = " "
    # if status:
    #     for n in status.value.split()[1:]:
    #         new_bar += n + " "
    #         current_set = current_set[n]
    params = message.params.copy()
    if params:
        while isinstance(current_set, dict) and\
                params and params[0] in current_set.keys():
            param = params.pop(0)
            current_set = current_set[param]
            new_bar += param + " "
    if isinstance(current_set, tuple):
        if message.user.level >= current_set[1]:
            ans = current_set[0](params, system, message)
            if isinstance(ans, tuple) and isinstance(ans[1], bool):
                if not ans[1]:
                    if status:
                        status.value = message.sym + 'set' + new_bar
                        session.commit()
                    else:
                        message.add_setting(session,
                                            'active',
                                            'set' + new_bar.strip())
                    return new_bar + '\n' + ans[0]
                else:
                    message.delete_active(session)
                    return {'msg': ans[0], 'keyboard': [[]]}
            message.delete_active(session)
            return {'msg': ans, 'keyboard': [[]]}

        else:
            return "Не хватает прав"
    else:
        if status is None:
            message.add_setting(session, 'active', 'set' + new_bar.strip())
        elif new_bar.strip():
            status.value = message.sym + 'set' + new_bar
            session.commit()
        keys = list(current_set.keys())
        return {'msg': "!settings" + new_bar + ' ' + '{' + '|'.join(
            keys) + '}', 'keyboard': [
            [*[keys[i:i + 5] for i in range(0, len(keys), 5)],
             [('Выход', 'negative')]], False]}


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
