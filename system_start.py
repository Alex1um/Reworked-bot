import argparse
import sys
import json
from Core.core import ChatSystem
from chats import vk_chat, command_promt

chat_classes = {'VK': vk_chat.VK, 'command_promt': command_promt.SimpleChat}

parser = argparse.ArgumentParser()
parser.add_argument('runed_file', type=str)
parser.add_argument('json_file', type=str)
parser.add_argument(
    '-db_param',
    default=None,
    type=str,
    choices={'full', 'command', None},
    required=False
)
args = parser.parse_args(sys.argv)
if not args:
    args = parser.parse_args(input())
with open(f'./cfg/{args.json_file}', 'r') as f:
    params = json.load(f)
print('Creating system...')
chat_system = ChatSystem(**params['ChatSystem'])
print('Creating chats...')
for type, chats in params['Chats'].items():
    for chat in chats:
        print(chat)
        chat_classes[type](**chat, main_system=chat_system).start()
        print(f'Chat {type} created!')
print('Done')