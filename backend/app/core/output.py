from app.core.labels import confidence_label
from app.core.explain import explain_guard


def build_output(results, total_sessions):
    output = []

    for r in results:
        output.append({
            "guard_id": r["guard_id"],
            "confidence": r["confidence"],
            "confidence_level": confidence_label(r["confidence"]),
            "sessions_seen": r["seen_sessions"],
            "explanation": explain_guard(
                r["guard_id"],
                r["seen_sessions"],
                total_sessions
            )
        })

    return output
