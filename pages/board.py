import streamlit as st
from login import get_session_from_session_state, set_session_from_params, get_session_from_cookies


if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k databázi")
    #st.switch_page("pages/board.py")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = st.session_state["cookies"]
set_session_from_params(st.session_state["sb_database"])
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if database is None:
    st.stop()

if session:
    st.write("**Under construction**")
    st.image("pictures/under_construction.png", use_container_width=True)
