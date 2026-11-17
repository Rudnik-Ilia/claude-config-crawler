from typing import Self


class GH:
    def __init__(self, endpoint: str) -> None:
        self.command = ["gh", "api", endpoint]

    @classmethod
    def api(cls, endpoint: str) -> Self:
        return cls(endpoint)

    def method(self, method: str) -> Self:
        self.command.extend(["--method", method])
        return self

    def field(self, name: str, value: str | int) -> Self:
        self.command.extend(["-f", f"{name}={value}"])
        return self

    def build(self) -> list[str]:
        return self.command.copy()
