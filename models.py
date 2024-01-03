import random
import emoji as emj
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from errors import *

engine = create_engine('sqlite:///bot.db')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


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

    @classmethod
    def create_alias(cls, alias_name, role_alias_name):

        if session.query(Alias).filter(Alias.alias == alias_name).first():
            raise AliasAlreadyExistsError("Alias with this name already exists")

        alias = Alias(alias=alias_name)

        role = session.query(Role).join(RoleAlias).join(Alias).filter(Alias.alias == role_alias_name).first()
        if not role:
            raise RoleNotFoundError("Role not found")

        session.add(alias)
        session.commit()

        role_alias = RoleAlias(alias_id=alias.id, role_id=role.id)
        session.add(role_alias)
        session.commit()


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship('User', secondary='user_roles', back_populates='roles')

    @classmethod
    def get_users_cmd(cls, alias_name):
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

    @classmethod
    def create_new_role(cls, role_name, alias_name):
        if not role_name or not alias_name:
            print("Role name and alias name are required.")
            return

        existing_role = session.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            raise RoleAlreadyExistsError("Role with this name already exists")

        for alias in alias_name:
            existing_alias = session.query(Alias).filter(Alias.alias == alias).first()
            if existing_alias:
                raise AliasAlreadyExistsError("Alias with this name already exists")

        new_role = Role(name=role_name)
        session.add(new_role)
        session.commit()

        for alias in alias_name:
            new_alias = Alias(alias=alias)
            session.add(new_alias)
            session.commit()

            role_alias = RoleAlias(role_id=new_role.id, alias_id=new_alias.id)
            session.add(role_alias)
            session.commit()

        session.commit()


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

    def get_roles(self, username=None):
        if username is not None:
            user = session.query(User).filter_by(username=username).first()
        else:
            user = session.query(User).filter_by(id=self.id).first()

        if not user:
            raise UserDoesntHaveRoleError("No roles found")

        return [role.name for role in user.roles]

    def add_role(self, alias_name):
        if not alias_name:
            raise EmptyInputError("Empty input")

        if self.id in Role.get_users_cmd(alias_name):
            raise UserAlreadyHasRoleError("You already have this role")

        alias = session.query(Alias).filter(Alias.alias == alias_name).first()

        if not alias:
            raise AliasNotFoundError("Command not found")

        role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
        if not role:
            raise RoleNotFoundError("Role not found")

        self.roles.append(role)
        session.commit()

    def remove_role(self, alias_name):
        if not alias_name:
            raise EmptyInputError("Empty input")

        if self.id not in Role.get_users_cmd(alias_name):
            raise UserDoesntHaveRoleError("You don't have this role")

        alias = session.query(Alias).filter(Alias.alias == alias_name).first()
        if not alias:
            raise AliasNotFoundError("Command not found")

        role = session.query(Role).join(RoleAlias).filter(RoleAlias.alias_id == alias.id).first()
        if not role:
            raise RoleNotFoundError("Role not found")

        self.roles.remove(role)
        session.commit()

    @staticmethod
    def get_emojis(username=None, user_id=None):
        if username is not None:
            user = session.query(User).filter_by(username=username).first()
        elif user_id is not None:
            user = session.query(User).filter_by(id=user_id).first()

        if user:
            return [emoji.emoji for emoji in user.emojis]
        else:
            return None

    def add_emoji(self, emoji):
        if not emj.is_emoji(emoji):
            raise SymbolIsntEmojiError("Пиши нормально")

        if emoji in [e.emoji for e in self.emojis]:
            raise UserAlreadyHasEmojiError("Ти шо поц? Баяни - бан")

        if session.query(UserEmoji).filter(UserEmoji.emoji == emoji).first():
            raise EmojiAlreadyTakenError("Хтось спиздів це емодзі")

        if len(self.emojis) >= 10:
            raise EmojiLimitReachedError("Не розганяйся, ліміт 10")

        new_emoji = UserEmoji(emoji=emoji)
        self.emojis.append(new_emoji)
        session.commit()

    def remove_emoji(self, emoji):
        if not emj.is_emoji(emoji):
            raise SymbolIsntEmojiError("Пиши нормально")

        if emoji not in [e.emoji for e in self.emojis]:
            raise UserDoesntHaveEmojiError("Ти шо поц? Спочатку додай")

        emoji_record = None
        for e in self.emojis:
            if e.emoji == emoji:
                emoji_record = e
                break

        if emoji_record is not None:
            self.emojis.remove(emoji_record)
            session.delete(emoji_record)
            session.commit()
            return True

    @classmethod
    def crt_user(cls, username, user_id):

        existing_user = session.query(User).filter(User.id == user_id).first()
        if existing_user:
            raise UserAlreadyExists

        new_user = User(id=user_id, username="@" + username)
        session.add(new_user)
        session.commit()

        new_user_emoji = UserEmoji(user_id=new_user.id, emoji=random.choice(["😀", "😃", "😄", "😁", "😅", "😊", "☺️"]))
        session.add(new_user_emoji)
        session.commit()


class Donate(Base):
    __tablename__ = 'donate'
    id = Column(Integer, primary_key=True)
    remain = Column(Integer)
    name = Column(Integer)
