from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Result:
    ok: bool
    data: Any = None
    error: Optional[str] = None
    status_code: Optional[int] = None


def success(data: Any = None, status_code: int = 200) -> Result:
    return Result(ok=True, data=data, status_code=status_code)


def failure(error: str, status_code: int = 400) -> Result:
    return Result(ok=False, error=error, status_code=status_code)
