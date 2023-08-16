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
    User("@themaximkol", ["over", "drg"]),
    User("@smillims_0", ["over", "dota", "drg", "bg3"]),
    User("@maosttra", ["over", "drg"]),
    User("@KnowNoth1ng", ["over", "dota", "drg", "bg3"]),
    User("@emprerorr", ["over", "dota"]),
    User("@shidler_nm", ["over"]),
    User("@Doomfisting2004", ["over", "dota"]),
    User("@MedvedNikki", ["bg3"]),
    User("@nogarD4C", ["over", "dota"])
]

games = {
    "over": "Over",
    "dota": "Dota",
    "drg": "Deep Rock",
    "bg3": "Baldur's gate 3"
}

aliases = {
    "bg": "bg3",
    "baldur": "bg3",
    "rock": "drg",
    "DEEPROCKSEX": "drg",
    "DEEP_ROCK_SEX_YURA_GANDON": "drg",
    "sosat": "dota"
}


def get_game_players(game):
    return [user for user in users if user.has_role(game)]


def text(game, username, message):
    command_parts = message.text.split()[1:]
    if username != "themaximkol":
        return "о"

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
    response_text = text(real_command, username=message.from_user.username, message=message)

    game_players = get_game_players(real_command)
    mentioned_users = [str(user) for user in game_players if str(user) != "@" + message.from_user.username]

    if len(mentioned_users) > 5:
        first_response = response_text
        bot.reply_to(message, first_response)

        remaining_users = mentioned_users[5:]
        remaining_response = list_to_string(remaining_users)
        bot.send_message(message.chat.id, remaining_response)
    else:
        bot.reply_to(message, response_text)


# @bot.message_handler(commands=['krylo'])
# def handle_krylo_command(message):
# 	user_id = "160274125"
# 	bot.reply_to(message,
# 	             f'<a href="tg://user?id={user_id}">Крило</a> уєбан',
# 	             parse_mode='HTML')


# @bot.message_handler(commands=['test', 'a'])
# def handle_dota(message):
#     response = "Скажите пожалуйста, тегнул ли вас сейчас бот на это сообщение" + "\n\n" + "@themaximkol @themaximkol @themaximkol @themaximkol @themaximkol @themaximkol @Doomfisting2004 @nogarD4C"
#     bot.reply_to(message, response)


keep_alive()
bot.polling(non_stop=True, interval=0)
