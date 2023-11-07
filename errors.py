class EmptyInputError(Exception):
    pass


class UserAlreadyHasRoleError(Exception):
    pass


class UserDoesntHaveRoleError(Exception):
    pass


class RoleNotFoundError(Exception):
    pass


class RoleAlreadyExistsError(Exception):
    pass


class AliasNotFoundError(Exception):
    pass


class AliasAlreadyExistsError(Exception):
    pass


class UserAlreadyHasEmojiError(Exception):
    pass


class UserDoesntHaveEmojiError(Exception):
    pass


class EmojiAlreadyTakenError(Exception):
    pass


class EmojiLimitReachedError(Exception):
    pass


class SymbolIsntEmojiError(Exception):
    pass
