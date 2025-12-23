from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import tempfile

from app.pipeline import run_investigation
from app.tor.consensus import fetch_latest_consensus, TorConsensusParser

router = APIRouter()


@router.post("/investigate")
async def investigate(
    file: UploadFile = File(...),
    mode: str = Form("simulation")
):
    # 1. Persist uploaded PCAP safely
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
        tmp.write(await file.read())
        pcap_path = tmp.name

    # 2. Fetch TOR consensus once per investigation
    raw = fetch_latest_consensus()
    relays = TorConsensusParser(raw).parse()

    # 3. Run full investigation pipeline
    result = run_investigation(
        pcap_path=pcap_path,
        mode=mode,
        relays=relays
    )

    return result
