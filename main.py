import os
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import uuid
from login import set_session_from_params, get_session_from_session_state, get_session_from_cookies, get_login_frame, get_loged_frame
import time
from pages.switch_panel import main_menu
import pages.page_controller as pgs

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL")
APP_NAME = os.getenv("APP_NAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

pg = pgs.Page_controller()
page_board     = pg.page_create("pages/board.py", "Board", "board")
#Company
page_companies = pg.page_create("pages/company/companies.py", "Seznam partnerů", "companies")
page_company   = pg.page_create("pages/company/company.py", "Detail partnera", "company")

#assortment
page_assortments = pg.page_create("pages/assortment/assortments.py", "Seznam sortimentů", "assortments")

page_test      = pg.page_create("pages/page_test.py", "Test", "test")
#Settings
page_settings  = pg.page_create("pages/settings/settings.py", "Nastavení", "settings")

pg.create_page_navigator()

cookies = EncryptedCookieManager(prefix=APP_NAME, password=APP_PASSWORD)
if not cookies.ready():
    st.stop()

database = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.session_state["sb_database"] = database

st.session_state["app_base_url"] = APP_BASE_URL

st.set_page_config(page_title="LEJSEK", page_icon="pictures/lejsek_sedy_head.png")

session = None
st.session_state["cookies"] = cookies
set_session_from_params(st.session_state["sb_database"])
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if session:
    col_picture, col_login = st.columns(2)
    with col_picture:
        with st.container(border=True):
            st.image("pictures/lejsek_sedy_vetev_7.png", use_container_width=True)
    with col_login:
        with st.container(border=True):
            get_loged_frame(session, cookies)
else:
    col_picture, col_login = st.columns(2)
    with col_picture:
        with st.container(border=True):
            st.image("pictures/lejsek_sedy_login.png", use_container_width=True)
            st.markdown("# L.E.J.S.E.K.")
    with col_login:
        with st.container(border=True):
            get_login_frame(cookies, APP_BASE_URL)

if "show_loged_out" in st.session_state and st.session_state["show_loged_out"]:
    st.info("Odhlášeno")
    st.session_state["show_loged_out"] = False
if "show_loged_in" in st.session_state and st.session_state["show_loged_in"]:
    st.info("Přihlášeno")
    st.session_state["show_loged_in"] = False
if "user_info_registrered" in st.session_state and st.session_state["user_info_registrered"]:
    st.success("Emailová adresa byla zaregistrována")
    st.session_state["user_info_registrered"] = False

if session:
    main_menu()

pg.run()

