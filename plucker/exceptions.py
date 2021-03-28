from typing import Optional
from .tokeniser import Token


class PluckError(TypeError):
    """A mismatched type error while trying to populate a dataclass."""

    def __init__(self, message: str):
        """Initialise a type error with a message."""
        self.message = message

    def __str__(self):
        """Provide a useful string representation of the error."""
        # TODO: actually make this useful
        return self.message


class ExtractError(ValueError):
    """
    A fancier version of PluckError.

    TODO: Remove PluckError, keep this.
    """

    message: str
    token: Token
    path: Optional[str]

    def __init__(self, token: Token, message: str):
        """Initialise an error while processing a given token with a message."""
        self.token = token
        self.message = message
        self.path = None

    def __str__(self):
        """Provide a useful string representation of the error."""
        if self.path:
            return (
                f"{self.message}:\n"
                f"{self.path}\n"
                f"{' ' * self.token.location.start}{'^' * len(self.token.location)}"
            )
        else:
            return self.message
