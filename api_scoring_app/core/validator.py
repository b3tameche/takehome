from typing import Any, Protocol

class IValidator(Protocol):

    def validate(self, spec: dict[str, Any]) -> bool:
        pass
