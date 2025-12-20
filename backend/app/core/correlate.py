from collections import defaultdict

def correlate_guards(session_guards: dict):
    """
    session_guards:
      { session_id: set(guard_ids) }
    """

    counts = defaultdict(int)
    total_sessions = len(session_guards)

    for guards in session_guards.values():
        for g in guards:
            counts[g] += 1

    results = []
    for guard, seen in counts.items():
        confidence = round(seen / total_sessions, 3)
        results.append({
            "guard_id": guard,
            "seen_sessions": seen,
            "confidence": confidence
        })

    return sorted(results, key=lambda x: x["confidence"], reverse=True)
