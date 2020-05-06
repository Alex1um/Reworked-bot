from Core.core import ChatSystem


def dothis(message):
    """
    Help function
    :param message: Message type
    :return: command help or list of commands with short help
    making query to sql to get all commands
    """
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    params = message.msg.split()
    if len(params) > 1:
        if params[1].isdigit():
            index = int(params[1])
            cmd = next(
                filter(
                    lambda x: x[0] == index, enumerate(
                        session.query(system.db_session.CommandTable))))[1]
        else:
            cmd = system.getcommand(params[1])
        if cmd:
            mreturn = cmd.help
        else:
            mreturn = 'Команда не найдена'
    else:
        mreturn = '\n'.join(
            map(
                lambda x: f"{x[0]} - {x[1].name}" + (
                    (" - " + x[1].short_help) if x[1].short_help else ""),
                enumerate(session.query(system.db_session.CommandTable))))
    return mreturn


def main():
    return ("help",  # name
            "help",  # keywords
            dothis,  # callable function
            'help {Название команды | номер команды}\n'
            'Получить помощь по команде\n'
            'Ввод help без команды выведет список команд',  # help
            0,  # permission level
            None,  # special symbol
            "Помощь по командам"  # short help
            ), None, None  # additional functions and settings

