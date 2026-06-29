# Mini NANDA Testbed

This repository is a small integration testbed.

It does **not** contain the full NANDA source code. Instead, it connects several components together:

```text  
User / Coordinator
    ↓
NANDA Index
    ↓
NANDA Registry
    ↓
CatalogEntry
    ↓
AgentFacts
    ↓
A2A Endpoint
    ↓
Agent Response
```

The goal is to reproduce a simple NANDA-style agent discovery chain and make it easy for the team to extend later.

---

## 1. What has been completed

We have completed the following steps:

1. Deployed two agents on Railway:

   * Weather Agent
   * Robot Agent

2. Verified that both agents expose:

   * `/health`
   * `/query`
   * `/agentfacts`
   * `/a2a`

3. Verified A2A communication between the two Railway agents.

4. Reproduced a local NANDA Registry:

   * API: `http://localhost:3002`
   * Web UI: `http://localhost:3003`
   * Docs: `http://localhost:3002/docs`

5. Registered two agents into the local Registry:

   * `agent-1`
   * `agent-2`

6. Reproduced a local NANDA Index:

   * API: `http://localhost:3001`
   * Web UI: `http://localhost:3010`
   * Docs: `http://localhost:3001/docs`

7. Registered an organization into the local Index:

   * Organization: `yourname-demo`
   * Domain: `yourname-demo.local`
   * Registry URL: `http://localhost:3002`

8. Verified that a URN can be resolved by the Index:

```text
urn:ai:domain:yourname-demo.local:agent:agent-1
```

9. Built a small coordinator script and Streamlit dashboard that can automatically perform:

```text
URN → Index → Registry → AgentFacts → A2A endpoint → Agent response
```

---

## 2. Key idea

The current testbed shows that we no longer need to manually remember the agent runtime URL.

Instead, we can start from a stable agent name / locator, such as:

```text
urn:ai:domain:yourname-demo.local:agent:agent-1
```

Then the system automatically finds:

1. Which registry this organization uses
2. Which AgentFacts file describes the agent
3. Which A2A endpoint should be called
4. What response the agent returns

This is the basic idea of NANDA-style agent discovery.

---

## 3. Important concepts

### URN vs URL

A **URN** is a stable name.

Example:

```text
urn:ai:domain:yourname-demo.local:agent:agent-1
```

A **URL** is an address that can be visited.

Example:

```text
https://nanda-agent-1-production.up.railway.app/agentfacts
```

In simple words:

```text
URN = who the agent is
URL = where to access the agent information or endpoint
```

### NANDA Index

The Index does not directly store all agents.

It stores organization-level records.

For example, it knows:

```text
yourname-demo.local → http://localhost:3002
```

This means: if we want agents under `yourname-demo.local`, go to the Registry at `http://localhost:3002`.

### NANDA Registry

The Registry stores agent catalog entries.

For example:

```text
agent-1 → https://nanda-agent-1-production.up.railway.app/agentfacts
```

### CatalogEntry

A CatalogEntry is a lightweight registry record.

It contains basic information such as:

```text
identifier
displayName
description
tags
url to AgentFacts
```

### AgentFacts

AgentFacts is the detailed profile of an agent.

It contains:

```text
agent name
description
skills
capabilities
endpoints
telemetry
certification
```

### A2A endpoint

The A2A endpoint is the actual communication endpoint used by agents or coordinators.

Example:

```text
https://nanda-agent-1-production.up.railway.app/a2a
```

In this testbed, the Streamlit dashboard plays the role of a simple coordinator. It receives the user’s question, discovers the target agent, and calls the agent through A2A.

---

## 4. Project structure

This repository currently contains our own integration code:

```text
mini-testbed/
├── README.md
├── .gitignore
└── coordinator/
    ├── coordinator.py
    └── dashboard.py
```

The official NANDA repositories are external dependencies and should be cloned separately:

```text
nanda-registry
nanda-index-v2
```

---

## 5. Quick Start

### Step 1: Create working folder

```bash
mkdir -p full-nanda-repro
cd full-nanda-repro
```

---

### Step 2: Clone and run NANDA Registry

```bash
git clone https://github.com/projnanda/nanda-registry.git
cd nanda-registry
cp .env.example .env
```

Replace the default JWT secret:

```bash
sed -i '' "s/^JWT_SECRET=.*/JWT_SECRET=$(openssl rand -hex 32)/" .env
```

Start Registry:

```bash
docker compose up --build
```

In another terminal, test:

```bash
curl http://localhost:3002/health
```

Expected result:

```json
{"status":"ok","db":"ok"}
```

---

### Step 3: Register two agents into Registry

Login or register first, then save the Registry token.

Example:

```bash
export REGISTRY_TOKEN=$(curl -s -X POST 'http://localhost:3002/auth/register' \
  -H 'Content-Type: application/json' \
  --data-raw '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD","display_name":"YOUR_NAME"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')
```

Register Weather Agent:

```bash
curl -s -X POST 'http://localhost:3002/agents' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $REGISTRY_TOKEN" \
  --data-raw '{"agent_id":"agent-1","display_name":"Weather Predictor Agent","url":"https://nanda-agent-1-production.up.railway.app/agentfacts","media_type":"application/json","description":"Weather prediction and climate analysis agent.","tags":["weather","climate","forecast"],"version":"1.0.0"}'
```

Register Robot Agent:

