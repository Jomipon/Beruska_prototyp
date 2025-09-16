import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import uuid

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase = get_client()

st.set_page_config(page_title="Streamlit + Supabase + AUTH", page_icon="🔐")
st.title("🔐 Streamlit + Supabase + AUTH")

if st.button("Refresh"):
    st.rerun()

session = None

if "sb_tokens" in st.session_state:
    at, rt = st.session_state["sb_tokens"]
    supabase.auth.set_session(at, rt)

    session = supabase.auth.get_session()

if "sb_tokens" not in st.session_state:
    with st.form("login"):
        input_username = st.text_input("Username:")
        input_password = st.text_input("Password:", type="password")
        if st.form_submit_button("Přihlásit"):
            try:
                user = supabase.auth.sign_in_with_password({"email": input_username, "password": input_password})
            except Exception as e:
                user = None
            if user:
                session = supabase.auth.get_session()
                st.session_state["sb_tokens"] = (
                    session.access_token,
                    session.refresh_token,
                )
            else:
                st.error("Jméno nebo heslo je neplatné")
            st.rerun()
        

if session:
    st.success("Přihlášeno")
    if st.button("Odhlásit"):
        try:
            supabase.auth.sign_out()
        finally:
            st.session_state.pop("token", None)
            st.session_state.pop("sb_tokens", None)
        st.rerun()
else:
    st.warning("Nepřihlášený")


st.write(f"{str(uuid.uuid4())}")

if session:
    st.write("Test")
    with st.form("Add_item"):
        content = st.text_input("Name:")
        if st.form_submit_button("Přidat"):
            try:
                ins = supabase.from_("items").insert({"content": content.strip()}).execute()
                st.success(f"Přidáno: {ins.data[0]['content']}")
                #st.rerun()
            except Exception as e:
                st.error(f"Nepovedlo se uložit do databáze\n: {e}")
    items = supabase.from_("items").select("*").order("created_at").execute()
    if items.data:
        df = pd.DataFrame(items.data)
        df = df.assign(_selected=False)
        df = df.assign(url=df.id)
        df["url"] = df["url"].apply(lambda x: f"{APP_BASE_URL}?item={x}")
        # zobrazme jen potřebné sloupce (tvoje verze Streamlitu 1.33 nemá visible=False)
        df = df[["_selected", "content", "url", "id", "owner_id", "created_at"]]
        df_view = st.data_editor(
            data=df,
            hide_index=True,
            disabled=["id", "owner_id", "content", "created_at"],
            column_config={
                "_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
                "url": st.column_config.LinkColumn("", display_text="Detail"),
            },
            column_order=["_selected", "content", "url"],
            use_container_width=True,
            key="items_editor"
        )
        selected = df_view[df_view["_selected"]]

        if st.button("Smazat označené záznamy", disabled=selected.empty):
            for _, r in selected.iterrows():
                supabase.from_("items").delete().eq("id", r["id"]).execute()
            st.rerun()

        if st.button("Označená data"):
            if selected.empty:
                st.warning("Nic není označeno")
            else:
                st.dataframe(selected)
    else:
        st.write("Žádná data")

