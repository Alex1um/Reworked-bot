from Core.core import *


def dothis(message):
    try:
        system: ChatSystem = message.cls.main_system
        session = system.db_session.create_session()
        status = session.query(system.db_session.Settings).filter((system.db_session.Settings.user_id == message.userid) & (system.db_session.Settings.name == "active")).first()
        current_set = system.SETTINGS
        new_bar = ""
        if status:
            for n in status.split():
                current_set = current_set[n]
        params = message.params
        while isinstance(current_set, dict) and params[0] in current_set.keys():
            param = params.pop(0)
            current_set = current_set[param]
            new_bar += param + " "
        if isinstance(current_set, tuple):
            if message.user.level >= current_set[1]:
                status.delete()
                return current_set[0](params, system, message)
            else:
                return "Не хватает прав"
        else:
            status.value = new_bar
            return "!settings" + new_bar + ' ' + '{' + '|'.join(current_set.keys()) + '}'
    except Exception as f:
        return str(f)


def exitf(chat_system: ChatSystem):
    chat_system.db_session.create_session().commit()


def main():
    return ("settings", "set settings", dothis, '{!set|!settings} {module} {setting} {parameter} {name}\nНастройки', 0, None), (None, exitf), None
