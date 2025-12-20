import random

def generate_simulated_guards(sessions, all_guards, sticky_guards=3, noise=2):
    """
    Simulates TOR guard stickiness.

    - sticky_guards: guards common across all sessions
    - noise: random guards per session
    """

    all_guards = list(all_guards)
    base = set(random.sample(all_guards, sticky_guards))

    session_map = {}

    for s in sessions:
        extra = set(random.sample(all_guards, noise))
        session_map[s["session_id"]] = base | extra

    return session_map
