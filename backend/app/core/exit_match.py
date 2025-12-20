from app.db.engine import get_connection

def match_exit_relays(vantage: str = "server"):
    """
    Matches sessions to TOR exit relays.

    vantage:
      - 'server'  → Tor exit is CLIENT IP (your case)
      - 'exit'    → Tor exit is SERVER IP
    """

    if vantage == "server":
        join_field = "client_ip"
    else:
        join_field = "exit_ip"

    query = f"""
        SELECT
            s.session_id,
            s.exit_ip,
            s.start_time,
            s.end_time,
            r.relay_id,
            r.bandwidth,
            r.ip as tor_exit_ip
        FROM sessions s
        JOIN flows f ON s.session_id = f.evidence_id
        JOIN relays r ON f.{join_field} = r.ip
        WHERE r.is_exit = 1
          AND r.is_bad_exit = 0
        GROUP BY s.session_id
    """

    with get_connection() as conn:
        rows = conn.execute(query).fetchall()

    matched = []
    for row in rows:
        matched.append({
            "session_id": row["session_id"],
            "tor_exit_ip": row["tor_exit_ip"],
            "relay_id": row["relay_id"],
            "bandwidth": row["bandwidth"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
        })

    print(f"[+] Matched {len(matched)} sessions to TOR exit relays")
    return matched
