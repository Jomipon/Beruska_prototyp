import json
import os
import streamlit as st
import pandas as pd
import numpy as np
from login import get_session_from_session_state, get_session_from_cookies
from support import download_get_url, call_create_owner_api, get_access_token

def load_items(refresh_token):
    """
    Stáhne seznam partnerů z API
    """
    try:
        fast_api_url_base = os.getenv("FAST_API_URL_BASE")
        fast_api_url_items = os.getenv("FAST_API_URL_ITEMS")

        access_token_new = get_access_token(refresh_token)
        
        body = call_create_owner_api(access_token_new)
        
        url = f"{fast_api_url_base}{fast_api_url_items}"
        body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
        body = body.decode('UTF-8')
        items = json.loads(body)
        return items
    except Exception:
        st.query_params.clear()
        st.stop()

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k databázi")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = None
cookies = st.session_state["cookies"]
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if session is None:
    session = database.auth.get_session()
FAST_API_URL_BASE = os.getenv("FAST_API_URL_BASE")
FAST_API_URL_REFRESH = os.getenv("FAST_API_URL_REFRESH")
FAST_API_URL_COMPANIES = os.getenv("FAST_API_URL_COMPANIES")
acceess_token = session.access_token
refresh_token = session.refresh_token

if database is None:
    st.stop()

st.write("**Seznam sortimentů**")

#items = database.from_("item").select("*").order("name").execute()
items = load_items(refresh_token)
if items:
    df = pd.DataFrame(items)
    df = df.assign(url=df.item_id)
    df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/assortment?id={x}")
    df = df[["item_id", "name", "url", "note", "item_number"]]
    df_view = st.data_editor(
        data=df,
        hide_index=True,
        disabled=["item_id", "name", "url", "note", "item_number"],
        column_config={
            #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
            "url": st.column_config.LinkColumn("Odkaz", width=30, display_text="Detail"), #, display_text="Detail"
            "name": st.column_config.TextColumn("Název", width="medium"),
            "item_number": st.column_config.TextColumn("Číslo", width="medium"),
            "active": st.column_config.CheckboxColumn("Aktivní", width=20),
            "note": st.column_config.TextColumn("Poznámka", width="small"),
        },
        column_order=["name", "item_number", "url", "note"],
        width="stretch",
        key="items_editor"
    )
else:
    st.write("Seznam je prázdný")
st.link_button(url=f"assortment?new=1", label="Nový sortiment")
