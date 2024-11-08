import telebot
import random
from additional import token, select_random_file
from models import Alias, Role, User, Donate, RoleAlias, session, UserRole, UserEmoji
from errors import *
from datetime import datetime

bot = telebot.TeleBot(token)
print("RUNNING")


def get_command(message) -> str:
    return message.text.split()[0][1:]


def get_text(message) -> str:
    return " ".join(message.text.split()[1:]) if len(message.text.split()) > 1 else None


def responce_text(game, message) -> str:
    command_parts = get_text(message)

    if not command_parts:
        response = game + "\n\n"
    else:
        response = command_parts + "\n\n"

    if response[0].islower():
        return response[0].upper() + response[1:]
    return response


def booter(commands=None):
    if commands is None:
        commands = Alias.get_all_aliases()

    @bot.message_handler(commands=commands + ['over', 'persona'])
    def call_role(message):
        command_parts = message.text.split()
        command = command_parts[0][1:]

        user_ids = [user for user in Role.get_users_cmd(command) if
                    user != str(message.from_user.id)]
        # for user in user_ids:
        #     try:
        #         bot.get_chat_member(message.chat.id, int(user))
        #
        #     except telebot.apihelper.ApiException:
        #         user_ids.remove(user)

        role = Role.get_role_name(command)

        response = f"<b>{responce_text(role, message=message)}</b>"
        response += " ".join(
            [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>' for user_id in
             user_ids[:5]]
        )
        if message.reply_to_message:
            bot.reply_to(message.reply_to_message, response, parse_mode='HTML')
        else:
            bot.reply_to(message, response, parse_mode='HTML')

        i = 0
        if len(user_ids) > 5:
            while len(user_ids) > 5:
                if i + 5 >= len(user_ids):
                    break
                users = user_ids[i + 5:min(i + 10, len(user_ids))]
                print(users, len(users))

                second_response = "".join(
                    [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>ㅤ' for
                     user_id in users]
                )

                if len(users) >= 2:
                    second_response = second_response[:-1]

                bot.send_message(message.chat.id, second_response, parse_mode='HTML')
                i += 5


@bot.message_handler(commands=['role', 'viewrole'])
def get_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    username = get_text(message)
    try:
        if username is None:
            username = user.username
            roles = user.get_roles()
        else:
            roles = user.get_roles(username=username)

        bot.send_message(message.chat.id, f'<b>{username}</b>: {" - ".join(roles)}', parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except UserDoesntHaveRoleError as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['addrole'])
def add_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    role = get_text(message)

    try:
        user.add_role(role)
        bot.send_message(message.chat.id,
                         f"Role <b>{Role.get_role_name(message.text.split()[1])}</b> added successfully for @<b>{message.from_user.username}</b>",
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except EmptyInputError as e:
        bot.reply_to(message, str(e))
    except UserAlreadyHasRoleError as e:
        bot.reply_to(message, str(e))
    except (AliasNotFoundError, RoleNotFoundError) as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['rmvrole'])
def rmv_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    role = get_text(message)

    try:
        user.remove_role(role)
        bot.send_message(message.chat.id,
                         f"Role <b>{Role.get_role_name(message.text.split()[1])}</b> removed successfully for @<b>{message.from_user.username}</b>",
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except EmptyInputError as e:
        bot.reply_to(message, str(e))
    except UserDoesntHaveRoleError as e:
        bot.reply_to(message, str(e))
    except (AliasNotFoundError, RoleNotFoundError) as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['emoji', 'viewemoji', 'уьщош'])
def handle_my_emoji(message):
    username = get_text(message)

    if username is None:
        emojis = User.get_emojis(user_id=message.from_user.id)
        username = "@" + message.from_user.username
    else:
        emojis = User.get_emojis(username=username)

    if emojis is None:
        bot.reply_to(message, "No emojis avaible")
    else:
        bot.send_message(message.chat.id,
                         f'<b>{username}</b>: {" ".join([f"<code>{emoji}</code>" for emoji in emojis])}',
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['addemoji'])
def handle_add_emoji(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    new_emj = get_text(message)

    try:
        user.add_emoji(new_emj)
        bot.reply_to(message, f"Emoji {new_emj} added")

    except (SymbolIsntEmojiError, EmojiLimitReachedError, EmojiAlreadyTakenError, UserAlreadyHasEmojiError) as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['rmvemoji'])
