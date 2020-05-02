from Core.core import *
from commands.stupidAI import parser


def sett(self, message, length):
    param = message.params[length]
    if param in {'True', '1', 'true', 'yes'}:
        self.ai_enabled = True
    elif param in {'False', '0', 'false', 'no'}:
        self.ai_enabled = False


def analyze(message):
    if message.cls.SETTINGS[message.sendid].ai_enabled:
        # try:
        if message.sendid in message.cls.ACTIVE_COMMANDS.keys():
            ans, stat = parser.parse2(parser.normalize_sent(message.msg))
            if stat == 'acpt':
                del message.cls.ACTIVE_COMMANDS[message.sendid]
                return ans
            else:
                return ans
        else:
            ans, stat = parser.parse2(parser.normalize_sent(message.msg))
            if stat == 'acpt':
                return ans
            elif stat == 'add':
                message.cls.ACTIVE_COMMANDS[message.sendid] = message.text
                return ans
            elif stat == 'invoke':
                return message.cls.invoke_command(message, ans)
        # except Exception as f:
        #     print('ERROR >>', f)


def main(activates: dict, global_commands: dict, passive: list, global_settings: dict):
    activates.update({'supid_ai': {'ai'}})
    name = 'stupid_ai'
    currenthelp = '!ai\nПопытка ответить на вопрос'
    random_talk = Command(name, currenthelp, analyze, 0, exit)
    global_commands[name] = random_talk
    global_settings.update({
        'stupid_ai': {
            'True': (sett, 0),
            'False': (sett, 0),
            '0': (sett, 0),
            '1': (sett, 1)
        }})
    passive[name] = analyze
