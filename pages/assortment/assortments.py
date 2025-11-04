import streamlit as st
import pandas as pd
import numpy as np
from login import get_session_from_session_state

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k databázi")
    #st.switch_page("pages/board.py")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if database is None:
    #st.query_params.clear() 
    #st.switch_page("pages/board.py")
    st.stop()

try:
    database.rpc("create_owner_id").execute()
except:
    st.query_params.clear() 
    #st.switch_page("pages/board.py")
    st.stop()

st.write("**Seznam sortimentů**")
st.write("**Under construction**")
st.image("pictures/under_construction.png", use_container_width=True)
