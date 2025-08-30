import os
import json
import streamlit as st
from schema_types import IdeaSchema
from extractors import extract_text_from_pdf, extract_text_from_docx, transcribe_audio, consolidate_inputs
from llm_agent import propose_next_step
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

st.set_page_config(page_title="Listener Agent (Intake)", page_icon="📝", layout="centered")

# ---- Session State ----
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "aggregated_text" not in st.session_state:
    st.session_state.aggregated_text = ""
if "schema" not in st.session_state:
    st.session_state.schema = IdeaSchema()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "pending_field" not in st.session_state:
    st.session_state.pending_field = None

st.title("Listener Agent (Intake) 📝")
st.caption("Capture typed, voice, or document input. Clarify missing details one question at a time.")


# ---- Input widgets ----
st.subheader("1) Provide your idea")
typed = st.text_area("Type your idea in a few lines", height=140, placeholder="e.g., An AI bot that validates startup ideas instantly...")

col1, col2 = st.columns(2)
with col1:
    doc_file = st.file_uploader("Upload a document (PDF or DOCX)", type=["pdf", "docx"])
with col2:
    audio_file = st.file_uploader("Upload voice note (webm/wav/m4a/mp3)", type=["webm", "wav", "m4a", "mp3"])

if st.button("Process Inputs ▶️", type="primary"):
    doc_text = ""
    audio_text = ""

    if doc_file is not None:
        data = doc_file.read()
        if doc_file.type == "application/pdf" or doc_file.name.lower().endswith(".pdf"):
            doc_text = extract_text_from_pdf(data)
        else:
            doc_text = extract_text_from_docx(data)

    if audio_file is not None:
        audio_bytes = audio_file.read()
        try:
            audio_text = transcribe_audio(audio_bytes, filename=audio_file.name)
        except Exception as e:
            st.error(f"Transcription error: {e}")
            audio_text = ""

    agg = consolidate_inputs(typed, doc_text, audio_text)
    st.session_state.aggregated_text = agg

    # First LLM pass — try extracting fields & asking the first follow-up
    result = propose_next_step(agg, st.session_state.schema, st.session_state.chat_history)
    st.session_state.schema = IdeaSchema(**result.get("current_schema", {}))
    st.session_state.pending_question = result.get("question")
    st.session_state.pending_field = result.get("missing_field")

    # Show progress
    missing = st.session_state.schema.missing_required_fields()
    st.success(f"Processed. Missing required fields: {', '.join(missing) if missing else 'None'}")

# ---- Follow-up loop ----
if st.session_state.aggregated_text:
    st.subheader("2) Clarifications")
    if st.session_state.pending_question:
        st.info(st.session_state.pending_question)
        ans = st.text_input("Your answer", key="answer_box")

        colA, colB = st.columns([1,1])
        with colA:
            if st.button("Submit Answer ➤"):
                if ans.strip():
                    # Append to history & aggregated_text
                    st.session_state.chat_history.append({"role": "user", "content": ans.strip()})
                    st.session_state.aggregated_text += f"\n\n[ANSWER to {st.session_state.pending_field or 'unknown'}]\n{ans.strip()}"

                    # Re-run agent
                    result = propose_next_step(st.session_state.aggregated_text, st.session_state.schema, st.session_state.chat_history)
                    st.session_state.schema = IdeaSchema(**result.get("current_schema", {}))
                    st.session_state.pending_question = result.get("question")
                    st.session_state.pending_field = result.get("missing_field")

                    st.rerun()
                else:
                    st.warning("Please enter an answer.")
        with colB:
            if st.button("Skip"):
                # Put a placeholder so agent tries next field
                st.session_state.chat_history.append({"role": "user", "content": "(skip) I don't know yet."})
                st.session_state.aggregated_text += f"\n\n[ANSWER skipped for {st.session_state.pending_field or 'unknown'}]"
                result = propose_next_step(st.session_state.aggregated_text, st.session_state.schema, st.session_state.chat_history)
                st.session_state.schema = IdeaSchema(**result.get("current_schema", {}))
                st.session_state.pending_question = result.get("question")
                st.session_state.pending_field = result.get("missing_field")
                st.rerun()
    else:
        st.success("No more questions. Required fields appear complete.")

# ---- Final schema & actions ----
if st.session_state.aggregated_text:
    st.subheader("3) Current Idea Schema")
    schema_json = json.dumps(
        st.session_state.schema.model_dump(),
        indent=2,
        ensure_ascii=False
    )
    st.code(schema_json, language="json")

    # Simple completeness badge
    missing = st.session_state.schema.missing_required_fields()
    if not missing:
        st.success("✅ All required fields present. Ready for downstream agents.")
    else:
        st.warning(f"Still missing: {', '.join(missing)}")

    st.download_button("Download JSON", data=schema_json, file_name="idea_schema.json", mime="application/json")

st.divider()
if st.button("🔄 Reset Session"):
    for k in ["session_id", "aggregated_text", "schema", "chat_history", "pending_question", "pending_field"]:
        st.session_state.pop(k, None)
    st.rerun()

st.caption("Tip: For live mic capture in Streamlit, integrate `streamlit-webrtc`. For now, upload your audio file.")
