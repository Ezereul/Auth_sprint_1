from typing import TypedDict

User = TypedDict('User', {'username': str, 'password': str})


class StubDB:
    storage: dict[str, str] = {}

    def save_data(self, data: dict):
        self.storage.update(data)

    def get_data(self, key: str) -> User | None:
        data = self.storage.get(key)

        if not data:
            return None

        return {'username': key, 'password': data}


stub_database = StubDB()
