from pathlib import Path
from app.evidence.pcap_ingest import ingest_pcap
from app.evidence.flow_extract import extract_flows
from app.evidence.store_flows import store_flows
from app.evidence.validate import validate_traffic
from app.core.sessionize import build_sessions
from app.core.store_sessions import store_sessions
from app.core.exit_match import match_exit_relays
from app.core.output import build_output
from app.core.correlate import correlate_guards
from app.core.simulated_input import generate_simulated_guards
from app.core.realtime_input import derive_guard_candidates


def run_investigation(pcap_path: str, mode: str, relays):
    """
    Single product-grade investigation entry point
    """

    evidence_id = ingest_pcap(pcap_path)

    flows = extract_flows(pcap_path, evidence_id)
    store_flows(flows)

    if not validate_traffic(evidence_id):
        return {
            "status": "failed",
            "reason": "No public TOR-like traffic detected"
        }

    sessions = build_sessions(evidence_id)
    store_sessions(sessions)

    if mode == "simulation":
        all_guards = {r.relay_id for r in relays if r.is_guard}
        session_guards = generate_simulated_guards(sessions, all_guards)

    elif mode == "realtime":
        matched_sessions = match_exit_relays(vantage="server")
        if not matched_sessions:
            return {
                "status": "failed",
                "reason": "No TOR exit relays matched"
            }

        session_guards = derive_guard_candidates(
            matched_sessions=matched_sessions,
            relays=relays
        )
    else:
        return {"status": "failed", "reason": "Invalid mode"}

    results = correlate_guards(session_guards)
    output = build_output(results, total_sessions=len(session_guards))

    return {
        "status": "success",
        "mode": mode,
        "sessions": len(session_guards),
        "results": output
    }
