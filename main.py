import telebot
import random
import emoji as emj
from additional import token
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

engine = create_engine('sqlite:///bot.db')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
bot = telebot.TeleBot(token)
print("RUNNING")


class RoleAlias(Base):
    __tablename__ = 'role_alias'
    id = Column(Integer, primary_key=True)
    alias_id = Column(Integer, ForeignKey('aliases.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))


class Alias(Base):
    __tablename__ = 'aliases'
    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True)

    @classmethod
    def get_all_aliases(cls):
        aliases = session.query(Alias).all()
        return [alias.alias for alias in aliases]


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship('User', secondary='user_roles', back_populates='roles')

    @classmethod
    def get_users_cmd(cls, alias_name, usr_id):
        alias = session.query(Alias).filter(Alias.alias == alias_name).first()
        if alias:
            role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
            if role:
                return [user.id for user in role.users]
        return []

    @classmethod
    def get_role_name(cls, alias_name):
        alias = session.query(Alias).filter(Alias.alias == alias_name).first()
        if alias:
            role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
            return role.name if role else None


class UserRole(Base):
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))


class UserEmoji(Base):
    __tablename__ = 'user_emojis'
    id = Column(Integer, primary_key=True)
    emoji = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='emojis')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    roles = relationship('Role', secondary='user_roles',
                         primaryjoin='User.id == user_roles.c.user_id',
                         secondaryjoin='Role.id == user_roles.c.role_id',
                         back_populates='users')

    emojis = relationship('UserEmoji', back_populates='user')

    def add_role(self, alias_name):
        if self.id in Role.get_users_cmd(alias_name, self.id): return False
        alias = session.query(Alias).filter(Alias.alias == alias_name).first()
        if alias:
            role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
            if role:
                self.roles.append(role)
                session.commit()
                return True
        return False

    def remove_role(self, alias_name):
        if self.id not in Role.get_users_cmd(alias_name, self.id): return False
        alias = session.query(Alias).filter(Alias.alias == alias_name).first()
        if alias:
            role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
            if role:
                self.roles.remove(role)
                session.commit()
                return True
        return False

    def get_roles(self):
        return [role.name for role in self.roles]

    @staticmethod
    def get_roles_usrn(username):
        user = session.query(User).filter_by(username=username).first()
        if user:
            return [role.name for role in user.roles]
        else:
            return []

    # ---------------------------------------------
    def get_emojis(self):
        return [emoji.emoji for emoji in self.emojis]

    def add_emoji(self, emoji):
        if not emj.is_emoji(emoji): return False
        if len(self.emojis) < 10 and emoji not in [e.emoji for e in self.emojis]:
            new_emoji = UserEmoji(emoji=emoji)
            self.emojis.append(new_emoji)
            session.commit()
            return True
        return False

    def remove_emoji(self, emoji):
        if not emj.is_emoji(emoji): return False
        for e in self.emojis:
            if e.emoji == emoji:
                self.emojis.remove(e)
                session.commit()
                return True
        return False

    @staticmethod
    def get_emojis_usrn(username):
        user = session.query(User).filter(User.username == username).first()
        if user:
            return [emoji.emoji for emoji in user.emojis]
        else:
            return []

    @staticmethod
    def get_emojis_id(usr_id):
        user = session.query(User).filter(User.id == usr_id).first()
        if user:
            return [emoji.emoji for emoji in user.emojis]
        else:
            return []


def get_text(message):
    return message.text.split()[1:] if len(message.text.split()) > 1 else None


def text(game, message):
    command_parts = get_text(message)

    if not command_parts:

        response = game + "\n\n"
    else:
        response = " ".join(command_parts) + "\n\n"

    if response[0].islower():
        return response[0].upper() + response[1:]
    return response


