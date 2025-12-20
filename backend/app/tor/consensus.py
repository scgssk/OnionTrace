import urllib.request
import datetime
import re
from typing import List
from app.tor.models import Relay

BASE_URL = (
    "https://collector.torproject.org/recent/"
    "relay-descriptors/consensuses/"
)


def fetch_latest_consensus() -> str:
    # 1. Fetch directory listing
    with urllib.request.urlopen(BASE_URL, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    # 2. Extract consensus filenames
    files = re.findall(
        r'href="(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-consensus)"',
        html,
    )

    if not files:
        raise RuntimeError("No consensus files found")

    # 3. Pick latest file
    latest = sorted(files)[-1]
    consensus_url = BASE_URL + latest

    print(f"[+] Using consensus file: {latest}")

    # 4. Fetch consensus file
    with urllib.request.urlopen(consensus_url, timeout=30) as resp:
        return resp.read().decode("utf-8")


class TorConsensusParser:
    def __init__(self, raw_text: str):
        self.lines = raw_text.splitlines()
        self.i = 0

    def parse(self) -> List[Relay]:
        relays: List[Relay] = []

        while self.i < len(self.lines):
            if self.lines[self.i].startswith("r "):
                relay = self._parse_relay()
                if relay:
                    relays.append(relay)
            else:
                self.i += 1

        return relays

    def _parse_relay(self) -> Relay | None:
        r_parts = self.lines[self.i].split()
        if len(r_parts) < 8:
            self.i += 1
            return None

        nickname = r_parts[1]
        fingerprint = r_parts[2]
        ip = r_parts[6]

        published = datetime.datetime.strptime(
            f"{r_parts[4]} {r_parts[5]}",
            "%Y-%m-%d %H:%M:%S",
        )

        is_guard = False
        is_exit = False
        is_bad_exit = False
        bandwidth = 0

        self.i += 1

        while self.i < len(self.lines):
            line = self.lines[self.i]

            if line.startswith("s "):
                flags = set(line.split()[1:])
                is_guard = "Guard" in flags
                is_exit = "Exit" in flags
                is_bad_exit = "BadExit" in flags or "MiddleOnly" in flags

            elif line.startswith("w "):
                for token in line.split():
                    if token.startswith("Bandwidth="):
                        bandwidth = int(token.split("=")[1])

            elif line.startswith("r "):
                break

            self.i += 1

        if is_exit and is_bad_exit:
            is_exit = False

        return Relay(
            relay_id=fingerprint,
            nickname=nickname,
            ip=ip,
            is_guard=is_guard,
            is_exit=is_exit,
            is_bad_exit=is_bad_exit,
            bandwidth=bandwidth,
            published=published,
        )