```bash
curl -s -X POST 'http://localhost:3002/agents' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $REGISTRY_TOKEN" \
  --data-raw '{"agent_id":"agent-2","display_name":"Robot Expert Agent","url":"https://nanda-agent-2-production.up.railway.app/agentfacts","media_type":"application/json","description":"Robotics and automation systems expert agent.","tags":["robotics","automation","robots"],"version":"1.0.0"}'
```

Check Registry:

```bash
curl -s 'http://localhost:3002/agents' | python3 -m json.tool
```

Important note:

```text
agent_id should use hyphen, such as agent-1.
Do not use agent_1 in the Registry, because the Registry only accepts lowercase letters, numbers, and hyphens.
```

---

### Step 4: Clone and run NANDA Index

Go back to the working folder:

```bash
cd ..
git clone https://github.com/projnanda/nanda-index-v2.git
cd nanda-index-v2
cp .env.example .env
```

Replace the default JWT secret:

```bash
sed -i '' "s/^JWT_SECRET=.*/JWT_SECRET=$(openssl rand -hex 32)/" .env
```

If port `3000` is already used, change the web UI port to `3010`:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("docker-compose.yml")
text = p.read_text()
text = text.replace('"3000:3000"', '"3010:3000"')
text = text.replace("- 3000:3000", "- 3010:3000")
p.write_text(text)
PY
```

Start Index:

```bash
docker compose up --build
```

In another terminal, test:

```bash
curl http://localhost:3001/health
```

Expected result:

```json
{"status":"ok","db":"ok"}
```

---

### Step 5: Register local Registry into Index

Create Index account and save token:

```bash
export INDEX_TOKEN=$(curl -s -X POST 'http://localhost:3001/auth/register' \
  -H 'Content-Type: application/json' \
  --data-raw '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD","display_name":"YOUR_NAME"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')
```

Register organization:

```bash
curl -s -X POST 'http://localhost:3001/api/v1/orgs' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $INDEX_TOKEN" \
  --data-raw '{"org_id":"yourname-demo","display_name":"yourname NANDA Demo","hosting_path":"registry","domain":"yourname-demo.local","contact_email":"YOUR_EMAIL","registry_url":"http://localhost:3002","identifier":"urn:ai:domain:yourname-demo.local","media_type":"application/ai-catalog+json","description":"Local NANDA-style registry for two Railway agents.","tags":["demo","nanda","a2a"],"publisher":{"identifier":"urn:ai:domain:yourname-demo.local","displayName":"yourname NANDA Demo","identityType":"dns"},"catalog_metadata":{"org.projectnanda.preferredDiscovery":"ai-catalog","org.projectnanda.resolutionRole":"nested-ai-catalog"}}'
```

The organization may be created as `pending`.

For local testing, activate it manually:

```bash
docker compose exec db psql -U nanda -d nanda_index -c "UPDATE organizations SET status='active', email_verified=true WHERE org_id='yourname-demo';"
```

Check Index:

```bash
curl -s 'http://localhost:3001/api/v1/index' | python3 -m json.tool
```

---

### Step 6: Test URN resolution

```bash
curl -s 'http://localhost:3001/api/v1/resolve?locator=urn:ai:domain:yourname-demo.local:agent:agent-1' | python3 -m json.tool
```

Expected result:

The output should contain:

```text
registry_url: http://localhost:3002
identifier: agent-1
```

This means the Index can resolve the URN to the correct Registry.

---

### Step 7: Run coordinator

Go to this repository:

```bash
cd ../mini-testbed/coordinator
```

Create virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install streamlit requests
```

Run coordinator script:

```bash
python coordinator.py
```

Expected result:

The script should print:

```text
Resolved registry
CatalogEntry
AgentFacts
A2A endpoint
Agent response
```

---

### Step 8: Run Streamlit dashboard

```bash
streamlit run dashboard.py
```

Open:

```text
http://localhost:8501
```

Input:

```text
NANDA Index API:
http://localhost:3001

Agent URN / Locator:
urn:ai:domain:yourname-demo.local:agent:agent-1

Question:
Briefly explain what weather conditions are dangerous for outdoor robots.
```

Click the button.

Expected result:

The dashboard should show:

```text
1. Index Resolution
2. Registry CatalogEntry
3. AgentFacts
4. Selected A2A Endpoint
5. Agent Response
```

---

## 6. Current limitation

This is only a local testbed.

That means:

```text
localhost:8501
localhost:3001
localhost:3002
```

can only be accessed on the machine running the services.

---

## 7. Next Steps

### Task A: Reproduce the baseline

Run the whole testbed on your own computer.

### Task B: Improve this document with your own thoughts

### Task C: Add capability-based discovery

Currently, the dashboard resolves a specific URN.

Next, improve it so that users can search by capability, such as:

```text
weather
robotics
forecast
...
```

The system should search Registry entries and show candidate agents.

### Task D: Compare NANDA and AGNTCY

Study NANDA and AGNTCY/CoffeeAGNTCY at a high level.

---

## 8. Next direction

The current testbed is a starting point.

Possible extensions:

1. Capability-based agent discovery
2. Trust-aware agent selection
3. Malicious or fake AgentFacts testing
4. Multi-agent orchestration
5. NANDA vs AGNTCY comparison
6. Public deployment for team collaboration
7. Integration with Nanda Town for larger-scale experiments

The long-term research question is:

```text
How can we build a trust-aware discovery and orchestration testbed for the Internet of Agents?
```
