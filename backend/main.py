from app.tor.consensus import fetch_latest_consensus, TorConsensusParser
from app.tor.topology import TorTopology
from app.db.repository import upsert_relays
from app.db.engine import get_connection
from pathlib import Path
import sqlite3
from app.evidence.pcap_ingest import ingest_pcap
from app.evidence.flow_extract import extract_flows
from app.evidence.store_flows import store_flows    
from app.core.sessionize import build_sessions
from app.core.store_sessions import store_sessions
from app.core.exit_match import match_exit_relays
from app.evidence.validate import validate_traffic
import sys
from app.core.mode import MODE
from app.core.output import build_output
import random
random.seed(42)
import json
from pathlib import Path

mode = MODE
if len(sys.argv) > 1:
    mode = sys.argv[1]

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
    if not validate_traffic(evidence_id):
        print("[!] Aborting correlation pipeline safely")
        return

    sessions = build_sessions(evidence_id)
    store_sessions(sessions)

    # matched_sessions = match_exit_relays(vantage="server")
    
    if mode == "simulation":
        print("[*] Running in SIMULATION mode")

        from app.core.simulated_input import generate_simulated_guards
        from app.core.correlate import correlate_guards

        # Get all guard relay IDs from topology
        all_guards = {r.relay_id for r in relays if r.is_guard}

        session_guards = generate_simulated_guards(
            sessions=sessions,
            all_guards=all_guards
        )

        results = correlate_guards(session_guards)

        final_output = build_output(results, total_sessions=len(sessions))
        
        print("\n[+] Final Intelligence Output (Simulation Mode)")
        for item in final_output[:5]:
            print(item)

        
        out_path = Path("output_simulation.json")
        out_path.write_text(json.dumps(final_output, indent=2))

        print(f"[+] Output written to {out_path.resolve()}")
        return


if __name__ == "__main__":
    main()
