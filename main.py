import telebot
import random
import emoji as emj

from datetime import datetime
from additional import token, with_cursor, games, aliases

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

    # ---------------------------------------------
    @staticmethod
    @with_cursor
    def get_my_roles(cursor, user_id):
        cursor.execute("SELECT roles.name FROM roles JOIN user_roles ON roles.id = user_roles.role_id "
                       "WHERE user_roles.user_id=?", (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    @staticmethod
    @with_cursor
    def remove_user_role(cursor, user_id, command):
        # Find the alias_id
        cursor.execute("SELECT id FROM aliases WHERE alias=?", (command,))
        alias_id = cursor.fetchone()
        if not alias_id:
            return False

        # Find the role_id
        cursor.execute("SELECT role_id FROM role_alias WHERE alias_id=?", (alias_id[0],))
        role_id = cursor.fetchone()
        if not role_id:
            return False

        # Remove the role
        cursor.execute("DELETE FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id[0]))
        return True

    @staticmethod
    @with_cursor
    def add_user_role(cursor, user_id, command):
        # Find the alias_id
        cursor.execute("SELECT id FROM aliases WHERE alias=?", (command,))
        alias_id = cursor.fetchone()
        if not alias_id:
            return False

        # Find the role_id
        cursor.execute("SELECT role_id FROM role_alias WHERE alias_id=?", (alias_id[0],))
        role_id = cursor.fetchone()
        if not role_id:
            return False

        # Check if the user already has this role
        cursor.execute("SELECT * FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id[0]))
        existing_entry = cursor.fetchone()
        if existing_entry:
            return False

        # Add the role to the user
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id[0]))
        return True

    @staticmethod
    @with_cursor
    def get_user_roles_by_username(cursor, username):
        # Step 1: Check if the user with the given username exists
        cursor.execute("SELECT id FROM user WHERE username=?", (username,))
        user_id = cursor.fetchone()

        if not user_id:
            return None  # User with the provided username doesn't exist

        user_id = user_id[0]  # Extracting the user ID from the result

        # Step 2: Retrieve roles associated with the user
        cursor.execute("SELECT roles.name FROM roles "
                       "JOIN user_roles ON roles.id = user_roles.role_id "
                       "WHERE user_roles.user_id=?", (user_id,))

        rows = cursor.fetchall()
        return [row[0] for row in rows]  # Return a list of roles

    # ---------------------------------------------
    def print_emoji(self):
        return random.choice(self.emoji)

    @staticmethod
    @with_cursor
    def get_usr_emoji(cursor, user_id):

        cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
        row = cursor.fetchone()[0].split(",")

        return row

    @staticmethod
    @with_cursor
    def add_usr_emoji(cursor, user_id, new_emoji):

        cursor.execute("SELECT id FROM user WHERE id=?", (user_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
            current_emojis = cursor.fetchone()[0]

            emojis_list = current_emojis.split(',')
            if len(emojis_list) < 10:
                if new_emoji not in emojis_list:
                    emojis_list.append(new_emoji)
                    updated_emojis = ','.join(emojis_list)

                    cursor.execute("UPDATE user SET emoji=? WHERE id=?", (updated_emojis, user_id))
                    return True
            return False
        return False

    @staticmethod
    @with_cursor
    def remove_usr_emoji(cursor, user_id, emoji_to_remove):

        cursor.execute("SELECT id FROM user WHERE id=?", (user_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.execute("SELECT emoji FROM user WHERE id=?", (user_id,))
            current_emojis = cursor.fetchone()[0]

            emojis_list = current_emojis.split(',')
            print(emojis_list)
            print(len(emojis_list))
            if emoji_to_remove in emojis_list:
                emojis_list.remove(emoji_to_remove)
                updated_emojis = ','.join(emojis_list)

                cursor.execute("UPDATE user SET emoji=? WHERE id=?", (updated_emojis, user_id))
                return True
        return False

    @staticmethod
    @with_cursor
    def get_random_users(cursor):
        cursor.execute("SELECT id FROM user ORDER BY RANDOM() LIMIT 4")
        users_data = cursor.fetchall()
        return users_data


def get_role_id(role_name, cursor):
    cursor.execute(
        "SELECT role_alias.role_id FROM aliases JOIN role_alias ON aliases.id = role_alias.alias_id WHERE "
        "aliases.alias = ?",
        (role_name,))
    role_id = cursor.fetchone()
    return role_id[0] if role_id else None


def get_text(message):
    return message.text.split()[1:] if len(message.text.split()) > 1 else None


def text(game, message):
    command_parts = get_text(message)

    if not command_parts:
        response = f"{games[game]}" + "\n\n"
    else:
        response = " ".join(command_parts) + "\n\n"

    if response[0].islower():
        return response[0].upper() + response[1:]
    return response


@bot.message_handler(commands=list(aliases.values()))
@with_cursor
def handle_game_command(cursor, message):
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


# ---------------------------------------------
@bot.message_handler(commands=['emoji', 'my_emoji'])
def handle_my_emoji(message):
    emojis = User.get_usr_emoji(message.from_user.id)
    response = "Emoji: \n\n" + ' '.join(emojis)

    bot.reply_to(message, response)


@bot.message_handler(commands=['addemoji'])
def handle_add_emoji(message):
    new_emj = str(message.text.split()[1])

    if len(new_emj) == 1 and emj.is_emoji(new_emj) and User.add_usr_emoji(message.from_user.id, new_emj):
        reply = f"Emoji {new_emj} added"
    else:
        reply = "Нормально пиши"

    bot.reply_to(message, reply)


@bot.message_handler(commands=['rmvemoji'])
def handle_rmv_emoji(message):
    old_emj = str(message.text.split()[1])

    if len(old_emj) == 1 and emj.is_emoji(old_emj) and User.remove_usr_emoji(message.from_user.id, old_emj):
        reply = f"Emoji {old_emj} removed"
    else:
        reply = "Нормально пиши"

    bot.reply_to(message, reply)


# ---------------------------------------------
@bot.message_handler(commands=['role', 'roles', 'my_roles', 'my_role'])
def handle_usr_roles(message):
    reply = " - ".join(User.get_my_roles(message.from_user.id))
    bot.reply_to(message, reply)


@bot.message_handler(commands=['rmvrole'])
def handle_rmv_roles(message):
    success = User.remove_user_role(message.from_user.id, get_text(message)[0])
    if success:
        reply = "Role removed"
    else:
        reply = "Role removal failed"
    bot.reply_to(message, reply)


@bot.message_handler(commands=['addrole'])
def handle_add_roles(message):
    success = User.add_user_role(message.from_user.id, get_text(message)[0])
    if success:
        reply = "Role added"
    else:
        reply = "Role addition failed"
    bot.reply_to(message, reply)


@bot.message_handler(commands=['viewrole'])
def handle_view_roles(message):
    username = get_text(message)

    if username is None:
        bot.reply_to(message, "Пиши нормально")
        return

    roles = User.get_user_roles_by_username(username[0])

    if roles is None:
        bot.reply_to(message, "Пиши нормально")
    else:
        bot.reply_to(message, str(username[0]) + ": " + " - ".join(roles))


@bot.message_handler(commands=['baka'])
def handle_baka(message):
    random_users = [user_id for user_id, in User.get_random_users()]
    
    response = "Ви наче шарите\n\n" + " ".join(
        [f'<a href="tg://user?id={user}">{random.choice(User.get_usr_emoji(user))}</a>' for user in random_users[:5]]
    )

    bot.reply_to(message, response, parse_mode='HTML')


# ---------------------------------------------

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


@bot.message_handler(commands=['pack'])
def handle_pack_command(message):
    msg_url = "https://t.me/c/2037387850/2558"
    bot.reply_to(message, msg_url)


@bot.message_handler(commands=['bot', 'BOT', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def handle_max_command(message):
    link = "https://t.me/c/2037387850/2556"
    bot.reply_to(message, link)


# bot.send_message("-1001973817859", "🍺")  # test
bot.polling(non_stop=True, interval=0)
