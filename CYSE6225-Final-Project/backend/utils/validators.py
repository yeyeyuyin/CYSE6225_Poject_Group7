import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_RE.match(email))


def is_valid_password(password: str) -> bool:
    """Minimum 8 chars, at least one letter and one number."""
    if not password or len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    return has_letter and has_number


def is_valid_rating(score) -> bool:
    try:
        score = int(score)
    except (TypeError, ValueError):
        return False
    return 0 <= score <= 5
