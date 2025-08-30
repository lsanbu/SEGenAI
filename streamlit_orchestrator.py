import os, json, traceback
import streamlit as st
from dotenv import load_dotenv

# load env (.env should have OPENAI_API_KEY and CLAUDE_API_KEY)
load_dotenv()

# local agents you already have
from llm_agent import propose_next_step           # Listener Agent
from schema_types import IdeaSchema
from analyst_agent import run_analyst_agent       # Analyst (Claude)

st.set_page_config(page_title="Idea Validator (Listener → Analyst)", page_icon="🧠", layout="wide")
st.title("Idea Validator")
st.caption("Paste an idea → we auto-structure it → send to Analyst → show final results.")

with st.form("idea_form"):
    idea_text = st.text_area(
        "Your idea (one input, one click, done):",
        height=140,
        placeholder="e.g., A micro-SaaS Greetings Generator so anyone can send customized greetings instead of generic ones."
    )
    submitted = st.form_submit_button("Validate Idea")

if submitted:
    if not idea_text.strip():
        st.warning("Please enter your idea.")
        st.stop()

    try:
        # Step 1: Listener (auto-fill schema — Option 2 logic, no back-and-forth)
        st.write("⏳ Running Listener Agent…")
        empty_schema = IdeaSchema()
        listener_out = propose_next_step(idea_text, empty_schema, [])
        schema_data = listener_out.get("current_schema") or {}
        st.success("Listener Agent complete ✅")

        # Step 2: Analyst (Claude)
        st.write("⏳ Running Analyst Agent…")
        analyst_report = run_analyst_agent(schema_data)
        st.success("Analyst Agent complete ✅")

        # Display (one screen, two sections)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Structured Idea (Listener Output)")
            st.code(json.dumps(schema_data, indent=2, ensure_ascii=False), language="json")
        with col2:
            st.subheader("Validation Report (Analyst Output)")
            st.code(json.dumps(analyst_report, indent=2, ensure_ascii=False), language="json")

        # Optional: single downloadable combined output
        combined = {
            "listener_schema": schema_data,
            "analyst_report": analyst_report
        }
        st.download_button("Download Combined JSON", data=json.dumps(combined, indent=2, ensure_ascii=False),
                           file_name="idea_validation.json", mime="application/json")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.exception(traceback.format_exc())
