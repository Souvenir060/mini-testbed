import json
import urllib.parse
import urllib.request

INDEX_URL = "http://localhost:3001"
LOCATOR = "urn:ai:domain:shuwen-demo.local:agent:agent-1"

def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)

resolve_url = INDEX_URL + "/api/v1/resolve?" + urllib.parse.urlencode({"locator": LOCATOR})
resolved = get_json(resolve_url)

registry_url = resolved["index_record"]["registry_url"].rstrip("/")
agent_id = resolved["identifier"]

print("1. Resolved registry:", registry_url)
print("2. Resolved agent id:", agent_id)

entry = get_json(f"{registry_url}/agents/{agent_id}")
facts_url = entry["url"]

print("3. CatalogEntry points to AgentFacts:", facts_url)

facts = get_json(facts_url)
a2a_url = facts["endpoints"]["static"][0]

print("4. AgentFacts label:", facts.get("label"))
print("5. A2A endpoint:", a2a_url)

payload = {
    "content": {
        "text": "Briefly explain what weather conditions are dangerous for outdoor robots.",
        "type": "text"
    },
    "role": "user",
    "conversation_id": "index-registry-coordinator-demo",
    "agent_id": "coordinator-demo"
}

result = post_json(a2a_url, payload)

print("6. Agent response:")
print(json.dumps(result, indent=2, ensure_ascii=False))
