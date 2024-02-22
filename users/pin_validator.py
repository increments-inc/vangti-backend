import string
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PINValidator:
    def __init__(self, min_length=5, max_length=5):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password must not contain more than %(min_length)d characters."),
                code="password_too_big",
                params={"max_length": self.max_length},
            )
        for character in password:
            if character not in string.digits:
                raise ValidationError(
                    _("This password must contain only digits."),
                    code="password_not_digits",
                    params={"min_length": self.min_length},
                )

    def get_help_text(self):
        return _(
            "Your password must contain only digits"
            % {"min_length": self.min_length}
        )