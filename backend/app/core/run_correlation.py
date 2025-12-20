MODE = "simulation"   # switch to "realtime" later

def run_correlation(sessions, all_guards):
    if MODE == "simulation":
        from app.core.simulated_input import generate_simulated_guards
        session_guards = generate_simulated_guards(sessions, all_guards)

    elif MODE == "realtime":
        from app.core.realtime_input import derive_guard_candidates
        session_guards = derive_guard_candidates(sessions)

    else:
        raise ValueError("Invalid mode")

    from app.core.correlate import correlate_guards
    return correlate_guards(session_guards)
