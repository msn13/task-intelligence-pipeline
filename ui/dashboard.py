import streamlit as st
import pandas as pd
import sys, os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import config
from storage.sample_meetings import NOTES
from app import run_pipeline
from storage.json_store import load_json

st.set_page_config(page_title="AI Task Extractor", layout="wide")
st.title("🏥 Wellness Meeting → Task Pipeline")

# --- Sidebar ---
st.sidebar.header("Controls")
note_index = st.sidebar.selectbox("Select Meeting Note", range(len(NOTES)),
                                  format_func=lambda i: f"Meeting {i + 1}")
use_demo = st.sidebar.checkbox("Use saved demo data (no API call)")

# --- Show raw note ---
st.subheader("📋 Raw Meeting Note")
st.text_area("", NOTES[note_index], height=150, disabled=True)

# --- Extract ---
if st.button("⚡ Extract Tasks"):
    if use_demo:
        try:
            bundle = load_json(config.SAMPLE_OUTPUT / "tasks_bundle.json")
            st.session_state["bundle"] = bundle
        except FileNotFoundError:
            st.error("No saved demo data found. Run the pipeline once first.")
    else:
        with st.spinner("Calling Claude Haiku..."):
            try:
                bundle = run_pipeline(note_index=note_index)
                st.session_state["bundle"] = bundle
            except Exception as e:
                st.error(f"Pipeline failed: {e}")

# --- Display results ---
if "bundle" in st.session_state:
    bundle = st.session_state["bundle"]

    st.subheader("📝 Meeting Summary")
    st.info(bundle.get("summary", "No summary available."))

    tasks = bundle.get("tasks", [])
    st.subheader(f"✅ Extracted Tasks ({len(tasks)} found)")

    if tasks:
        df = pd.DataFrame(tasks)[["task_id", "description", "owner", "due_date", "priority", "status", "risk"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No tasks extracted.")