#Seznam výdejek
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
    st.stop()

try:
    database.rpc("create_owner_id").execute()
except:
    st.query_params.clear() 
    st.stop()

st.write("**Seznam výdejek**")
issues = database.from_("issue_head").select("*").order("issue_number").execute()
if issues.data:
    df = pd.DataFrame(issues.data)
    df = df.assign(url=df.issue_id)
    df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/issue?id={x}")
    df = df[["issue_id", "issue_number", "date_of_issue", "company_id", "note", "place", "issue_price", "url"]]
    df_view = st.data_editor(
        data=df,
        hide_index=True,
        disabled=["issue_id", "issue_number", "date_of_issue", "company_id", "note", "place", "issue_price"],
        column_config={
            #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
            "issue_number": st.column_config.TextColumn("Číslo", width="small"),
            "company_id": st.column_config.TextColumn("Společnost", width="medium"),
            "url": st.column_config.LinkColumn("Odkaz", width=30, display_text="Detail"), #, display_text="Detail"
            "date_of_issue": st.column_config.TextColumn("Datum vydání", width="small"),
            "issue_price": st.column_config.TextColumn("Celková cena", width="small"),
            "place": st.column_config.TextColumn("Místo", width="small"),
            "note": st.column_config.TextColumn("Poznámka", width="small"),
        },
        column_order=["issue_number", "company_id", "url", "date_of_issue", "issue_price", "place", "note"],
        width="stretch",
        key="issues_editor"
    )
else:
    st.write("Seznam je prázdný")
st.link_button(url=f"issue?new=1", label="Nová výdejka")
