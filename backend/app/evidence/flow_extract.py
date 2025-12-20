from scapy.all import rdpcap, IP, TCP, UDP
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm


def extract_flows(pcap_path: str, evidence_id: str):
    """
    Extracts network flows from a PCAP file.
    Returns a list of flow dicts.
    """

    packets = rdpcap(pcap_path)
    flows = {}

    for pkt in tqdm(packets, desc="[*] Processing packets"):
        if IP not in pkt:
            continue

        ip = pkt[IP]
        proto = None
        sport = dport = None

        if TCP in pkt:
            proto = "TCP"
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
        elif UDP in pkt:
            proto = "UDP"
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
        else:
            continue

        key = (
            ip.src,
            sport,
            ip.dst,
            dport,
            proto,
        )

        ts = datetime.fromtimestamp(float(pkt.time))
        size = len(pkt)

        if key not in flows:
            flows[key] = {
                "evidence_id": evidence_id,
                "src_ip": ip.src,
                "dst_ip": ip.dst,
                "src_port": sport,
                "dst_port": dport,
                "protocol": proto,
                "start_time": ts,
                "end_time": ts,
                "packet_count": 1,
                "byte_count": size,
            }
        else:
            f = flows[key]
            f["end_time"] = ts
            f["packet_count"] += 1
            f["byte_count"] += size

    return list(flows.values())
