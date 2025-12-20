import ipaddress
from app.db.engine import get_connection


def is_public_unicast(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return (
            addr.version == 4
            and not addr.is_private
            and not addr.is_loopback
            and not addr.is_multicast
            and not addr.is_reserved
            and not addr.is_link_local
        )
    except ValueError:
        return False


def validate_traffic(evidence_id: str) -> bool:
    """
    Returns True if PCAP likely contains TOR exit traffic.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT client_ip, server_ip
            FROM flows
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchall()

    public_hits = 0

    for row in rows:
        if is_public_unicast(row["client_ip"]) or is_public_unicast(row["server_ip"]):
            public_hits += 1
            break

    if public_hits == 0:
        print("[!] Traffic validation failed")
        print("[!] No public unicast IPs detected")
        print("[!] This PCAP does NOT contain TOR exit traffic")
        return False

    print("[+] Traffic validation passed (public IPs detected)")
    return True
