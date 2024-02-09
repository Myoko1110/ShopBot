from typing import Any


class Request:
    def __init__(
            self,
            id: int,
            title: str,
            description: str,
            requests: list[str]
    ):
        self.id = id
        self.title = title
        self.description = description
        self.requests = requests
