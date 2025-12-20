def explain_guard(guard_id, seen, total):
    return (
        f"Guard {guard_id} appeared in {seen} out of {total} sessions. "
        f"Repeated appearance across independent sessions increases confidence "
        f"due to TOR guard stickiness."
    )
