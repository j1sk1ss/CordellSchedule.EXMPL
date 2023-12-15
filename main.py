#######################
#   IMPORT SECTION

from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import TeleBot, types
from Scripts.ScheduleParser import Parser, PairType
from Objects.User import Users, User
from prettytable import PrettyTable as prettyTable

#   IMPORT SECTION
#######################

# Configuration Constants
BOT_TOKEN = input('Type bot token: ')
SCHEDULE_URL = "http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group=13889&mode=full"

# Initialize bot and scheduler
bot = TeleBot(BOT_TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Berlin")

# Initialize Users
users = Users.load_object()
current_user = User(0)


# Daily message contains data of all pair in this day
#  ____________________________
# | PAIR | AUDIT | TYPE | TIME |
#
def send_daily_message():
    users.save_object()
    for user in users.users:
        schedule = get_schedule()
        if not user.every_day_review:
            return

        tb = prettyTable()
        tb.field_names = ["Pair", "Type", "Time", "Audit", "Missed"]

        current_day = schedule.get_current_day()

        if current_day is None:
            send_message('No study today', user.chat_id)
            current_day = schedule.find_near_day()[0]

        for pair in current_day.pairs:
            tb.add_row([str(pair.name[:10]), str(pair.type), str(pair.time)[:5], str(pair.audit),
                        user.pairs_missed.get(pair.name, 0)])

        send_table(tb, user.chat_id)


# Pre pair attention sends to user before pair (For ex. 5 minutes before pair start)
#  ____________________________
# | PAIR | AUDIT | TYPE | TIME |
# | I GO   |          | I MISS |
#
# With choose type of message where user choose
def send_pre_pair_attention():
    for user in users.users:
        if user.is_attention is False:
            continue

        schedule = get_schedule()
        current_day = schedule.get_current_day()
        if current_day is None:
            continue

        pair, duration = current_day.find_near_pair()
        if pair is None:
            continue

        if duration.seconds // 60 == user.attention:
            if user.is_answer:
                user.pairs_missed[user.pair.name] = user.pairs_missed.get(user.pair.name, 0) + 1
                user.is_answer = False

            send_message(f'Before pair attention {user.attention} min', user.chat_id)

            tb = prettyTable()
            tb.field_names = ["Pair", "Type", "Time", "Audit", "Missed"]

            missed = user.pairs_missed.get(pair.name, 0)
            tb.add_row([str(pair.name), str(pair.type), str(pair.time)[:5], str(pair.audit), missed])

            send_table(tb, user.chat_id)
            send_buttons(f'Did u go to this pair?', ['Yes, i go', 'No, i don`t go'], user.chat_id)
            user.is_answer = True
            user.pair = pair


# Get schedule of all pairs
def get_schedule():
    parser = Parser(SCHEDULE_URL, PairType().get_all())
    return parser.parse()


############################
# Task of attentions part

scheduler.add_job(send_daily_message, trigger="cron", hour=23)
scheduler.add_job(send_pre_pair_attention, 'cron', day_of_week='mon-fri', hour='0-23', minute='5-59/1',
                  timezone='America/Chicago')


def schedule_checker():
    while True:
        scheduler.start()


Thread(target=schedule_checker).start()

# Task of attentions part
############################


@bot.message_handler(commands=['start'])
def start(message):
    send_buttons('Start setup', ['Start setup', 'Setup end'], message.chat.id)
    user = User(message.chat.id)
    if users.get_user(user.chat_id) is not None:
        return None

    users.add_user(user)
    users.save_object()


@bot.message_handler()
def get_message(message):
    global current_user
    current_user = users.get_user(message.chat.id)
    if current_user is None:
        return

    bot.delete_message(message.chat.id, message.message_id)
    if current_user.is_setting_attention:
        current_user.attention = int(message.text)
        current_user.is_attention = current_user.attention != 0
        current_user.is_setting_attention = False
        send_buttons('Select setting', ['Attention time', 'Every day review', 'Setup end'], message.chat.id)
        return


@bot.callback_query_handler(func=lambda call: True)
def answer(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)

    global current_user
    current_user = users.get_user(message.message.chat.id)
    if current_user is None:
        return

    if message.data == 'Setup end':
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.message.chat.id)
        return

    #######################
    # All pairs showing

    if message.data == 'All pairs':
        send_buttons('Choose pair type', ['All any', 'All lection', 'All laboratory', 'All practice'],
                     message.message.chat.id)
        return

    if message.data in ['All any', 'All lection', 'All laboratory', 'All practice']:
        pair_type = {
            'All any': PairType().get_all,
            'All lection': PairType().get_lections,
            'All laboratory': PairType().get_labs,
            'All practice': PairType().get_practice
        }.get(message.data)()

        days = Parser(SCHEDULE_URL, pair_type).parse()
        day = days.get_current_day()
        if day is None:
            day = days.find_near_day()[0]

        day_index = days.find_day_index(day.date)
        text = f'Current [{day.date}]:\n'
        tb = prettyTable()
        tb.field_names = ["Pair", "Type", "Time", "Audit", "Missed"]

        for i in range(day_index, min(day_index + 6, len(days.days))):
            for pair in days.days[i].pairs:
                tb.add_row([str(pair.name[:10]), str(pair.type), str(pair.time)[:5], str(pair.audit),
                            current_user.pairs_missed.get(pair.name, 0)])

            text += '{}\n```\n{}```\n'.format(days.days[i].date, tb.get_string())
            tb.clear_rows()

        bot.send_message(message.message.chat.id, text, parse_mode='Markdown')
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.message.chat.id)
        return

    # All pairs showing
    #######################

    ###################
    # Next pair showing

    if message.data == 'Next pair':
        send_buttons('Choose pair type', ['Any', 'Lection', 'Laboratory', 'Practice'], message.message.chat.id)
        return

    if message.data in ['Any', 'Lection', 'Laboratory', 'Practice']:
        pair_type = {
            'Any': PairType().get_all,
            'Lection': PairType().get_lections,
            'Laboratory': PairType().get_labs,
            'Practice': PairType().get_practice
        }.get(message.data)()

        days = Parser(SCHEDULE_URL, pair_type).parse()
        pair = days.get_current_day().get_next_pair()

        tb = prettyTable()
        tb.field_names = ["Pair", "Type", "Time", "Audit", "Missed"]
        missed = current_user.pairs_missed.get(pair.name, 0)

        tb.add_row([str(pair.name[:10]), str(pair.type), str(pair.time)[:5], str(pair.audit), missed])

        send_table(tb, message.message.chat.id)
        send_buttons('Choose operation', ['All pairs', 'Next pair'], message.message.chat.id)
        return

    # Next pair showing
    ###################

    if message.data in ['Yes, i go', 'No, i don`t go'] and current_user.is_answer:
        if message.data == 'Yes, i go':
            current_user.pairs_missed[
                current_user.pair.name] = 0 if current_user.pair.name not in current_user.pairs_missed else \
                current_user.pairs_missed[current_user.pair.name] - 1
        else:
            current_user.pairs_missed[current_user.pair.name] = current_user.pairs_missed.get(current_user.pair.name,
                                                                                              0) + 1

    if message.data == 'Start setup':
        send_buttons('Select setting', ['Attention time', 'Every day review', 'Setup end'], message.message.chat.id)
        return

    if message.data == 'Attention time':
        send_message('Write count of minutes (0 - attentions turn off)', message.message.chat.id)
        current_user.is_setting_attention = True
        return

    if message.data == 'Every day review':
        send_buttons('Send all day pair in 2:00:00 every day?', ['Yes', 'No'], message.message.chat.id)
        current_user.is_setting_review = True
        return

    if current_user.is_setting_review:
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
