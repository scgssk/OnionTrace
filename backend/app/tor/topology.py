from collections import defaultdict
from typing import List
from app.tor.consensus import Relay


class TorTopology:
    def __init__(self, relays: List[Relay]):
        self.relays = relays
        self.guards = []
        self.exits = []

        self._classify()

    def _classify(self):
        for relay in self.relays:
            if relay.is_guard:
                self.guards.append(relay)
            if relay.is_exit:
                self.exits.append(relay)

    def summary(self) -> dict:
        return {
            "total_relays": len(self.relays),
            "guards": len(self.guards),
            "exits": len(self.exits),
        }
