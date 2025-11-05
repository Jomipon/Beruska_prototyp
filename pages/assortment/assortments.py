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

st.write("**Seznam sortimentů**")
items = database.from_("item").select("*").order("name").execute()
if items.data:
    df = pd.DataFrame(items.data)
    df = df.assign(url=df.item_id)
    df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/assortment?id={x}")
    df = df[["item_id", "name", "url", "note"]]
    df_view = st.data_editor(
        data=df,
        hide_index=True,
        disabled=["item_id", "name", "note"],
        column_config={
            #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
            "url": st.column_config.LinkColumn("Odkaz", width=30, display_text="Detail"), #, display_text="Detail"
            "name": st.column_config.TextColumn("Název partnera", width="medium"),
            "active": st.column_config.CheckboxColumn("Aktivní", width=20),
            "note": st.column_config.TextColumn("Poznámka", width="small"),
        },
        column_order=["name", "url", "note"],
        use_container_width=True,
        key="items_editor"
    )
else:
    st.write("Seznam je prázdný")
st.link_button(url=f"assortment?new=1", label="Nový sortiment")
