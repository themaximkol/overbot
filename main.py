import telebot
from background import keep_alive
from background import token_main, token_test


class User:

    def __init__(self, username, roles=[]):
        self.username = username
        self.roles = roles

    def has_role(self, role):
        return role in self.roles

    def __str__(self):
        return self.username


# bot = telebot.TeleBot(token_main)  # OverBot
bot = telebot.TeleBot(token_test)  # TestBot
print("RUNNING")

users = [
    User("@themaximkol", ["drg", "persona", "bcs", "bb"]),
    User("@lukasobaka", ["bb", "jojo"]),
    User("@maosttra", ["over", "drg", "bleach", "persona", "bcs", "bb"]),
    User("@KnowNoth1ng", ["over", "dota", "drg", "bg3", "bleach", "persona", "kevin", "onepiece", "bcs", "bb", "jojo"]),
    User("@pink_wild_cherry", ["bleach", "onepiece", "bcs", "bb", "jojo"]),
    User("@shidler_nm", ["over", "bleach", "kevin", "onepiece", "jojo"]),
    User("@Doomfisting2004", ["over", "dota", "bleach", "onepiece"]),
    User("@MedvedNikki", ["bg3", "kevin", "onepiece", "bb"]),
    User("@nogarD4C", ["over", "dota"]),
    User("@smillims_0", ["over", "dota", "drg", "bg3", "bleach", "persona", "kevin", "onepiece", "bcs", "bb"]),
    User("@emprerorr", ["over", "dota"]),
    User("@plushabest", ["persona"]),
    User("@Pavlo_D_A", ["persona", "bb", "jojo"]),
    User("@TerribleRick132", ["bcs", "bb"])
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
}


def get_game_players(game):
    return [user for user in users if user.has_role(game)]


def text(game, username, message):
    command_parts = message.text.split()[1:]
    # if username != "themaximkol":
    # return ""

    if not command_parts:
        response = f"{games[game]}"

        game_players = get_game_players(game)
        mentioned_users = [str(user) for user in game_players if str(user) != "@" + username][:5]
        response += "\n\n" + list_to_string(mentioned_users)

    else:
        response = list_to_string(command_parts)
        game_players = get_game_players(game)
        mentioned_users = [str(user) for user in game_players if str(user) != "@" + username][:5]
        response += "\n\n" + list_to_string(mentioned_users)

    if response[0].islower():
        response = response[0].upper() + response[1:]

    return response


def list_to_string(input_list):
    return " ".join(input_list)


def get_command(game):
    return aliases.get(game, game)


@bot.message_handler(commands=list(games.keys()) + list(aliases.keys()))
def handle_game_command(message):
    command_parts = message.text.split()
    command = command_parts[0][1:]
    real_command = get_command(command)
    response_text = text(real_command,
                         username=message.from_user.username,
                         message=message)

    game_players = get_game_players(real_command)
    mentioned_users = [
        str(user) for user in game_players
        if str(user) != "@" + message.from_user.username
    ]

    if len(mentioned_users) > 5:
        first_response = response_text
        bot.reply_to(message, first_response)

        remaining_users = mentioned_users[5:]
        remaining_response = list_to_string(remaining_users)
        bot.send_message(message.chat.id, remaining_response)
    else:
        bot.reply_to(message, response_text)


@bot.message_handler(commands=['pack'])
def handle_pack_command(message):
    msg_url = "https://t.me/c/1760116557/1012237"
    bot.reply_to(message, msg_url)


@bot.message_handler(commands=['money', "manonsha"])
def handle_manon_command(message):
    user_id = "146943636"
    bot.reply_to(message, f'<a href="tg://user?id={user_id}">Манонша</a> дай деняк (693 грн)', parse_mode='HTML')


@bot.message_handler(commands=["davidka"])
def handle_davidka_command(message):
    user_id = "761982075"
    bot.reply_to(message, f'<a href="tg://user?id={user_id}">Давидка</a>', parse_mode='HTML')


@bot.message_handler(commands=['krylo'])
def handle_krylo_command(message):
    user_id = "160274125"
    bot.reply_to(message, f'<a href="tg://user?id={user_id}">Крило</a> уєбан', parse_mode='HTML')


keep_alive()
bot.polling(non_stop=True, interval=0)
