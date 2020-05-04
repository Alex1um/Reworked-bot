from Core.core import ChatSystem


def dothis(message):
    system: ChatSystem = message.cls.main_system
    session = system.db_session.create_session()
    params = message.msg.split()
    if len(params) > 1:
        cmd = system.getcommand(params[1])
        if cmd:
            mreturn = cmd.help
        else:
            mreturn = 'No command'
    else:
        mreturn = '\n'.join(
            map(
                lambda x: f"{x[0]} - {x[1].name}", enumerate(
                    session.query(system.db_session.CommandTable))))
    return mreturn


def main():
    return ("help",  # name
            "help",  # keywords
            dothis,  # callable function
            '!help {Название команды}\nПолучить помощь по команде',  # help
            0,  # permission level
            None  # special symbol
            ), None, None  # additional functions and settings

