from app.tor.consensus import fetch_latest_consensus, TorConsensusParser
from app.tor.topology import TorTopology
from app.db.repository import upsert_relays
from app.db.engine import get_connection
from pathlib import Path
import sqlite3

def init_db():
    schema_path = Path(__file__).parent / "app/db/schema.sql"
    try:
        with get_connection() as conn:
            conn.executescript(schema_path.read_text())
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("[!] Database tables already exist. Skipping initialization.")
        else:
            raise e

def main():
    print("[+] Initializing database")
    init_db()

    print("[+] Fetching TOR consensus")
    raw = fetch_latest_consensus()

    print("[+] Parsing relays")
    parser = TorConsensusParser(raw)
    relays = parser.parse()

    print(f"[+] Parsed {len(relays)} relays")

    print("[+] Storing relays")
    upsert_relays(relays)

    topo = TorTopology(relays)
    print("[+] Topology summary:", topo.summary())


if __name__ == "__main__":
    main()