@bot.message_handler(commands=Alias.get_all_aliases())
def handle_game_command(message):
    command_parts = message.text.split()
    command = command_parts[0][1:]

    users = [user for user in Role.get_users_cmd(command, message.from_user.id) if user != str(message.from_user.id)]
    role = Role.get_role_name(command)

    response = text(role, message=message)

    response += " ".join(
        [f'<a href="tg://user?id={user}">{random.choice(User.get_emojis_id(user))}</a>' for user in
         users[:5]]
    )

    bot.reply_to(message, response, parse_mode='HTML')

    if len(users) > 5:
        while len(users) > 5:
            users = users[5:]
            second_response = "".join(
                [f'<a href="tg://user?id={user}">{random.choice(User.get_emojis_id(user))}</a>ㅤ' for user in
                 users]
            )

            if len(users) >= 2:
                second_response = second_response[:-1]

            bot.send_message(message.chat.id, second_response, parse_mode='HTML')


@bot.message_handler(commands=['role', 'roles', 'my_roles', 'my_role'])
def handle_usr_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    reply = " - ".join(user.get_roles())
    bot.reply_to(message, reply)


@bot.message_handler(commands=['rmvrole'])
def handle_rmv_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    role = get_text(message)[0]
    print(role)
    if user.remove_role(role):
        bot.reply_to(message, "REMOVED")
    else:
        bot.reply_to(message, "Пиши нормально")


@bot.message_handler(commands=['addrole'])
def handle_add_roles(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    role = get_text(message)[0]
    if user.add_role(role):
        bot.reply_to(message, "ADDED")
    else:
        bot.reply_to(message, "Пиши нормально")


@bot.message_handler(commands=['viewrole'])
def handle_view_roles(message):
    username = get_text(message)

    if username is None:
        bot.reply_to(message, "Пиши нормально")
        return

    roles = User.get_roles_usrn(username[0])

    if roles is None:
        bot.reply_to(message, "Пиши нормально")
    else:
        bot.reply_to(message, str(username[0]) + ": " + " - ".join(roles))


@bot.message_handler(commands=['emoji', 'my_emoji', 'emojis', 'my_emojis'])
def handle_my_emoji(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    response = "Emoji: \n\n" + " ".join(user.get_emojis())

    bot.reply_to(message, response)


@bot.message_handler(commands=['addemoji'])
def handle_add_emoji(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    new_emj = str(message.text.split()[1])
    if user.add_emoji(new_emj):
        bot.reply_to(message, "ADDED")
    else:
        bot.reply_to(message, "Пиши нормально")


@bot.message_handler(commands=['rmvemoji'])
def handle_rmv_emoji(message):
    user = session.query(User).filter(User.id == message.from_user.id).first()
    old_emj = str(message.text.split()[1])
    if user.remove_emoji(old_emj):
        bot.reply_to(message, "REMOVED")
    else:
        bot.reply_to(message, "Пиши нормально")


@bot.message_handler(commands=['viewemoji', 'viewemojis'])
def handle_view_emojis(message):
    username = get_text(message)

    if username is None:
        bot.reply_to(message, "Пиши нормально")
        return

    roles = User.get_emojis_usrn(username[0])

    if roles is None:
        bot.reply_to(message, "Пиши нормально")
    else:
        bot.reply_to(message, str(username[0]) + ": " + " ".join(roles))


@bot.message_handler(commands=['baka'])
def handle_baka(message):
    random_users = [user_id for user_id, in User.get_random_users()]

    response = "Ви наче шарите\n\n" + " ".join(
        [f'<a href="tg://user?id={user}">{random.choice(User.get_usr_emoji(user))}</a>' for user in random_users[:5]]
    )

    bot.reply_to(message, response, parse_mode='HTML')


@bot.message_handler(commands=['pack'])
def handle_pack_command(message):
    msg_url = "https://t.me/c/2037387850/2558"
    bot.reply_to(message, msg_url)


@bot.message_handler(commands=['bot', 'BOT', 'nicebotmax', 'nicebot', 'NICEBOTMAX', 'NICEBOT'])
def handle_max_command(message):
    link = "https://t.me/c/2037387850/2556"
    bot.reply_to(message, link)


bot.polling(non_stop=True, interval=0)
