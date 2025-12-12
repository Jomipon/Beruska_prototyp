#Seznam výdejek
import json
import os
import streamlit as st
import pandas as pd
import numpy as np
from login import get_session_from_session_state, get_session_from_cookies
from support import download_get_url, call_create_owner_api, get_access_token

def main():
    if "sb_database" not in st.session_state:
        st.error("Nepovedlo se připojit k databázi")
        #st.switch_page("pages/board.py")
        st.stop()

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
    if not session:
        return
    refresh_token = session.refresh_token

    if database is None:
        st.stop()

    st.write("**Seznam výdejek**")

    try:
        fast_api_url_base = os.getenv("FAST_API_URL_BASE")
        fast_api_url_issues = os.getenv("FAST_API_URL_ISSUES")

        access_token_new = get_access_token(refresh_token)
        body = call_create_owner_api(access_token_new)
        url = f"{fast_api_url_base}{fast_api_url_issues}"
        body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
        issues = json.loads(body)
    except Exception as e:
        #st.query_params.clear()
        st.write(f"{e=}")
        st.stop()

    if issues["row_count"] > 0:
        df = pd.DataFrame(issues["data"])
        df.sort_values("created_at", ascending=False, inplace=True)
        df = df.assign(url=df.issue_id)
        df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/issue?id={x}")
        df = df[["issue_id", "issue_number", "date_of_issue", "company_id", "note", "place", "issue_price", "url", "company_fullname"]]
        df_view = st.data_editor(
            data=df,
            hide_index=True,
            disabled=["issue_id", "issue_number", "date_of_issue", "company_id", "note", "place", "issue_price", "company_fullname"],
            column_config={
                #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
                "issue_number": st.column_config.TextColumn("Číslo", width="small"),
                "company_id": st.column_config.TextColumn("Společnost", width="medium"),
                "company_fullname": st.column_config.TextColumn("Společnost", width="medium"),
                "url": st.column_config.LinkColumn("Odkaz", width=30, display_text="Detail"), #, display_text="Detail"
                "date_of_issue": st.column_config.TextColumn("Datum vydání", width="small"),
                "issue_price": st.column_config.TextColumn("Celková cena", width="small"),
                "place": st.column_config.TextColumn("Místo", width="small"),
                "note": st.column_config.TextColumn("Poznámka", width="small"),
            },
            column_order=["issue_number", "company_fullname", "url", "date_of_issue", "issue_price", "place", "note"],
            width="stretch",
            key="issues_editor"
        )
    else:
        st.write("Seznam je prázdný")
    st.link_button(url=f"issue?new=1", label="Nová výdejka")

if __name__ == "__main__":
    main()