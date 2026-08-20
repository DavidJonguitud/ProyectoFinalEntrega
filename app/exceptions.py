class ServiceError(Exception):
    pass


class DatabaseTransactionError(ServiceError):
    pass