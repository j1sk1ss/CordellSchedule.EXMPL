from threading import Thread

import telebot
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import types

from ScheduleParser import Parser, PairType
from User import Users, User

print('Type bot token: ')
bot = telebot.TeleBot('5511006797:AAHGTKMP7cULEQKIuTRCH9QPclBxCZv6tTE')
scheduler = BlockingScheduler(timezone="Europe/Berlin")

users = Users([])
current_user = User(0)


def send_daily_message():
    for user in users.users:
        if not user.every_day_review:
            continue

        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        text = ''
        for pair in days.get_current_day().pairs:
            text += f'Pair: {pair.name}, Time: {pair.time}, Audit: {pair.audit}\n'

        send_message(text, user.chat.id)


def attention():
    for user in users.users:
        if user.is_attention is False:
            continue

        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        pair, duration = days.get_current_day().find_near_pair()

        if duration.seconds // 3600 <= current_user.attention:
            send_message(f'Near next pair: {pair.name}, Time: {pair.time}, Audit: {pair.audit}', user.chat_id)


scheduler.add_job(send_daily_message, trigger="cron", hour=23)
scheduler.add_job(attention, 'cron', day_of_week='mon-fri', hour='12-16', minute='5-59/1', timezone='America/Chicago')


def schedule_checker():
    while True:
        scheduler.start()


Thread(target=schedule_checker).start()


@bot.message_handler(commands=['start'])
def start(message):
    send_buttons('Start setup', ['Start setup', 'Setup end'], message.chat.id)
    user = User(message.chat.id)
    if users.get_user(user.chat_id) is not None:
        return None

    users.add_user(user)


@bot.message_handler()
def get_message(message):
    global current_user
    current_user = users.get_user(message.chat.id)
    if current_user is None:
        return None

    if current_user.is_setting_attention is True:
        current_user.attention = int(message.text)
        if current_user.attention == 0:
            current_user.is_attention = False
        else:
            current_user.is_attention = True

        current_user.is_setting_attention = False
        send_buttons('Start setup', ['Start setup', 'Setup end'], message.chat.id)
        return None

    if current_user.is_setting_review is True:
        current_user.every_day_review = message.text == '1'
        current_user.is_setting_review = False
        send_buttons('Start setup', ['Start setup', 'Setup end'], message.chat.id)
        return None

    if message.text == 'Setup end':
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.chat.id)
        return None

    if message.text == 'All pairs':
        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        text = ''
        for pair in days.get_current_day().pairs:
            text += f'Pair: {pair.name}, Time: {pair.time}, Audit: {pair.audit}\n'

        send_message(text, message.chat.id)
        return None

    if message.text == 'Next pair':
        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        pair = days.get_current_day().get_next_pair()
        send_message(f'Next pair: {pair.name}, Time: {pair.time}, Audit: {pair.audit}\n', message.chat.id)
        return None

    if message.text == 'Start setup':
        send_buttons('Select setting', ['Attention time', 'Every day review'], message.chat.id)
        return None

    if message.text == 'Attention time':
        send_message('Write count of minutes (0 - attentions turn off)', message.chat.id)
        current_user.is_setting_attention = True
        return None

    if message.text == 'Every day review':
        send_message('Send all day pair in 2:00:00 every day? (1/0)', message.chat.id)
        current_user.is_setting_review = True
        return None


def send_message(text, chat_id):
    bot.send_message(chat_id, text=text)


def send_buttons(text, buttons, chat_id):
    buttons_list = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in buttons:
        buttons_list.append(types.KeyboardButton(i))
        markup.add(buttons_list[-1])

    bot.send_message(chat_id, text=text, reply_markup=markup)


def send_button(text, button, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    parse = types.KeyboardButton(button)
    markup.add(parse)

    bot.send_message(chat_id, text=text, reply_markup=markup)


bot.polling(none_stop=True)
