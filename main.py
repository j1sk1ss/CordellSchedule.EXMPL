from threading import Thread

import telebot
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import types

from Scripts.ScheduleParser import Parser, PairType
from Objects.User import Users, User

from prettytable import PrettyTable as prettyTable


print('Type bot token: ')
bot = telebot.TeleBot(input())
scheduler = BlockingScheduler(timezone="Europe/Berlin")

users = Users([])
current_user = User(0)


def send_daily_message():
    for user in users.users:
        if user.every_day_review is False:
            continue

        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        tb = prettyTable()

        tb.field_names = ["Pair", "Type", "Time", "Audit"]
        day = days.get_current_day()
        if day is None:
            send_message('No study today', user.chat_id)
            day = days.find_near_day()

        for pair in day.pairs:
            tb.add_row([str(pair.name), str(pair.type), str(pair.time)[:5], str(pair.audit)])

        send_table(tb, user.chat_id)


def attention():
    for user in users.users:
        if user.is_attention is False:
            continue

        parser = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                        PairType().get_all())
        days = parser.parse()
        pair, duration = days.get_current_day().find_near_pair()
        if pair is None:
            return None

        if duration.seconds // 60 <= current_user.attention:
            send_message(f'Before pair attention {user.attention} min', user.chat_id)

            tb = prettyTable()
            tb.field_names = ["Pair", "Type", "Time", "Audit"]
            tb.add_row([str(pair.name), str(pair.type), str(pair.time)[:5], str(pair.audit)])
            send_table(tb, user.chat_id)


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
        return

    bot.delete_message(message.chat.id, message.message_id)
    if current_user.is_setting_attention is True:
        current_user.attention = int(message.text)
        current_user.is_attention = current_user.attention != 0
        current_user.is_setting_attention = False
        send_buttons('Start setup', ['Start setup', 'Setup end'], message.chat.id)
        return


@bot.callback_query_handler(func=lambda call: True)
def answer(message):
    global current_user
    current_user = users.get_user(message.message.chat.id)
    if current_user is None:
        return

    bot.delete_message(message.message.chat.id, message.message.message_id)
    if message.data == 'Setup end':
        send_buttons('Choose operation', ['All pairs',
                                          'Next pair'], message.message.chat.id)
        return

    if message.data == 'All pairs':
        days = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full",
                      PairType().get_all()).parse()
        tb = prettyTable()

        tb.field_names = ["Pair", "Type", "Time", "Audit"]
        day = days.get_current_day()
        if day is None:
            send_message('No study today', message.message.chat.id)
            day = days.find_near_day()

        for pair in day.pairs:
            tb.add_row([str(pair.name), str(pair.type), str(pair.time)[:5], str(pair.audit)])

        send_table(tb, message.message.chat.id)
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.message.chat.id)
        return

    ###################
    # Next pair showing

    if message.data == 'Next pair':
        send_buttons('Choose pair type', ['Any', 'Lection', 'Laboratory', 'Practice'], message.message.chat.id)
        return

    if message.data in ['Any', 'Lection', 'Laboratory', 'Practice']:
        pair_type = PairType().get_practice()
        if message.data == 'Any':
            pair_type = PairType().get_all()
        elif message.data == 'Lection':
            pair_type = PairType().get_lections()
        elif message.data == 'Laboratory':
            pair_type = PairType().get_labs()

        days = Parser("http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full", pair_type).parse()
        pair = days.get_current_day().get_next_pair()

        tb = prettyTable()
        tb.field_names = ["Pair", "Type", "Time", "Audit"]
        tb.add_row([str(pair.name), str(pair.type), str(pair.time)[:5], str(pair.audit)])

        send_table(tb, message.message.chat.id)
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.message.chat.id)
        return

    # Next pair showing
    ###################

    if message.data == 'Start setup':
        send_buttons('Select setting', ['Attention time', 'Every day review'], message.message.chat.id)
        return

    if message.data == 'Attention time':
        send_message('Write count of minutes (0 - attentions turn off)', message.message.chat.id)
        current_user.is_setting_attention = True
        return

    if message.data == 'Every day review':
        send_buttons('Send all day pair in 2:00:00 every day?', ['Yes', 'No'], message.message.chat.id)
        current_user.is_setting_review = True
        return

    if current_user.is_setting_review is True:
        current_user.every_day_review = message.data == 'Yes'
        current_user.is_setting_review = False
        send_buttons('Start setup', ['Start setup', 'Setup end'], message.message.chat.id)
        return


def send_message(text, chat_id):
    bot.send_message(chat_id, text=text)


def send_table(table, chat_id):
    response = '```\n{}```'.format(table.get_string())
    bot.send_message(chat_id, response, parse_mode='Markdown')


def send_buttons(text, buttons, chat_id):
    markup = types.InlineKeyboardMarkup()
    for i in buttons:
        markup.add(types.InlineKeyboardButton(i, callback_data=i))

    bot.send_message(chat_id, text=text, reply_markup=markup)


def send_button(text, button, chat_id):
    markup = types.InlineKeyboardMarkup()
    parse = types.InlineKeyboardButton(button, callback_data=button)
    markup.add(parse)

    bot.send_message(chat_id, text=text, reply_markup=markup)


bot.polling(none_stop=True)
