# Python Blockchain Simulator

A lightweight, fully functional decentralized blockchain prototype built from scratch in Python. This project was developed for educational purposes to deeply understand the core mechanics of blockchain technology, distributed ledgers, and network consensus.

## Key Features

- **Object-Oriented Architecture:** Solid POO foundation modeling blocks, transaction pools, and the ledger state.
- **Cryptographic Immutability:** Secure block chaining using SHA-256 cryptographic hashing (`hashlib`).
- **Proof-of-Work Consensus:** Implemented a mining algorithm mimicking real-world consensus mechanisms.
- **Decentralized P2P Network:** Built a REST API with Flask allowing multiple distinct nodes to register, share transactions, and mine blocks.
- **Conflict Resolution (Longest-Chain Rule):** Automatic consensus algorithm that queries neighboring nodes and resolves ledger conflicts.
- **Network Resilience:** Robust exception handling (`requests`) to prevent node crashes when neighboring peers are offline.

## Tech Stack

- **Language:** Python 3.14+
- **Framework:** Flask (REST API)
- **Libraries:** Requests, Hashlib, UUID, Urllib

Make sure you have Python installed, then set up your virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask requests
