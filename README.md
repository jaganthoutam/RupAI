# MCP Payments Server

This repository contains a reference implementation of a payments server following the guidelines in `AGENT.md`.

## Development

Install dependencies:

```bash
pip install -r requirements/dev.txt
```

Run the server locally:

```bash
python -m app.main
```

The server listens on `0.0.0.0:8000` by default and exposes a health check at `/health`.
MCP JSON-RPC calls are handled via the `/rpc` endpoint.
