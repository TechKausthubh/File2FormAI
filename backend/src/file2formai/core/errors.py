class ApplicationError(Exception):
    """Base class for safe application-layer errors."""

    status_code = 500
    detail = "An unexpected application error occurred"


class ResourceNotFoundError(ApplicationError):
    status_code = 404
    detail = "Resource not found"


class AuthenticationRequiredError(ApplicationError):
    status_code = 401
    detail = "Authentication required"


class PermissionDeniedError(ApplicationError):
    status_code = 403
    detail = "Permission denied"


class ConflictError(ApplicationError):
    status_code = 409

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
