import uuid
from app.db.engine import get_connection
from datetime import datetime,timedelta

SESSION_GAP_SECONDS = 30
MIN_FLOWS_PER_SESSION = 3

def parse_ts(ts):
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts)



def build_sessions(evidence_id: str):
    """
    Groups flows into TOR exit sessions.
    Returns list of session dicts.
    """

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                server_ip,
                start_time,
                end_time
            FROM flows
            WHERE evidence_id = ?
            ORDER BY server_ip, start_time
            """,
            (evidence_id,),
        ).fetchall()

    sessions = []
    current = None

    for row in rows:
        server_ip = row["server_ip"]
        start = parse_ts(row["start_time"])
        end = parse_ts(row["end_time"])

        if current is None:
            current = _new_session(server_ip, start, end)
            continue

        gap = (start - current["last_end"]).total_seconds()

        if server_ip == current["exit_ip"] and gap <= SESSION_GAP_SECONDS:
            current["last_end"] = max(current["last_end"], end)
            current["flow_count"] += 1
        else:
            if current["flow_count"] >= MIN_FLOWS_PER_SESSION:
                sessions.append(_finalize_session(current))

            current = _new_session(server_ip, start, end)

    if current and current["flow_count"] >= MIN_FLOWS_PER_SESSION:
        sessions.append(_finalize_session(current))

    print(f"[+] Built {len(sessions)} sessions")
    return sessions


def _new_session(exit_ip, start, end):
    return {
        "session_id": str(uuid.uuid4()),
        "exit_ip": exit_ip,
        "start_time": start,
        "last_end": end,
        "flow_count": 1,
    }


def _finalize_session(session):
    return {
        "session_id": session["session_id"],
        "exit_ip": session["exit_ip"],
        "start_time": session["start_time"],
        "end_time": session["last_end"],
        "flow_count": session["flow_count"],
    }
