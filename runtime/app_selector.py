import streamlit as st
from engine.app_registry import list_apps
from runtime.app_runner import run_app


def run_app_selector():
    st.set_page_config(layout="wide")

    # Ha már fut egy app → ne mutassuk a választót
    if "selected_app" in st.session_state:
        run_app(st.session_state["selected_app"])
        return

    # ---- App selector UI ----
    st.title("🧠 Talk to Your Data")

    apps = list_apps("apps")

    if not apps:
        st.error("Nincsenek elérhető appok az apps/ könyvtárban.")
        return

    st.markdown("### Válassz egy alkalmazást")

    options = {app["name"]: app for app in apps}

    selected_name = st.selectbox(
        "Elérhető alkalmazások",
        list(options.keys())
    )

    selected_app = options[selected_name]

    if st.button("Indítás"):
        st.session_state["selected_app"] = selected_app["path"]
        st.rerun()
