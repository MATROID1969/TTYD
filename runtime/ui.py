#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import matplotlib.figure as mpl_fig

from engine.ai_engine import generate_code
from engine.code_executor import execute_code
from engine.conversation_gate import classify_followup
from engine.question_rewriter import rewrite_question
from engine.conversation_logger import log_event
from engine.verbalizer import verbalize_result


from audio_recorder_streamlit import audio_recorder
import tempfile
import hashlib
import os
from openai import OpenAI


# In[ ]:


# =========================================================
# CSS
# =========================================================

def apply_theme_css(theme_color: str | None = None):
    css = """
    <style>
      .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 1rem !important;
      }

      textarea {
        font-size: 1.05rem !important;
        min-height: 70px !important;
        height: 70px !important;
      }

      .stpyplot {
        max-height: 520px !important;
        overflow-y: auto !important;
      }

      .streamlit-expanderContent {
        max-height: 550px !important;
        overflow-y: auto !important;
      }

      .answer-box {
        font-size: 2rem !important;
        line-height: 1.5 !important;
        padding: 1rem 1.2rem;
        background: #fff6f8;
        border-left: 5px solid #7a0019;
        border-radius: 6px;
        margin-top: 1rem;
      }

      .debug-box {
        background: #f3f3f3;
        border-left: 4px solid #999;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        color: #333;
      }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    if theme_color:
        st.markdown(
            f"""
            <style>
              .answer-box {{
                color: {theme_color} !important;
                border-left-color: {theme_color} !important;
              }}
            </style>
            """,
            unsafe_allow_html=True,
        )


# In[ ]:


# =========================================================
# Main UI
# =========================================================

def render_app_ui(cfg: dict, df, prompt: str, app_path: str):
    ui_cfg = cfg.get("ui", {})
    ai_cfg = cfg.get("ai", {})

    apply_theme_css(ui_cfg.get("theme_color"))

    st.title(cfg.get("app", {}).get("name", "Talk to Your Data"))
    desc = cfg.get("app", {}).get("description")
    if desc:
        st.caption(desc)

    # Conversation memory
    if "base_question" not in st.session_state:
        st.session_state["base_question"] = None
    if "last_audio_hash" not in st.session_state:
        st.session_state["last_audio_hash"] = None
    
    if "voice_question" not in st.session_state:
        st.session_state["voice_question"] = ""


    # Layout
    show_code_panel = bool(ui_cfg.get("show_code_panel", True))
    if show_code_panel:
        col_left, col_right = st.columns([3, 2])
    else:
        col_left, col_right = st.columns([1, 0.0001])

    code_placeholder = None
    if show_code_panel:
        with col_right:
            with st.expander("🧠 AI által generált kód", expanded=False):
                code_placeholder = st.empty()

    with col_left:
        # 🎙️ Hangbemondás
        audio_bytes = audio_recorder(
            recording_color="#ff3333",
            neutral_color="#cccccc",
            icon_name="microphone",
            icon_size="2x",
        )

        if audio_bytes:
            audio_hash = hashlib.md5(audio_bytes).hexdigest()

            if audio_hash != st.session_state["last_audio_hash"]:
                st.session_state["last_audio_hash"] = audio_hash

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name

                try:
                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                    with open(tmp_path, "rb") as audio_file:
                                transcript = client.audio.transcriptions.create(
                                    file=audio_file,
                                    model="whisper-1",
                                    language="hu",
                                    response_format="text",
                                    temperature=0,
                                    prompt=(
                                        "Magyar piackutatási és adatelemzési kérdések: "
                                        "gyorsétterem, csokoládé, százalék, darabszám, "
                                        "nők, férfiak, budapestiek."
                                    ),
                                )

                    st.session_state["voice_question"] = transcript

                finally:
                    os.remove(tmp_path)

        question = st.text_area(
                                "Írd be a kérdést:",
                                value=st.session_state.get("voice_question", ""),
                                placeholder="Pl.: Melyik a legnépszerűbb úticél?",
                            )


        run_clicked = st.button("Futtatás")
        result_placeholder = st.empty()
        

    # =====================================================
    # Run
    # =====================================================

    if run_clicked and question.strip():

        prev = st.session_state["base_question"]

        if prev:
            decision = classify_followup(prev, question)
        else:
            decision = "NEW"

        # Döntés megjelenítése
        final_question = None

        if decision == "UNCLEAR":
            result_placeholder.warning("Kérlek, pontosítsd a kérdésedet.")
            return

        if decision == "FOLLOWUP":
            final_question = rewrite_question(prev, question, model=ai_cfg.get("model", "gpt-4.1"))
        else:
            final_question = question

        # ---- AI futtatás ----

        model = ai_cfg.get("model", "gpt-4.1")
        temperature = ai_cfg.get("temperature", 0.0)

        log_event({
                    "previous_question": prev,
                    "user_input": question,
                    "gate_decision": decision,
                    "rewritten_question": final_question if decision == "FOLLOWUP" else None,
                    "sent_to_ai": final_question,
                    "app": cfg.get("app", {}).get("name"),
                })

        
        code = generate_code(
            user_question=final_question,
            system_prompt=prompt,
            model=model,
            temperature=temperature,
        )

        log_event({
                    "generated_code": code
                })
                        
        if code_placeholder is not None:
            code_placeholder.code(code, language="python")

        try:
            result = execute_code(code, df)
        
            if isinstance(result, mpl_fig.Figure):
                # 🔙 RÉGI, BEVÁLT DIAGRAM MEGJELENÍTÉS
                result_placeholder.pyplot(result)
        
            else:
                pretty_text = verbalize_result(
                                                question=final_question,
                                                result=result,
                                                model=ai_cfg.get("model", "gpt-4.1"),
                                                temperature=0.2,
                                            )

                result_placeholder.markdown(
                    f"<div class='answer-box'>{pretty_text}</div>",
                    unsafe_allow_html=True,
                )        
            # Ez lesz az új base_question
            st.session_state["base_question"] = final_question
            st.session_state["voice_question"] = ""

        
        except Exception as e:
            result_placeholder.error(str(e))
        


