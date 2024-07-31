from model import db


class UniqueRule:
    def __init__(self, collection_name, field) -> None:
        self.collection_name = collection_name
        self.field = field

    def validate(self, value, field_name):
        data, _ = db.find_one(self.collection_name, {self.field: value})
        if data is not None:
            return f"data {field_name} harus unik"


class ExistsRule:
    def __init__(self, collection_name, field) -> None:
        self.collection_name = collection_name
        self.field = field

    def validate(self, value, field_name):
        data, _ = db.find_one(self.collection_name, {self.field: value})
        if data is None:
            return f"data {field_name} tidak ada di database"
