import hashlib
from pathlib import Path
from app.db.engine import get_connection
import uuid


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ingest_pcap(pcap_path: str) -> str:
    """
    Registers a PCAP file as forensic evidence.
    Returns evidence_id.
    """
    path = Path(pcap_path)
    if not path.exists():
        raise FileNotFoundError(f"PCAP not found: {pcap_path}")

    file_hash = sha256_file(path)
    evidence_id = str(uuid.uuid4())

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO evidence (evidence_id, type, sha256)
            VALUES (?, ?, ?)
            """,
            (evidence_id, "pcap", file_hash),
        )

    print(f"[+] Evidence registered: {evidence_id}")
    print(f"[+] SHA256: {file_hash}")

    return evidence_id
