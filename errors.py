class UserAlreadyHasRoleError(Exception):
    pass


class UserDoesntHaveRoleError(Exception):
    pass


class RoleNotFoundError(Exception):
    pass


class AliasNotFoundError(Exception):
    pass


class EmojiAlreadyExistsError(Exception):
    pass


class EmptyInputError(Exception):
    pass
