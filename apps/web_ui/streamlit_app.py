import os
from pathlib import Path

import streamlit as st
import requests

API_URL = "http://localhost:8000"
RAW_DIR = Path(os.getenv("DATA_DIR", "./data/raw_documents"))

st.set_page_config(page_title="Enterprise Knowledge Copilot", layout="centered")
st.title("Enterprise Knowledge Copilot")

st.caption(f"📁 Documents folder: `{RAW_DIR}`")

# -----------------------------
# Upload section
# -----------------------------
st.subheader("Upload documents")
uploaded_files = st.file_uploader(
    "Upload TXT / MD / PDF files",
    type=["txt", "md", "pdf"],
    accept_multiple_files=True,
)

col_u1, col_u2 = st.columns([1, 1])

with col_u1:
    save_clicked = st.button("Save uploaded files")

with col_u2:
    ingest_after_save = st.checkbox("Ingest immediately after saving", value=True)

def save_uploads(files):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        # keep original filename
        out_path = RAW_DIR / f.name
        with open(out_path, "wb") as w:
            w.write(f.getbuffer())
        saved.append(str(out_path))
    return saved

if save_clicked:
    if not uploaded_files:
        st.warning("Please upload at least one file.")
    else:
        saved_paths = save_uploads(uploaded_files)
        st.success(f"Saved {len(saved_paths)} file(s).")
        for p in saved_paths:
            st.write(f"✅ {p}")

        if ingest_after_save:
            with st.spinner("Ingesting documents..."):
                r = requests.post(f"{API_URL}/ingest", timeout=600)
            if r.status_code == 200:
                st.success(r.json())
            else:
                st.error(f"Ingest failed: {r.status_code} - {r.text}")

st.divider()

# -----------------------------
# Manual ingest button
# -----------------------------
st.subheader("Ingest documents (manual)")
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("Ingest Documents"):
        with st.spinner("Ingesting..."):
            r = requests.post(f"{API_URL}/ingest", timeout=600)
        if r.status_code == 200:
            st.success(r.json())
        else:
            st.error(f"Ingest failed: {r.status_code} - {r.text}")
with col2:
    st.caption("Uploads are saved into `data/raw_documents/` then indexed into Qdrant.")

st.divider()

# -----------------------------
# Chat history state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("agent"):
            st.markdown(f"🧠 **Agent:** `{msg['agent']}`")
        st.markdown(msg["text"])

        if msg.get("sources"):
            st.markdown("**Sources:**")
            for s in msg["sources"]:
                score = s.get("score", None)
                file_ = s.get("file", "unknown")
                if score is None:
                    st.write(f"- {file_}")
                else:
                    st.write(f"- {file_} (score: {score:.3f})")
                if s.get("snippet"):
                    st.caption(s["snippet"])

# -----------------------------
# Ask
# -----------------------------
prompt = st.chat_input("Ask a question about your documents...")
if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_URL}/ask",
                json={"question": prompt, "top_k": 2},
                timeout=600,
            )

        if resp.status_code != 200:
            st.error(f"API error: {resp.status_code} - {resp.text}")
        else:
            data = resp.json()
            agent = data.get("agent", "unknown")
            answer = data.get("answer", "")
            sources = data.get("sources", [])

            st.markdown(f"🧠 **Agent:** `{agent}`")
            st.markdown(answer)

            if sources:
                st.markdown("**Sources:**")
                for s in sources:
                    score = s.get("score", None)
                    file_ = s.get("file", "unknown")
                    if score is None:
                        st.write(f"- {file_}")
                    else:
                        st.write(f"- {file_} (score: {score:.3f})")
                    if s.get("snippet"):
                        st.caption(s["snippet"])

            # Save assistant message
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "agent": agent,
                    "text": answer,
                    "sources": sources,
                }
            )
