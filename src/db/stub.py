import uuid


class StubDB:
    storage: list[dict] = []

    def save_data(self, data: dict):
        data.update({'id': str(uuid.uuid4())})
        self.storage.append(data)

    def get_data(self, field: str, key: str) -> dict | None:
        for record in self.storage:
            if record[field] == key:
                return record
        return None


stub_database = StubDB()
