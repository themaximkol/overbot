import telebot
import random
from additional import token
from models import Alias, Role, User, Donate, session
from errors import *

bot = telebot.TeleBot(token)
print("RUNNING")


def get_text(message):
    return " ".join(message.text.split()[1:]) if len(message.text.split()) > 1 else None


def responce_text(game, message):
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

    @bot.message_handler(commands=commands)
    def call_role(message):
        command_parts = message.text.split()
        command = command_parts[0][1:]

        user_ids = [user for user in Role.get_users_cmd(command) if
                    user != str(message.from_user.id)]
        role = Role.get_role_name(command)

        response = f"<b>{responce_text(role, message=message)}</b>"
        response += " ".join(
            [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>' for user_id in
             user_ids[:5]]
        )

        bot.reply_to(message, response, parse_mode='HTML')

        if len(user_ids) > 5:
            while len(user_ids) > 5:
                user_ids = user_ids[5:]
                second_response = "".join(
                    [f'<a href="tg://user?id={user_id}">{random.choice(User.get_emojis(user_id=user_id))}</a>ㅤ' for
                     user_id in user_ids]
                )

                if len(user_ids) >= 2:
                    second_response = second_response[:-1]

                bot.send_message(message.chat.id, second_response, parse_mode='HTML')


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
                         f"Role <b>{role}</b> added successfully for @<b>{message.from_user.username}</b>",
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
                         f"Role <b>{role}</b> removed successfully for @<b>{message.from_user.username}</b>",
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except EmptyInputError as e:
        bot.reply_to(message, str(e))
    except UserDoesntHaveRoleError as e:
        bot.reply_to(message, str(e))
    except (AliasNotFoundError, RoleNotFoundError) as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['emoji', 'viewemoji'])
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

    bot.reply_to(message, response, parse_mode='HTML')


@bot.message_handler(commands=['bot', 'pack', 'BOT', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def nicebot(message):
    link = f'<a href="https://t.me/c/2037387850/2556"><b>Bot Commands</b></a>  |  <a href="https://t.me/c/2037387850/2558"><b>Sticker Packs</b></a>'
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

        bot.send_message(message.chat.id, f'Alias <b>/{new_aliases}</b> was added to role <b>{role_alias_name}</b>',
                         parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)
        booter(Alias.get_all_aliases())

    except RoleNotFoundError as e:
        bot.reply_to(message, str(e))
    except AliasAlreadyExistsError as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['luka'])
def luka(message):
    record = session.query(Donate).filter(Donate.id == 1).first()
    if record.remain <= 0:
        bot.delete_message(message.chat.id, message.message_id)
        return

    user_id = "428717189"
    bot.reply_to(message, f'<a href="tg://user?id={user_id}">Лука</a> даун', parse_mode='HTML')
    record.remain -= 1
    session.commit()


@bot.message_handler(commands=['addluka'])
def add_luka(message):
    if message.from_user.id == 335762220:
        luka = session.query(Donate).filter(Donate.id == 1).first()

        luka.remain += 50
        session.commit()
        bot.send_message(message.chat.id, f'Лука вырос на 50. Баланс: {luka.remain}', parse_mode='HTML')

    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['checkluka'])
def view_luka(message):
    record = session.query(Donate).filter(Donate.id == 1).first()
    bot.reply_to(message, f'Баланс: {record.remain}', parse_mode='HTML')


@bot.message_handler(commands=['krylo'])
def krylo(message):
    # if message.from_user.id != 335762220:
    #     return
    user = session.query(User).filter(User.id == 160274125).first()

    try:
        user.add_role("kevin")
        bot.send_message(message.chat.id, f"<b>Блудный КРИЛО вернулся</b>", parse_mode='HTML')
        bot.delete_message(message.chat.id, message.message_id)

    except UserAlreadyHasRoleError:
        bot.reply_to(message, f"<b>КРИЛО уже вернулся</b>", parse_mode='HTML')


if __name__ == "__main__":
    booter()
    bot.polling(non_stop=True, interval=0)
