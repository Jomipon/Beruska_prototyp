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

if st.button("code='123'"):
    st.query_params["code"] = "123"
    st.rerun()
if st.button("code='456'"):
    st.query_params["code"] = "456"
    st.rerun()
if st.button("code='789'"):
    st.query_params["code"] = "789"
    st.rerun()
if st.button("no code"):
    st.query_params.pop("code", None)
    st.rerun()

st.write(f"code = {st.query_params.get('code', 'NO CODE')}")

if st.button("Znovu načíst stránku"):
    st.rerun()

session = None

if "sb_tokens" in st.session_state:
    try:
        at, rt = st.session_state["sb_tokens"]
        supabase.auth.set_session(at, rt)
    except:
        pass
    session = supabase.auth.get_session()

if not session or "sb_tokens" not in st.session_state:
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
                st.session_state["zobrazit_prihlaseno"] = True
            else:
                st.error("Jméno nebo heslo je neplatné")
            st.rerun()
        

if session:
    if "zobrazit_prihlaseno" in st.session_state and st.session_state["zobrazit_prihlaseno"]:
        st.success("Přihlášeno")
        st.session_state.pop("zobrazit_prihlaseno", None)
    if st.button("Odhlásit"):
        try:
            supabase.auth.sign_out()
        finally:
            st.session_state.pop("token", None)
            st.session_state.pop("sb_tokens", None)
        st.rerun()
else:
    st.warning("Nepřihlášený")


if session:
    item_param = st.query_params.get("item")
    # detail předmětu
    if item_param:
        # odkaz zpět
        #st.link_button("Home page", url=APP_BASE_URL)
        if st.button("Home page"):
            st.query_params.clear()
            st.rerun()
        try:
            item_res = supabase.from_("items").select("*").filter("id", "eq", item_param).execute()
        except:
            item_res = None
        if not item_res or not item_res.data:
            st.error("Položka nenalezena.")
            st.query_params.pop("item", None)
            st.rerun()
        else:
            row = item_res.data[0]
            content_key = row['id']
            initial = row.get("content") or ""
            if content_key not in st.session_state:
                st.session_state[content_key] = initial
            with st.form("edit_item"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Content:", key=content_key)
                with col2:
                    st.text_input("id", row["id"], disabled=True)
                    st.text_input("owner id", row["owner_id"], disabled=True)
                with col3:
                    st.text_input("created at", row["created_at"], disabled=True)

                if st.form_submit_button("Uložit"):
                    try:
                        new_content = st.session_state[content_key]
                        supabase.from_("items").update({"content": new_content}).eq("id", row["id"]).execute()
                        st.success("Uloženo.")
                    except Exception as e:
                        st.error(f"Update error: {e}")
    else:
        # základní panel
        st.markdown("**Přidat předmět**")
        content = st.text_input("Name:")
        if st.button("Přidat"):
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
            st.markdown("**Seznam předmětů**")
            df_view = st.data_editor(
                data=df,
                hide_index=True,
                disabled=["id", "owner_id", "content", "created_at", "url"],
                column_config={
                    "_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
                    "url": st.column_config.LinkColumn("", display_text="Detail"),
                },
                column_order=["_selected", "content"],
                use_container_width=True,
                key="items_editor"
            )
            selected = df_view[df_view["_selected"]]

            st.write(f"Označeno {len(selected)} záznamů")
            if st.button("Smazat označené záznamy", disabled=selected.empty):
                for _, r in selected.iterrows():
                    supabase.from_("items").delete().eq("id", r["id"]).execute()
                st.rerun()

            if st.button("Detail", disabled=len(selected) != 1):
                st.query_params["item"] = selected.iloc[0]["id"]
                st.rerun()
            if st.button("Označená data"):
                if selected.empty:
                    st.warning("Nic není označeno")
                else:
                    st.dataframe(selected)
        else:
            st.write("Žádná data")

st.write(f"ID stránky: {str(uuid.uuid4())}")