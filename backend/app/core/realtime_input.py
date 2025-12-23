from collections import defaultdict
from datetime import datetime

BANDWIDTH_RATIO = 0.5  # conservative threshold


def derive_guard_candidates(matched_sessions, relays):
    """
    Real-time guard candidate derivation.

    matched_sessions: list of dicts from exit_match.py
    relays: list of Relay objects (from consensus)

    Returns:
      { session_id: set(guard_relay_ids) }
    """

    # Pre-filter guards only once
    guard_relays = [
        r for r in relays
        if r.is_guard and not r.is_bad_exit
    ]

    session_guards = defaultdict(set)

    for s in matched_sessions:
        session_id = s["session_id"]
        start = _parse_ts(s["start_time"])
        end = _parse_ts(s["end_time"])
        exit_bw = s["bandwidth"]

        for g in guard_relays:
            # 1️⃣ Temporal plausibility
            if g.published > end:
                continue

            # 2️⃣ Bandwidth plausibility
            if g.bandwidth < exit_bw * BANDWIDTH_RATIO:
                continue

            session_guards[session_id].add(g.relay_id)

    return dict(session_guards)


def _parse_ts(ts):
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts)
