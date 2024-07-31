from apn_validators.rules import (AllowedFile, DateAfter, Email, Equals,
                                  GreaterThenOrEqual, Length, LessThenOrEqual,
                                  NotBlank, Numeric, Password)

err_message = {
    "blank": "{field_name} tidak boleh kosong",
    "email": "value {field_name} bukan valid email",
    "equals": "value {field_name} harus sama dengan {another_value}",
    "length": "panjang {field_name} harus berada diantara {min} and {max}",
}


class NotBlank(NotBlank):
    def __init__(self, message=err_message.get("blank")):
        self.message = message


class Email(Email):
    def __init__(self, message=err_message.get("email")):
        self.message = message


class Length(Length):
    def __init__(
        self,
        min_length: int,
        max_length: int,
        message=err_message.get("length"),
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.message = message


class GreaterThenOrEqual(GreaterThenOrEqual):
    def __init__(
        self,
        threshold: int,
        message="value {field_name} harus lebih atau sama dengan {threshold}",
    ):
        self.threshold = threshold
        self.message = message


class LessThenOrEqual(LessThenOrEqual):
    def __init__(
        self,
        threshold: int,
        message="value {field_name} harus lebih kecil atau sama dengan {threshold}",
    ):
        self.threshold = threshold
        self.message = message


class AllowedFile(AllowedFile):
    def __init__(
        self,
        allowed_extensions=None,
        message="{field_name} hanya menerima file {allowed_extensions}",
    ):
        self.allowed_extensions = allowed_extensions or {"png", "jpg", "jpeg"}
        self.message = message


class Numeric(Numeric):
    def __init__(self, message="{field_name} hanya bisa diisi angka") -> None:
        self.message = message


class Equals(Equals):
    def __init__(
        self,
        another_value: str,
        message="{field_name} harus sama dengan {another_value}",
    ):
        self.another_value = another_value
        self.message = message


class DateAfter(DateAfter):
    def __init__(
        self, target_date, message="{d[field_name]} harus setelah {d[target_date]}"
    ):
        self.target_date = target_date
        self.message = message
