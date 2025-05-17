from typing import Any, Protocol

class IValidator(Protocol):

    def validate(self) -> bool:
        pass