def rmv_emoji(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    old_emj = get_text(message)

    try:
        user.remove_emoji(old_emj)
        bot.send_message(message.chat.id, f"Emoji {old_emj} removed for @<b>{message.from_user.username}</b>",
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except (SymbolIsntEmojiError, UserDoesntHaveEmojiError) as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['baka'])
def baka(message):
    random_users = random.sample(
        [user.id for user in session.query(User).all() if user.id != str(message.from_user.id)],
        4)

    response = "<b>Ви наче шарите</b>\n\n" + " ".join(
        [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>' for user_id in
         random_users])

    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, response, parse_mode='HTML')
    else:
        bot.reply_to(message, response, parse_mode='HTML')


@bot.message_handler(
    commands=['bot', 'pack', 'donate', 'donat', 'BOT', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def nicebot(message):
    link = f'<a href="https://t.me/c/2037387850/324036"><b>Donate</b></a>  |  <a href="https://t.me/c/2037387850/2556"><b>Bot Commands</b></a>  |  <a href="https://t.me/c/2037387850/2558"><b>Sticker Packs</b></a>'
    bot.reply_to(message, link, parse_mode='HTML')


@bot.message_handler(commands=['crtrole', 'c'])
def crt_role(message):
    if message.from_user.id != 335762220:
        return

    params = get_text(message).split("-")

    name = params[0]
    aliases = params[1].split()

    try:
        Role.create_new_role(role_name=name, alias_name=aliases)

        bot.send_message(message.chat.id, f'Role <b>{name}</b> was created with aliases <b>/{" /".join(aliases)}</b>',
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)
        booter(Alias.get_all_aliases())

    except RoleAlreadyExistsError as e:
        bot.reply_to(message, str(e))
    except AliasAlreadyExistsError as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['addalias', 'a'])
def add_alias(message):
    if message.from_user.id != 335762220:
        return

    params = get_text(message).split("-")
    role_alias_name = params[0]
    new_aliases = params[1].strip()

    try:
        Alias.create_alias(new_aliases, role_alias_name)
        role = session.query(Role).join(RoleAlias).join(Alias).filter(Alias.alias == role_alias_name).first()

        bot.send_message(message.chat.id, f'Alias <b>/{new_aliases}</b> was added to role <b>{role.name}</b>',
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)
        booter(Alias.get_all_aliases())

    except RoleNotFoundError as e:
        bot.reply_to(message, str(e))
    except AliasAlreadyExistsError as e:
        bot.reply_to(message, str(e))


def krylo() -> None:
    user = session.query(User).filter(User.id == "160274125").first()
    try:
        user.add_role("kevin")
        session.commit()
    except UserAlreadyHasRoleError:
        pass

    try:
        user.remove_role("tlou")
        session.commit()
    except  UserDoesntHaveRoleError:
        pass


@bot.message_handler(
    commands=[value for result in session.query(Donate.name).all() for value in result[0].split(', ') if
              value != 'all'])
def points(message):
    name = get_command(message)
    if name == "krylo":
        krylo()

    for record_name in session.query(Donate.name).all():
        if name in record_name[0].split(', '):
            name = record_name[0]

    record = session.query(Donate).filter(Donate.name == name).first()

    if record.remain <= 0:
        bot.delete_message(message.chat.id, message.message_id)
        return

    answer = f'<a href="tg://user?id={record.id}">{record.tag_name}</a> {random.choice(record.reply.split("*"))}'

    if record.media and (record.cnt > record.cooldown):
        name = name.split(', ')[0]
        random_file = select_random_file(f'botphoto/{name}')
        if random_file[-3:] == "mp4":
            bot.send_animation(message.chat.id, open(random_file, "rb"), caption=answer, parse_mode='HTML')
            record.cnt = 0
        else:
            bot.send_photo(message.chat.id, open(random_file, "rb"), caption=answer, parse_mode='HTML')
            record.cnt = 0
    else:
        bot.reply_to(message, answer, parse_mode='HTML')
        record.cnt += 1

    record.remain -= 1
    session.commit()


@bot.message_handler(commands=['add'])
def manage_points(message):
    text = get_text(message).split()
    name = text[0]

    for record_name in session.query(Donate.name).all():
        if name in record_name[0].split(', '):
            name = record_name[0]

    if user := session.query(Donate).filter(Donate.name == name).first():
        if message.from_user.id == 335762220:  # check if admin:
            amount = int(text[1])
            user.remain += amount
            session.commit()
            bot.send_message(message.chat.id, f'<b>{user.tag_name} плюс {amount}. Баланс: {user.remain}</b>',
                             parse_mode='HTML')
            bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['check'])
