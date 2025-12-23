from pathlib import Path
from collections import defaultdict

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


def _build_confidence_timeline(session_guards: dict):
    """
    Builds confidence-over-time series.
    Returns:
      { guard_id: [c1, c2, c3, ...] }
    """
    guard_counts = defaultdict(int)
    timeline = defaultdict(list)

    sessions = list(session_guards.values())
    total = 0

    for guards in sessions:
        total += 1
        for g in guards:
            guard_counts[g] += 1

        for g, count in guard_counts.items():
            timeline[g].append(round(count / total, 3))

    return dict(timeline)


def run_investigation(pcap_path: str, mode: str, relays):
    """
    Single product-grade investigation entry point
    """

    # 1️⃣ Evidence ingestion
    evidence_id = ingest_pcap(pcap_path)

    flows = extract_flows(pcap_path, evidence_id)
    store_flows(flows)

    if not validate_traffic(evidence_id):
        return {
            "status": "failed",
            "reason": "No public TOR-like traffic detected",
            "timeline": {},
            "results": [],
            "sessions": 0,
        }

    # 2️⃣ Session reconstruction
    sessions = build_sessions(evidence_id)
    store_sessions(sessions)

    # 3️⃣ Guard candidate derivation
    if mode == "simulation":
        all_guards = {r.relay_id for r in relays if r.is_guard}
        session_guards = generate_simulated_guards(
            sessions=sessions,
            all_guards=all_guards
        )

    elif mode == "realtime":
        matched_sessions = match_exit_relays(vantage="server")
        if not matched_sessions:
            return {
                "status": "failed",
                "reason": "No TOR exit relays matched",
                "timeline": {},
                "results": [],
                "sessions": 0,
            }

        session_guards = derive_guard_candidates(
            matched_sessions=matched_sessions,
            relays=relays
        )
    else:
        return {
            "status": "failed",
            "reason": "Invalid mode",
            "timeline": {},
            "results": [],
            "sessions": 0,
        }

    if not session_guards:
        return {
            "status": "failed",
            "reason": "No guard candidates derived",
            "timeline": {},
            "results": [],
            "sessions": 0,
        }

    # 4️⃣ Correlation
    results = correlate_guards(session_guards)
    output = build_output(results, total_sessions=len(session_guards))

    # 5️⃣ Confidence-over-time (NEW)
    timeline = _build_confidence_timeline(session_guards)

    # 6️⃣ Final response (contract-safe)
    return {
        "status": "success",
        "mode": mode,
        "sessions": len(session_guards),
        "results": output,
        "timeline": timeline,
    }
