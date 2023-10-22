import telebot
import random
import sqlite3 as sql
import emoji as emj
from datetime import datetime

from additional import token

bot = telebot.TeleBot(token)
print("RUNNING")


class User:
    def __init__(self, usr_id="000000000", username="@user", emoji=None):
        if emoji is None:
            self.emoji = ["😄"]
        else:
            self.emoji = emoji.split(",")

        self.id = usr_id
        self.username = username

    def __str__(self):
        return self.id

    def print_emoji(self):
        return random.choice(self.emoji)

    @staticmethod
    def get_usr_emoji(user_id):
        conn = sql.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
        row = cursor.fetchone()[0].split(",")

        cursor.close()
        conn.close()
        return row

    @staticmethod
    def add_usr_emoji(user_id, new_emoji):
        conn = sql.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE id=?", (user_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
            current_emojis = cursor.fetchone()[0]

            emojis_list = current_emojis.split(',')

            if new_emoji not in emojis_list:
                emojis_list.append(new_emoji)
                updated_emojis = ','.join(emojis_list)

                cursor.execute("UPDATE user SET emoji=? WHERE id=?", (updated_emojis, user_id))
                conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def remove_usr_emoji(user_id, emoji_to_remove):
        conn = sql.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE id=?", (user_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
            current_emojis = cursor.fetchone()[0]

            emojis_list = current_emojis.split(',')

            if emoji_to_remove in emojis_list:
                emojis_list.remove(emoji_to_remove)
                updated_emojis = ','.join(emojis_list)

                cursor.execute("UPDATE user SET emoji=? WHERE id=?", (updated_emojis, user_id))
                conn.commit()

        cursor.close()
        conn.close()


def load_games_aliases():
    conn = sql.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roles")
    rows = cursor.fetchall()
    games = {row[0]: row[1] for row in rows}

    cursor.execute("SELECT * FROM aliases")
    rows = cursor.fetchall()
    aliases = {row[0]: row[1] for row in rows}

    cursor.close()
    conn.close()

    return games, aliases


games, aliases = load_games_aliases()


def get_role_id(role_name, cursor):
    cursor.execute(
        "SELECT role_alias.role_id FROM aliases JOIN role_alias ON aliases.id = role_alias.alias_id WHERE "
        "aliases.alias = ?",
        (role_name,))
    role_id = cursor.fetchone()
    return role_id[0] if role_id else None


def text(game, message):
    command_parts = message.text.split()[1:]

    if not command_parts:
        response = f"{games[game]}" + "\n\n"

    else:
        response = " ".join(command_parts) + "\n\n"

    if response[0].islower():
        return response[0].upper() + response[1:]
    return response


@bot.message_handler(commands=list(aliases.values()))
def handle_game_command(message):
    conn = sql.connect('bot.db')
    cursor = conn.cursor()

    command_parts = message.text.split()
    command = command_parts[0][1:]
    real_command = aliases.get(command, command)

    role_id = get_role_id(real_command, cursor)

    cursor.execute(
        "SELECT id, username, emoji FROM user WHERE ? IN (SELECT role_id FROM user_roles WHERE user_id=user.id)",
        (role_id,))

    users_data = cursor.fetchall()

    users = [User(user_id, username, emoji) for user_id, username, emoji in users_data if
             user_id != str(message.from_user.id)]

    response_text = text(role_id, message=message)
    first_response = response_text + " ".join(
        [f'<a href="tg://user?id={user.id}">{user.print_emoji()}</a>' for user in users[:5]]
    )

    bot.reply_to(message, first_response, parse_mode='HTML')

    if len(users) > 5:
        second_response = "".join(
            [f'<a href="tg://user?id={user.id}">{user.print_emoji()}</a>ㅤ' for user in users[5:]]
        )

        if len(users[5:]) >= 2:
            second_response = second_response[:-1]

        bot.send_message(message.chat.id, second_response, parse_mode='HTML')

    cursor.close()
    conn.close()


