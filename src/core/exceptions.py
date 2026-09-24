class UserError(Exception):
    """Base exception for users"""
    pass

class UserNotFoundError(UserError):
    """User not found in db"""
    pass

class UsernameTakenError(UserError):
    """Username already taken by other user"""
    pass

class EmailTakenError(UserError):
    """Email already taken by other user"""
    pass


class AuthError(Exception):
    """Base exception for authentication"""
    pass

class InvalidCredentialsError(AuthError):
    """Wrong login or password"""
    pass

class InvalidTokenError(AuthError):
    """Invalid token"""
    pass
