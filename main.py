import os
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import uuid
from login import set_session_from_params, get_session_from_session_state, get_session_from_cookies, get_login_frame, get_loged_frame

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")
APP_NAME = os.getenv("APP_NAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

page_board     = st.Page("pages/board.py",     title="Board",            url_path="board")
page_companies = st.Page("pages/companies.py", title="Seznam partnerů",  url_path="companies")
page_company   = st.Page("pages/_company.py",  title="Detail partnera",  url_path="company")
page_test      = st.Page("pages/page_test.py", title="Test",             url_path="test")
page_settings  = st.Page("pages/settings.py",  title="Nastavení",        url_path="settings")
pg = st.navigation([page_board, page_companies, page_company, page_test, page_settings])


cookies = EncryptedCookieManager(prefix=APP_NAME, password=APP_PASSWORD)
if not cookies.ready():
    #st.stop()
    #st.write("Načítám cookies")
    pass

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

database = get_client()
if "sb_database" not in st.session_state:
    st.session_state["sb_database"] = database

st.session_state["app_base_url"] = APP_BASE_URL

st.set_page_config(page_title="LEJSEK", page_icon="lejsek_sedy_head.png")

session = None

set_session_from_params(st.session_state["sb_database"])
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)

if session:
    col_picture, col_login = st.columns(2)
    with col_picture:
        with st.container(border=True):
            #st.image("lejsek_sedy_vetev_doprava.png", use_container_width=True)
            st.image("lejsek_sedy_vetev_7.png", use_container_width=True)
    with col_login:
        with st.container(border=True):
            get_loged_frame(session, cookies)
else:
    col_picture, col_login = st.columns(2)
    with col_picture:
        with st.container(border=True):
            st.image("lejsek_sedy_login.png", use_container_width=True)
            st.markdown("# L.E.J.S.E.K.")
    with col_login:
        with st.container(border=True):
            get_login_frame(cookies, APP_BASE_URL)

pg.run()
