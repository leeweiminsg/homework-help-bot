#Refer to echobot2: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
import logging

import telegram

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logging.basicConfig(format=f'{asctime}s - {name}s - {levelname}s - {message}s',
#                     level=logging.INFO)

token = '837770119:AAEmP97SuF0moJezC0jipSHz5Uy-CXqNNoI'

def main():
    print('Program started!')
    bot = telegram.Bot(token=token)
    print(f'Bot is created! Bot details: {bot.get_me()}')

if __name__ == '__main__':
    main()