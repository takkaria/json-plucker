from typing import Optional, Tuple


class PluckError(TypeError):
    """A mismatched type error while trying to populate a dataclass."""

    def __init__(self, message: str):
        """Initialise a type error with a message."""
        self.message = message

    def __str__(self):
        """Provide a useful string representation of the error."""
        # TODO: actually make this useful
        return self.message


class TokeniserError(ValueError):
    """A parse error while tokenising."""

    message: str
    context: Optional[Tuple[str, int]] = None

    def __init__(self, message: str):
        """Initialise a parse error with a message."""
        self.message = message

    def __str__(self):
        """Provide a useful string representation of the error."""
        if self.context is None:
            return self.message
        else:
            path, idx = self.context
            return f"{self.message} at index {idx}:\n" + f"{path}\n" + f"{' ' * idx}^"
