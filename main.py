import telebot
import random
from datetime import datetime

from additional import token


class User:
    def __init__(self, usr_id="000000000", username="@user", roles=None, birthday="01-01", emoji=None):
        if roles is None:
            roles = []
        if emoji is None:
            emoji = ["😄"]

        self.id = usr_id
        self.username = username
        self.roles = roles
        self.birthday = birthday
        self.emoji = emoji

    def has_role(self, role):
        return role in self.roles

    def __str__(self):
        return self.id

    def print_emoji(self):
        return random.choice(self.emoji)


bot = telebot.TeleBot(token)

print("RUNNING")

users = [
    User("335762220", "@themaximkol", ["tlou", "drg", "persona", "bcs", "bb", "cp", "cs", "yakuza"], "19-03",
         ["😎", "👨🏻‍💻"]),
    User("428717189", "@lukasobaka", ["tlou", "bb", "jojo", "re", "drg", "cp", "cs", "yakuza"], "22-11",
         ["🧅", "🏹", "💅"]),
    User("694949879", "@maosttra", ["over", "drg", "bleach", "persona", "bcs", "bb", "re", "tlou", "yakuza", "jojo"],
         "22-11", ["☠️"]),
    User("160274125", "@KnowNoth1ng",
         ["over", "dota", "drg", "bg3", "bleach", "persona", "kevin", "onepiece", "bcs", "bb", "jojo", "re", "cp",
          "cs", "tlou", "yakuza", "jjk", "emul"], "12-10", ["🤠", "👨‍🦰", "🦍", "🦧", "🦅"]),
    User("146943636", "@pink_wild_cherry", ["bleach", "onepiece", "bcs", "bb", "jojo", "jjk"], "05-05",
         ["🤭", "🪱", "🧍🏻‍♀️", "🛌", "🐁"]),
    User("744197313", "@shidler_nm", ["over", "bleach", "kevin", "onepiece", "jojo", "re", "yakuza", "jjk", "emul"],
         "24-09", ["👶", "🤓", "🤡", "💀", "😭"]),
    User("761982075", "@Doomfisting2004", ["over", "dota", "bleach", "onepiece", "bg3", "drg", "cs", "wh", "jojo"],
         "18-11",
         ["👨🏿", "🦂", "🦎"]),
    User("87600842", "@MedvedNikki", ["bg3", "kevin", "onepiece", "bb", "cp", "wh", "bleach", "jjk", "emul"], "18-03",
         ["👨‍🦳", "🐻", "🧸", "🔺"]),
    User("628793236", "@Pavlo_D_A", ["persona", "bb", "jojo", "yakuza", "wh", "emul"], "08-06", ["🍩", "🗿"]),
    User("552126018", "@TerribleRick132", ["bcs", "bb", "re", "tlou", "emul"], "14-05", ["🍆"]),
    User(username="@nogarD4C", roles=["over", "dota"], birthday="16-09", emoji=["🎮"]),
    User("539017344", "@smillims_0",
         ["tlou", "over", "dota", "drg", "bleach", "persona", "kevin", "onepiece", "bcs", "bb", "re", "cs", "jjk",
          "jojo"],
         "10-04", ["🚻", "🫦", "🥸", "😈", "👽", "👺", "👨‍💻", "🫥", "🥵"]
         ),
    User("741280840", "@emprerorr", ["over", "dota"], "13-03", ["🌬"]),
    User("287196610", "@plushabest", ["persona", "onepiece"], "12-06", ["🤓"]),
    User("306758056", "@phiIemon", ["persona"], "09-10", ["🪠"]),
    User(usr_id="628363051", username="@xtiwsu", birthday="06-06", emoji=["🧚‍♂"]),
    User(usr_id="599347025", username="@r6_raven", birthday="18-11", emoji=["🖐"]),
    User("377260960", "@limbonchik", ["cp"], "20-05", ["🥷"]),
]

