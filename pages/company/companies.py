"""
Stránka se seznamem společností
"""
import json
import os
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from login import get_session_from_session_state, get_session_from_cookies
from support import download_get_url, call_create_owner_api, get_access_token


def load_companies(refresh_token):
    """
    Stáhne seznam partnerů z API
    """
    try:
        fast_api_url_base = os.getenv("FAST_API_URL_BASE")
        fast_api_url_companies = os.getenv("FAST_API_URL_COMPANIES")

        access_token_new = get_access_token(refresh_token)
        
        body = call_create_owner_api(fast_api_url_base, access_token_new)
        
        url = f"{fast_api_url_base}{fast_api_url_companies}"
        body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
        body = body.decode('UTF-8')
        companies = json.loads(body)
        return companies
    except Exception:
        st.query_params.clear()
        st.stop()


def main():
    """
    Hlavní metoda pro zobrazení seznamu partnerů
    """
    load_dotenv()

    if "sb_database" not in st.session_state:
        st.error("Nepovedlo se připojit k databázi")
        st.stop()

    database = st.session_state.get("sb_database", None)

    session = None
    cookies = st.session_state["cookies"]
    session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
    session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

    if session is None:
        session = database.auth.get_session()
    refresh_token = session.refresh_token

    if database is None:
        st.stop()
    companies = load_companies(refresh_token)
    st.markdown("**Seznam partnerů**")
    if companies:
        df = pd.DataFrame(companies)
        df = df.assign(url=df.company_id)
        df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/company?id={x}")
        df = df[["company_id", "name", "name_first", "name_last", "active", "note", "created_at", "url", "phone_number", "alias", "type_person"]]
        df["name"] = np.where(df["type_person"] == 0, df["name_first"] + " " + df["name_last"], df["name"])
        st.data_editor(
            data=df,
            hide_index=True,
            disabled=["company_id", "name", "name_first", "name_last", "active", "note", "created_at", "url", "phone_number", "alias"],
            column_config={
                "url": st.column_config.LinkColumn("Odkaz", width=30, display_text="Detail"),
                "name": st.column_config.TextColumn("Název partnera", width="medium"),
                "active": st.column_config.CheckboxColumn("Aktivní", width=20),
                "phone_number": st.column_config.TextColumn("Telefon", width="small"),
                "note": st.column_config.TextColumn("Poznámka", width="small"),
                "alias": st.column_config.TextColumn("Alias", width="small"),
            },
            column_order=["name", "url", "note", "alias", "phone_number"],
            width="stretch",
            key="companies_editor"
        )
    else:
        st.write("Seznam je prázdný")
    st.link_button(url="company?new=1", label="Nový partner")

if __name__ == "__main__":
    main()
    