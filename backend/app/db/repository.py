from app.db.engine import get_connection
from app.tor.consensus import Relay


def upsert_relays(relays):
    with get_connection() as conn:
        for r in relays:
            conn.execute(
                """
                INSERT INTO relays (
                    relay_id, nickname, ip,
                    is_guard, is_exit, is_bad_exit,
                    bandwidth, published, last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(relay_id) DO UPDATE SET
                    ip=excluded.ip,
                    is_guard=excluded.is_guard,
                    is_exit=excluded.is_exit,
                    is_bad_exit=excluded.is_bad_exit,
                    bandwidth=excluded.bandwidth,
                    published=excluded.published,
                    last_seen=CURRENT_TIMESTAMP
                """,
                (
                    r.relay_id,
                    r.nickname,
                    r.ip,
                    int(r.is_guard),
                    int(r.is_exit),
                    int(r.is_bad_exit),
                    r.bandwidth,
                    r.published,
                ),
            )
