def normalize_flow(flow: dict) -> dict:
    """
    Normalize flow direction so that:
    client = ephemeral port
    server = well-known port
    """

    if flow["src_port"] < flow["dst_port"]:
        client_ip = flow["dst_ip"]
        server_ip = flow["src_ip"]
        client_port = flow["dst_port"]
        server_port = flow["src_port"]
    else:
        client_ip = flow["src_ip"]
        server_ip = flow["dst_ip"]
        client_port = flow["src_port"]
        server_port = flow["dst_port"]

    return {
        "evidence_id": flow["evidence_id"],
        "client_ip": client_ip,
        "server_ip": server_ip,
        "client_port": client_port,
        "server_port": server_port,
        "protocol": flow["protocol"],
        "start_time": flow["start_time"],
        "end_time": flow["end_time"],
        "packet_count": flow["packet_count"],
        "byte_count": flow["byte_count"],
    }