@bot.message_handler(commands=['pack'])
def handle_pack_command(message):
    msg_url = "https://t.me/c/2037387850/2558"
    bot.reply_to(message, msg_url)


@bot.message_handler(commands=['emoji', 'my_emoji'])
def handle_my_emoji(message):
    conn = sql.connect('bot.db')
    cursor = conn.cursor()

    emojis = User.get_usr_emoji(message.from_user.id)

    response = "Emoji: \n\n" + ' '.join(emojis)

    bot.reply_to(message, response)
    cursor.close()
    conn.close()


@bot.message_handler(commands=['addemoji'])
def handle_add_emoji(message):
    conn = sql.connect('bot.db')
    cursor = conn.cursor()
    new_emj = str(message.text.split()[1])

    if len(new_emj) == 1 and emj.is_emoji(new_emj):
        User.add_usr_emoji(message.from_user.id, new_emj)
        reply = f"Emoji {new_emj} added"
    else:
        reply = "Нормально пиши"

    bot.reply_to(message, reply)
    cursor.close()
    conn.close()


@bot.message_handler(commands=['rmvemoji'])
def handle_rmv_emoji(message):
    conn = sql.connect('bot.db')
    cursor = conn.cursor()
    old_emj = str(message.text.split()[1])

    if len(old_emj) == 1 and emj.is_emoji(old_emj):
        User.remove_usr_emoji(message.from_user.id, old_emj)
        reply = f"Emoji {old_emj} removed"
    else:
        reply = "Нормально пиши"

    bot.reply_to(message, reply)
    cursor.close()
    conn.close()


# @bot.message_handler(commands=['all_birthdays'])
# def handle_all_birthdays(message):
#     conn = sql.connect('bot.db')
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT id, username, emoji FROM user")
#
#     users_data = cursor.fetchall()
#
#     users = [User(user_id, username, emoji) for user_id, username, emoji in users_data if
#              user_id]
#
#     sorted_users = sorted(users, key=lambda x: datetime.strptime(x.birthday, '%d-%m'))
#     birthday_list = [f"{user.username}: {user.birthday}" for user in sorted_users if user.birthday != "01-01"]
#     response = "\n".join(birthday_list)
#     bot.reply_to(message, response)
#
#     cursor.close()
#     conn.close()
#
# @bot.message_handler(commands=['next_birthdays'])
# def handle_next_birthdays(message):
#     today = datetime.today()
#     sorted_users = sorted(users, key=lambda x: datetime.strptime(x.birthday, '%d-%m'))
#     next_birthdays = []
#
#     for user in sorted_users:
#         if user.birthday != "01-01":
#             bday = datetime.strptime(user.birthday, '%d-%m').replace(year=today.year)
#             if bday < today:
#                 bday = bday.replace(year=today.year + 1)
#             next_birthdays.append((user.username, bday))
#
#     next_birthdays = sorted(next_birthdays, key=lambda x: x[1])
#     next_birthdays = next_birthdays[:4]
#
#     response = "\n".join([f"{name}: {date.strftime('%d-%m')}" for name, date in next_birthdays])
#     bot.reply_to(message, response)
#
#
# @bot.message_handler(commands=['role', 'my_role', 'roles', 'my_roles'])
# def handle_my_roles(message):
#     usr_id = str(message.from_user.id)
#     user = next((u for u in users if u.id == usr_id), None)
#
#     roles = user.print_my_roles()
#     response = "Roles: \n\n" + '  '.join(roles)
#
#     bot.reply_to(message, response)


@bot.message_handler(commands=['bot', 'BOT', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def handle_max_command(message):
    link = "https://t.me/c/2037387850/2556"
    bot.reply_to(message, link)


# bot.send_message("-1001973817859", "🍺")  # test
bot.polling(non_stop=True, interval=0)
