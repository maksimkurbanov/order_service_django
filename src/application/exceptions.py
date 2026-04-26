class UseCaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NotFoundError(UseCaseError):
    pass


class InsufficientStockError(UseCaseError):
    pass