def manage_points(message):
    a = session.query(Donate.tag_name, Donate.remain).all()
    balance = ""
    for user in a:
        balance += f"{user[0].split(', ')[0]}: {user[1]}\n"

    bot.reply_to(message, balance, parse_mode='HTML')


@bot.message_handler(commands=['register'])
def register(message):
    try:
        User.crt_user(username=message.from_user.username, user_id=message.from_user.id)
        bot.reply_to(message, "<b>Done!</b>", parse_mode='HTML')
    except UserAlreadyExists:
        bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['next_birthdays'])
def next_birthdays(message):
    all_users = session.query(User).all()
    today = datetime.now()
    next_bd = []

    for user in all_users:
        if user.birthday is None:
            continue

        b_day, b_month = map(int, user.birthday.split('-'))
        next_birthday = datetime(year=today.year, month=b_month, day=b_day)

        if next_birthday < today:
            next_birthday = datetime(year=today.year + 1, month=b_month, day=b_day)

        next_bd.append((user, next_birthday))

    next_bd.sort(key=lambda x: x[1])

    output = "<b>Next Birthdays:</b> \n\n" + "\n".join(
        [f"{user.username} - {birthday.strftime('%d-%m')}" for user, birthday in next_bd[:4]])

    bot.send_message(message.chat.id, output, parse_mode='HTML')


@bot.message_handler(commands=['all_birthdays'])
def all_birthdays(message):
    all_users = session.query(User).all()
    all_bd = []

    for user in all_users:
        if user.birthday is not None:
            b_day, b_month = map(int, user.birthday.split('-'))
            birthday_date = datetime(year=1, month=b_month, day=b_day)  # Year doesn't matter for sorting
            all_bd.append((user, birthday_date))

    all_bd.sort(key=lambda x: x[1])
    all_bd = [(user, date.strftime('%d-%m')) for user, date in all_bd]

    output = "<b>All Birthdays:</b> \n\n" + "\n".join([f"{user.username} - {birthday}" for user, birthday in all_bd])

    bot.send_message(message.chat.id, output, parse_mode='HTML')


@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, "🤨")


@bot.message_handler(commands=['all'])
def all_users(message):
    record = session.query(Donate).filter(Donate.name == 'all').first()

    if record.remain <= 0:
        bot.delete_message(message.chat.id, message.message_id)
        return

    user_ids = [user.id for user in session.query(User).all()]

    response = "All users: \n\n" + " ".join(
        [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>' for user_id in
         user_ids[:5]]
    )
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, response, parse_mode='HTML')
    else:
        bot.reply_to(message, response, parse_mode='HTML')

    i = 0
    if len(user_ids) > 5:
        while len(user_ids) > 5:
            if i + 5 >= len(user_ids):
                break
            users = user_ids[i + 5:min(i + 10, len(user_ids))]
            print(users, len(users))

            second_response = "".join(
                [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>ㅤ' for
                 user_id in users]
            )

            if len(users) >= 2:
                second_response = second_response[:-1]

            bot.send_message(message.chat.id, second_response, parse_mode='HTML')
            i += 5
    # bot.send_message(message.chat.id, output, parse_mode='HTML')
    record.remain -= 1
    session.commit()


from sqlalchemy import and_


@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    user_id = "552126018"

    user = session.query(User).filter(User.id == user_id).first()

    if user:

        session.delete(user)

        tables = [UserRole, UserEmoji]
        for table in tables:
            records = session.query(table).filter(table.user_id == user_id).all()

            for record in records:
                session.delete(record)

        session.commit()

        bot.reply_to(message, "<b>User and related records deleted!</b>", parse_mode='HTML')
    else:
        bot.reply_to(message, "<b>User not found!</b>", parse_mode='HTML')


if __name__ == "__main__":
    booter()
    bot.polling(non_stop=True, interval=0)
