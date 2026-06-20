import json
import requests
import streamlit as st

st.set_page_config(page_title="Mini NANDA Testbed", layout="wide")
st.title("Mini NANDA Testbed")
st.caption("Index → Registry → AgentFacts → A2A endpoint → Agent response")

index_url = st.text_input("NANDA Index API", "http://localhost:3001")
locator = st.text_input("Agent URN / Locator", "urn:ai:domain:shuwen-demo.local:agent:agent-1")
question = st.text_area("Question to the resolved agent", "Briefly explain what weather conditions are dangerous for outdoor robots.")

if st.button("Resolve and Call Agent"):
    try:
        resolve_resp = requests.get(f"{index_url}/api/v1/resolve", params={"locator": locator}, timeout=20)
        resolve_resp.raise_for_status()
        resolved = resolve_resp.json()

        registry_url = resolved["index_record"]["registry_url"].rstrip("/")
        agent_id = resolved["identifier"]

        entry_resp = requests.get(f"{registry_url}/agents/{agent_id}", timeout=20)
        entry_resp.raise_for_status()
        entry = entry_resp.json()

        facts_resp = requests.get(entry["url"], timeout=20)
        facts_resp.raise_for_status()
        facts = facts_resp.json()

        a2a_url = facts["endpoints"]["static"][0]

        payload = {
            "content": {"text": question, "type": "text"},
            "role": "user",
            "conversation_id": "mini-nanda-dashboard-demo",
            "agent_id": "dashboard"
        }

        result_resp = requests.post(a2a_url, json=payload, timeout=180)
        result_resp.raise_for_status()
        result = result_resp.json()

        st.subheader("1. Index Resolution")
        st.json(resolved)

        st.subheader("2. Registry CatalogEntry")
        st.json(entry)

        st.subheader("3. AgentFacts")
        st.json(facts)

        st.subheader("4. Selected A2A Endpoint")
        st.code(a2a_url)

        st.subheader("5. Agent Response")
        st.json(result)

    except Exception as e:
        st.error(str(e))
