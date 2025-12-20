from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Relay:
    relay_id: str          # fingerprint (base64)
    nickname: str
    ip: str
    is_guard: bool
    is_exit: bool
    is_bad_exit: bool
    bandwidth: int
    published: datetime
