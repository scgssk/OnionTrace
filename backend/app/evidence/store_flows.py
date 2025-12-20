from app.db.engine import get_connection
from app.evidence.normalizer import normalize_flow


def store_flows(flows: list[dict]):
    with get_connection() as conn:
        for f in flows:
            nf = normalize_flow(f)

            conn.execute(
                """
                INSERT INTO flows (
                    evidence_id,
                    client_ip,
                    server_ip,
                    client_port,
                    server_port,
                    protocol,
                    start_time,
                    end_time,
                    packet_count,
                    byte_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nf["evidence_id"],
                    nf["client_ip"],
                    nf["server_ip"],
                    nf["client_port"],
                    nf["server_port"],
                    nf["protocol"],
                    nf["start_time"],
                    nf["end_time"],
                    nf["packet_count"],
                    nf["byte_count"],
                ),
            )

    print(f"[+] Stored {len(flows)} normalized flows")
