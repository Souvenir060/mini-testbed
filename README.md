# Mini NANDA Testbed

This testbed reproduces a simplified NANDA-style discovery chain:

User / Coordinator → NANDA Index → NANDA Registry → AgentFacts → A2A Endpoint → Agent Response

## Components

- `nanda-index-v2`: local NANDA Index, running on `http://localhost:3001`
- `nanda-registry`: local NANDA Registry, running on `http://localhost:3002`
- `coordinator/dashboard.py`: Streamlit dashboard, running on `http://localhost:8501`
- Railway agents:
  - Weather Agent: `https://nanda-agent-1-production.up.railway.app`
  - Robot Agent: `https://nanda-agent-2-production.up.railway.app`

## Current status

- Registry contains `agent-1` and `agent-2`
- Index contains organization `shuwen-demo`
- Dashboard can resolve a URN, fetch CatalogEntry, fetch AgentFacts, select A2A endpoint, and call the agent

## Next goals

- Add capability-based search, e.g., search by `weather`, `robotics`, or task description
- Add multiple agents and automatic team selection
- Add trust score, verification, and malicious-agent testing
- Later integrate Nanda Town for security evaluation