games = {
    "over": "Over",
    "dota": "Dota",
    "drg": "Deep Rock",
    "bg3": "Baldur's gate 3",
    "bleach": "Bleach",
    "persona": "Persona",
    "kevin": "KEVIN",
    "onepiece": "One Piece",
    "bb": "Breaking Bad",
    "bcs": "Better Call Saul",
    "jojo": "Анімедібылы общий сбор",
    "re": "Resident Evil",
    "cp": "Cyberpunk 2077",
    "cs": "Counter Strike",
    "tlou": "Last of Us",
    "yakuza": "Yakuza",
    "wh": "Вахоёбы",
    "jjk": "Jujutsu Kaisen",
    "emul": "Ретроёбы"
}

aliases = {
    "bg": "bg3",
    "baldur": "bg3",
    "rock": "drg",
    "DEEPROCKSEX": "drg",
    "DEEP_ROCK_SEX_YURA_GANDON": "drg",
    "sosat": "dota",
    "aizen_solo": "bleach",
    "bleach_fans": "bleach",
    "p5": "persona",
    "persona5": "persona",
    "op": "onepiece",
    "gear5_hueta": "onepiece",
    "saul": "bcs",
    "jarejare": "jojo",
    "nigerundayo": "jojo",
    "жожоёбы": "jojo",
    "жожойоби": "jojo",
    "resik": "re",
    "cp77": "cp",
    "cyberpunk": "cp",
    "rgg": "yakuza",
    "waha": "wh",
    "emuli": "emul",
    "retro": "emul",
    "SegaMegadrive": "emul",
}


def text(game, message):
    command_parts = message.text.split()[1:]

    if not command_parts:
        response = f"{games[game]}" + "\n\n"
    else:
        response = " ".join(command_parts) + "\n\n"

    if response[0].islower():
        return response[0].upper() + response[1:]
    return response


@bot.message_handler(commands=list(games.keys()) + list(aliases.keys()))
def handle_game_command(message):
    command_parts = message.text.split()
    command = command_parts[0][1:]
    real_command = aliases.get(command, command)
    response_text = text(real_command, message=message)

    game_players = [user for user in users if user.has_role(real_command)]
    all_users = [user for user in game_players if user.id != str(message.from_user.id)]

    first_response = response_text + " ".join(  # space
        [f'<a href="tg://user?id={user.id}">{user.print_emoji()}</a>' for user in all_users[:5]])
    bot.reply_to(message, first_response, parse_mode='HTML')

    if len(all_users) > 5:
        second_response = "".join(  # empty char
            [f'<a href="tg://user?id={user.id}">{user.print_emoji()}</a>ㅤ' for user in all_users[5:]])
        bot.send_message(message.chat.id, second_response[:-1], parse_mode='HTML')


@bot.message_handler(commands=['pack'])
def handle_pack_command(message):
    msg_url = "https://t.me/c/1760116557/1012237"
    bot.reply_to(message, msg_url)


@bot.message_handler(commands=['all_birthdays'])
def handle_all_birthdays(message):
    sorted_users = sorted(users, key=lambda x: datetime.strptime(x.birthday, '%d-%m'))
    birthday_list = [f"{user.username}: {user.birthday}" for user in sorted_users if user.birthday != "01-01"]
    response = "\n".join(birthday_list)
    bot.reply_to(message, response)


@bot.message_handler(commands=['next_birthdays'])
def handle_next_birthdays(message):
    today = datetime.today()
    sorted_users = sorted(users, key=lambda x: datetime.strptime(x.birthday, '%d-%m'))
    next_birthdays = []

    for user in sorted_users:
        if user.birthday != "01-01":
            bday = datetime.strptime(user.birthday, '%d-%m').replace(year=today.year)
            if bday < today:
                bday = bday.replace(year=today.year + 1)
            next_birthdays.append((user.username, bday))

    next_birthdays = sorted(next_birthdays, key=lambda x: x[1])
    next_birthdays = next_birthdays[:4]

    response = "\n".join([f"{name}: {date.strftime('%d-%m')}" for name, date in next_birthdays])
    bot.reply_to(message, response)


@bot.message_handler(commands=['bot', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def handle_max_command(message):
    link = "https://t.me/c/1760116557/1043332"
    bot.reply_to(message, link)


# bot.send_message("-1001973817859", "🍺")  # test
bot.polling(non_stop=True, interval=0)
