from app.db.engine import get_connection


def store_sessions(sessions: list[dict]):
    with get_connection() as conn:
        for s in sessions:
            conn.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    exit_ip,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    s["session_id"],
                    s["exit_ip"],
                    s["start_time"],
                    s["end_time"],
                ),
            )

    print(f"[+] Stored {len(sessions)} sessions")
