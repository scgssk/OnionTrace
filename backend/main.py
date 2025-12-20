from app.tor.consensus import fetch_latest_consensus, TorConsensusParser
from app.tor.topology import TorTopology
from app.db.repository import upsert_relays
from app.db.engine import get_connection
from pathlib import Path
import sqlite3
from app.evidence.pcap_ingest import ingest_pcap
from app.evidence.flow_extract import extract_flows
from app.evidence.store_flows import store_flows    

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

    evidence_id = ingest_pcap("c:\\Z\\torspy\\sample_data\\tor_exit_ngrok.pcap")   # use any PCAP you have
    flows = extract_flows("c:\\Z\\torspy\\sample_data\\tor_exit_ngrok.pcap", evidence_id)

    print(f"[+] Extracted {len(flows)} flows")

    store_flows(flows)
if __name__ == "__main__":
    main()
