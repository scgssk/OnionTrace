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
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
        tmp.write(await file.read())
        pcap_path = tmp.name

    raw = fetch_latest_consensus()
    relays = TorConsensusParser(raw).parse()

    return run_investigation(pcap_path, mode, relays)
