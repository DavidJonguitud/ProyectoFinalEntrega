class UserException(Exception):
    pass


class UserAlreadyExistsError(UserException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"The email '{email} is already registered.")


class InvalidCredentialsError(UserException):
    def __init__(self):
        super().__init__("Invalid email or password.")


class DatabaseTransactionError(UserException):
    def __init__(self, message: str):
        super().__init__(f"Database transaction failed {message}")
