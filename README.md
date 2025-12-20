# OnionTrace

OnionTrace is a forensic analysis tool designed for correlating TOR traffic with potential evidence.

## Project Structure

```
oniontrace/
│
├── backend/
│   ├── app/
│   │   ├── core/                 # Core intelligence (Traffic correlation, Scoring)
│   │   ├── tor/                  # TOR network intelligence (Consensus, Toplogy)
│   │   ├── evidence/             # Evidence processing (PCAP, Logs)
│   │   ├── db/                   # Database layer
│   │   ├── api/                  # API layer
│   │   └── utils/                # Utilities
│   │
│   ├── main.py                   # Application entry point
│   └── requirements.txt
│
└── electron/                     # Frontend application (Future)
```
